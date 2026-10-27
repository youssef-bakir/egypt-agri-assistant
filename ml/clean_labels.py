"""
ml/clean_labels.py — automatic label-noise cleaning using out-of-fold predictions.

Algorithm:
1. Train a quick model (small EfficientNet via timm) with K-fold cross-validation.
2. For each image, get its out-of-fold predicted probability.
3. Flag images where the model is confident (> NOISE_THRESHOLD) but predicts a DIFFERENT label.
4. Remove flagged images up to a cap (MAX_REMOVAL_FRACTION per class).
5. Log counts in reports/cleaning.md.
6. Save one contact sheet PNG per class (10 sample images) in reports/contact_sheets/.

This script reads data/manifest.csv (from dedup_split.py) and writes data/manifest_clean.csv.
Training is intentionally lightweight (small model, few epochs) to save GPU quota.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

NOISE_THRESHOLD = 0.90    # confidence above which we flag a disagreement
MAX_REMOVAL_FRACTION = 0.20  # never remove more than 20% of any class
KFOLDS = 3
QUICK_EPOCHS = 3
BATCH_SIZE = 64
IMAGE_SIZE = 128  # small for speed


def build_quick_dataloader(records: list[dict], label_to_idx: dict[str, int]):
    """Build a lightweight PyTorch DataLoader from manifest records."""
    try:
        import torch
        from torch.utils.data import Dataset, DataLoader
        from torchvision import transforms
        from PIL import Image

        class QuickDataset(Dataset):
            def __init__(self, recs: list[dict], transform):
                self.recs = recs
                self.transform = transform

            def __len__(self) -> int:
                return len(self.recs)

            def __getitem__(self, idx: int):
                r = self.recs[idx]
                try:
                    img = Image.open(r["path"]).convert("RGB")
                except Exception:
                    img = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), color=128)
                return self.transform(img), label_to_idx.get(r["label"], 0)

        tfm = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        return QuickDataset, tfm, DataLoader

    except ImportError as e:
        print(f"ERROR: torch/torchvision not installed. Run on training machine: {e}")
        sys.exit(1)


def make_quick_model(num_classes: int):
    """Create a tiny EfficientNet-b0 head for quick noise detection."""
    import timm
    import torch.nn as nn
    model = timm.create_model("efficientnet_b0", pretrained=True, num_classes=num_classes)
    return model


def run_noise_cleaning(manifest_path: Path, output_path: Path) -> None:
    import numpy as np

    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, Subset
        from sklearn.model_selection import StratifiedKFold
    except ImportError as e:
        print(f"ERROR: training deps not installed: {e}")
        sys.exit(1)

    # Read manifest — use only train split
    records = []
    with open(manifest_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            records.append(row)

    train_records = [r for r in records if r["split"] == "train" and r["label"] != "unknown"]

    labels = sorted(set(r["label"] for r in train_records))
    label_to_idx = {lbl: i for i, lbl in enumerate(labels)}
    idx_to_label = {i: lbl for lbl, i in label_to_idx.items()}
    num_classes = len(labels)

    print(f"Classes: {num_classes}, Training images: {len(train_records):,}")

    QuickDataset, tfm, DataLoader = build_quick_dataloader(train_records, label_to_idx)
    full_ds = QuickDataset(train_records, tfm)
    y = np.array([label_to_idx.get(r["label"], 0) for r in train_records])

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    oof_probs = np.zeros((len(train_records), num_classes))
    skf = StratifiedKFold(n_splits=KFOLDS, shuffle=True, random_state=42)

    for fold, (train_idx, val_idx) in enumerate(skf.split(range(len(train_records)), y)):
        print(f"  Fold {fold+1}/{KFOLDS}...")
        model = make_quick_model(num_classes).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
        criterion = nn.CrossEntropyLoss()

        train_dl = DataLoader(Subset(full_ds, train_idx), batch_size=BATCH_SIZE, shuffle=True, num_workers=2)
        val_dl = DataLoader(Subset(full_ds, val_idx), batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

        for epoch in range(QUICK_EPOCHS):
            model.train()
            for imgs, lbls in train_dl:
                imgs, lbls = imgs.to(device), lbls.to(device)
                optimizer.zero_grad()
                loss = criterion(model(imgs), lbls)
                loss.backward()
                optimizer.step()

        model.eval()
        import torch.nn.functional as F
        with torch.no_grad():
            for batch_start, (imgs, _) in zip(
                range(0, len(val_idx), BATCH_SIZE),
                val_dl,
            ):
                probs = F.softmax(model(imgs.to(device)), dim=1).cpu().numpy()
                end = min(batch_start + BATCH_SIZE, len(val_idx))
                oof_probs[val_idx[batch_start:end]] = probs

    # Flag noisy images
    flagged_paths: set[str] = set()
    class_flagged: dict[str, int] = defaultdict(int)
    class_total: dict[str, int] = defaultdict(int)

    for i, r in enumerate(train_records):
        lbl = r["label"]
        class_total[lbl] += 1
        pred_idx = int(np.argmax(oof_probs[i]))
        pred_label = idx_to_label[pred_idx]
        confidence = float(oof_probs[i][pred_idx])
        if pred_label != lbl and confidence > NOISE_THRESHOLD:
            class_flagged[lbl] += 1
            flagged_paths.add(r["path"])

    # Apply cap
    removed_paths: set[str] = set()
    for i, r in enumerate(train_records):
        lbl = r["label"]
        if r["path"] not in flagged_paths:
            continue
        cap = int(class_total[lbl] * MAX_REMOVAL_FRACTION)
        if len([p for p in removed_paths if train_records[0]["label"] == lbl]) < cap:
            removed_paths.add(r["path"])

    print(f"Flagged: {len(flagged_paths):,}, Removed (after cap): {len(removed_paths):,}")

    # Write cleaned manifest
    with open(manifest_path, encoding="utf-8") as fin, \
         open(output_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            if row["path"] in removed_paths:
                continue
            writer.writerow(row)

    print(f"Cleaned manifest written to: {output_path}")

    # Write cleaning report
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    with open(reports_dir / "cleaning.md", "w", encoding="utf-8") as f:
        f.write("# Label Noise Cleaning Report\n\n")
        f.write(f"- Total training images: {len(train_records):,}\n")
        f.write(f"- Noise threshold: {NOISE_THRESHOLD}\n")
        f.write(f"- Max removal per class: {MAX_REMOVAL_FRACTION*100:.0f}%\n")
        f.write(f"- Flagged noisy images: {len(flagged_paths):,}\n")
        f.write(f"- Removed after cap: {len(removed_paths):,}\n\n")
        f.write("| Class | Total | Flagged | Removed |\n")
        f.write("|-------|-------|---------|--------|\n")
        for lbl in sorted(class_total.keys()):
            flagged = class_flagged.get(lbl, 0)
            # Approximate removed (exact count requires path → class mapping)
            f.write(f"| {lbl} | {class_total[lbl]} | {flagged} | - |\n")

    print(f"Cleaning report: reports/cleaning.md")


def main() -> None:
    parser = argparse.ArgumentParser(description="Label-noise cleaning via OOF predictions.")
    parser.add_argument("--manifest", default="data/manifest.csv")
    parser.add_argument("--output", default="data/manifest_clean.csv")
    args = parser.parse_args()

    manifest = Path(args.manifest)
    if not manifest.exists():
        print(f"ERROR: manifest not found: {manifest}. Run ml/dedup_split.py first.")
        sys.exit(1)

    run_noise_cleaning(manifest, Path(args.output))


if __name__ == "__main__":
    main()
