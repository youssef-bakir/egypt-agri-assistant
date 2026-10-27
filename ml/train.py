"""
ml/train.py — disease model training script using timm backbones.

Features:
- Backbone from timm (default: mobilenetv3_large_100, efficientnet_b0).
- Domain-balanced + class-balanced sampling (so 54k lab images do not drown field images).
- Two-phase training:
    Phase A: train new classification head only (backbone frozen).
    Phase B: unfreeze backbone with lower LR + cosine annealing.
- Label smoothing: 0.1, AdamW optimizer, mixed precision (torch.amp).
- Early stopping on validation macro-F1.
- Output artifacts saved:
    - best_model.pt (PyTorch weights)
    - labels.json (index-to-class list, including 'unknown')
    - model_meta.json (git commit, manifest hash, config, metrics, timestamp)
- Supports --smoke mode for a fast 1-epoch subset run (Kaggle quota protection).
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from PIL import Image

import config
from ml.preprocess import get_eval_transform, get_train_transform, load_and_fix_image


def compute_manifest_sha256(manifest_path: Path) -> str:
    """Compute SHA-256 hash of the manifest file for reproducibility tracking."""
    if not manifest_path.exists():
        return "none"
    h = hashlib.sha256()
    with open(manifest_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_git_commit() -> str:
    """Get current git commit hash."""
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return "unknown"


def build_manifest_dataset_class():
    """Lazily build ManifestDataset using torch.utils.data.Dataset."""
    import torch
    from torch.utils.data import Dataset

    class ManifestDataset(Dataset):
        def __init__(self, records: list[dict], label_to_idx: dict[str, int], transform):
            self.records = records
            self.label_to_idx = label_to_idx
            self.transform = transform
            self.unknown_idx = label_to_idx.get("unknown", 0)

        def __len__(self) -> int:
            return len(self.records)

        def __getitem__(self, idx: int):
            rec = self.records[idx]
            p = rec["path"]
            raw_lbl = rec["label"]
            lbl_idx = self.label_to_idx.get(raw_lbl, self.unknown_idx)

            try:
                img = load_and_fix_image(p)
                tensor = self.transform(img)
            except Exception:
                img = load_and_fix_image(np.zeros((config.IMAGE_SIZE, config.IMAGE_SIZE, 3), dtype=np.uint8).tobytes())
                tensor = self.transform(img)

            return tensor, lbl_idx

    return ManifestDataset


def build_balanced_sampler(records: list[dict], label_to_idx: dict[str, int]):
    """Build WeightedRandomSampler to achieve class-balance and domain-balance."""
    import torch
    from torch.utils.data import WeightedRandomSampler

    class_counts = Counter(r["label"] for r in records)
    domain_counts = Counter(r["domain"] for r in records)

    weights = []
    for r in records:
        lbl = r["label"]
        dm = r["domain"]
        w_class = 1.0 / max(1, class_counts[lbl])
        w_domain = 1.0 / max(1, domain_counts[dm])
        weights.append(w_class * w_domain)

    weights_tensor = torch.as_tensor(weights, dtype=torch.double)
    return WeightedRandomSampler(weights=weights_tensor, num_samples=len(weights), replacement=True)


def evaluate_model(model, loader, device) -> tuple[float, float]:
    """Compute validation loss and macro-F1."""
    import torch
    import torch.nn as nn
    from sklearn.metrics import f1_score

    model.eval()
    criterion = nn.CrossEntropyLoss()
    total_loss = 0.0
    all_preds: list[int] = []
    all_targets: list[int] = []

    with torch.no_grad():
        for imgs, targets in loader:
            imgs, targets = imgs.to(device, non_blocking=True), targets.to(device, non_blocking=True)
            outputs = model(imgs)
            loss = criterion(outputs, targets)
            total_loss += loss.item() * len(targets)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_targets.extend(targets.cpu().numpy())

    avg_loss = total_loss / max(1, len(all_targets))
    macro_f1 = float(f1_score(all_targets, all_preds, average="macro", zero_division=0))
    return avg_loss, macro_f1


def train(
    manifest_path: str = "data/manifest_clean.csv",
    model_name: str = "mobilenetv3_large_100",
    image_size: int = config.IMAGE_SIZE,
    epochs_head: int = 5,
    epochs_full: int = 15,
    batch_size: int = 64,
    lr_head: float = 1e-3,
    lr_full: float = 1e-4,
    output_dir: str = "models",
    smoke: bool = False,
    seed: int = 42,
) -> dict:
    """Run full disease model training."""
    try:
        import timm
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader
    except ImportError as e:
        print(f"ERROR: Training dependencies (torch, torchvision, timm) not installed: {e}", flush=True)
        print("Please install requirements-train.txt or run on a GPU kernel.", flush=True)
        sys.exit(1)

    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})", flush=True)

    manifest_p = Path(manifest_path)
    if not manifest_p.exists():
        manifest_p = Path("data/manifest.csv")
    if not manifest_p.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path} or data/manifest.csv")

    with open(manifest_p, encoding="utf-8") as f:
        all_records = list(csv.DictReader(f))

    supported = sorted(set(config.SUPPORTED_CLASSES))
    classes = supported + (["unknown"] if "unknown" not in supported else [])
    label_to_idx = {c: i for i, c in enumerate(classes)}
    num_classes = len(classes)

    train_recs = [r for r in all_records if r["split"] == "train"]
    val_recs = [r for r in all_records if r["split"] == "val"]

    if smoke:
        print("[SMOKE RUN]: Subsetting to 500 train, 100 val images, 1 epoch head.", flush=True)
        train_recs = train_recs[:500]
        val_recs = val_recs[:100]
        epochs_head = 1
        epochs_full = 0

    print(f"Classes: {num_classes} | Train samples: {len(train_recs):,} | Val samples: {len(val_recs):,}", flush=True)

    train_tfm = get_train_transform(image_size)
    eval_tfm = get_eval_transform(image_size)

    ManifestDataset = build_manifest_dataset_class()
    train_ds = ManifestDataset(train_recs, label_to_idx, train_tfm)
    val_ds = ManifestDataset(val_recs, label_to_idx, eval_tfm)

    sampler = build_balanced_sampler(train_recs, label_to_idx)
    num_workers = min(4, os.cpu_count() or 1)

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        sampler=sampler,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )

    print(f"Creating model backbone: {model_name} (pretrained=True)...", flush=True)
    model = timm.create_model(model_name, pretrained=True, num_classes=num_classes)
    model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    scaler = torch.amp.GradScaler("cuda", enabled=torch.cuda.is_available())

    best_val_f1 = -1.0
    best_weights = None
    best_epoch = 0

    out_p = Path(output_dir)
    out_p.mkdir(parents=True, exist_ok=True)

    # ── Phase A: Head only ──────────────────────────────────────────────────
    print(f"\n=== Phase A: Training classification head only ({epochs_head} epochs, lr={lr_head}) ===", flush=True)
    for name, param in model.named_parameters():
        if "classifier" not in name and "head" not in name and "fc" not in name:
            param.requires_grad = False

    head_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(head_params, lr=lr_head, weight_decay=1e-2)

    for epoch in range(1, epochs_head + 1):
        model.train()
        train_loss = 0.0
        for imgs, targets in train_loader:
            imgs, targets = imgs.to(device, non_blocking=True), targets.to(device, non_blocking=True)
            optimizer.zero_grad()
            with torch.amp.autocast("cuda", enabled=torch.cuda.is_available()):
                outputs = model(imgs)
                loss = criterion(outputs, targets)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            train_loss += loss.item() * len(targets)

        train_loss /= max(1, len(train_recs))
        val_loss, val_f1 = evaluate_model(model, val_loader, device)
        print(f"Epoch {epoch:02d}/{epochs_head:02d} (Head) | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Macro-F1: {val_f1:.4f}", flush=True)

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_epoch = epoch
            best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    # ── Phase B: Full fine-tuning ───────────────────────────────────────────
    if epochs_full > 0:
        print(f"\n=== Phase B: Fine-tuning full backbone ({epochs_full} epochs, lr={lr_full}) ===", flush=True)
        for param in model.parameters():
            param.requires_grad = True

        optimizer = torch.optim.AdamW(model.parameters(), lr=lr_full, weight_decay=1e-2)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs_full, eta_min=1e-6)
        patience = 5
        epochs_no_improve = 0

        for epoch in range(1, epochs_full + 1):
            model.train()
            train_loss = 0.0
            for imgs, targets in train_loader:
                imgs, targets = imgs.to(device, non_blocking=True), targets.to(device, non_blocking=True)
                optimizer.zero_grad()
                with torch.amp.autocast("cuda", enabled=torch.cuda.is_available()):
                    outputs = model(imgs)
                    loss = criterion(outputs, targets)
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
                train_loss += loss.item() * len(targets)

            scheduler.step()
            train_loss /= max(1, len(train_recs))
            val_loss, val_f1 = evaluate_model(model, val_loader, device)
            print(f"Epoch {epoch:02d}/{epochs_full:02d} (Full) | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Macro-F1: {val_f1:.4f}", flush=True)

            if val_f1 > best_val_f1:
                best_val_f1 = val_f1
                best_epoch = epochs_head + epoch
                best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= patience:
                    print(f"Early stopping triggered at epoch {epoch} (best Val Macro-F1: {best_val_f1:.4f})", flush=True)
                    break

    # Save best model
    if best_weights is not None:
        model_path = out_p / "best_model.pt"
        torch.save(best_weights, model_path)
        print(f"\nBest model saved to: {model_path} (Best Val Macro-F1: {best_val_f1:.4f} at epoch {best_epoch})", flush=True)

    # Save labels.json
    labels_path = out_p / "labels.json"
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump(classes, f, indent=2, ensure_ascii=False)
    print(f"Labels saved to: {labels_path} ({num_classes} classes)", flush=True)

    # Save model_meta.json
    manifest_sha = compute_manifest_sha256(manifest_p)
    git_hash = get_git_commit()
    meta = {
        "model_name": model_name,
        "image_size": image_size,
        "num_classes": num_classes,
        "classes": classes,
        "git_commit": git_hash,
        "manifest_sha256": manifest_sha,
        "manifest_path": str(manifest_p),
        "best_val_macro_f1": round(best_val_f1, 4),
        "best_epoch": best_epoch,
        "epochs_head": epochs_head,
        "epochs_full": epochs_full,
        "batch_size": batch_size,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "smoke": smoke,
    }
    meta_path = out_p / "model_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"Metadata saved to: {meta_path}", flush=True)

    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description="Train disease model with timm backbone.")
    parser.add_argument("--manifest", default="data/manifest_clean.csv", help="Path to manifest")
    parser.add_argument("--model-name", default="mobilenetv3_large_100", help="timm backbone model name")
    parser.add_argument("--image-size", type=int, default=config.IMAGE_SIZE, help="Input image resolution")
    parser.add_argument("--epochs-head", type=int, default=5, help="Epochs for Phase A (head only)")
    parser.add_argument("--epochs-full", type=int, default=15, help="Epochs for Phase B (full fine-tuning)")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--lr-head", type=float, default=1e-3, help="Learning rate for Phase A")
    parser.add_argument("--lr-full", type=float, default=1e-4, help="Learning rate for Phase B")
    parser.add_argument("--output-dir", default="models", help="Directory to save weights & metadata")
    parser.add_argument("--smoke", action="store_true", help="Quick 1-epoch subset run to test pipeline")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    train(
        manifest_path=args.manifest,
        model_name=args.model_name,
        image_size=args.image_size,
        epochs_head=args.epochs_head,
        epochs_full=args.epochs_full,
        batch_size=args.batch_size,
        lr_head=args.lr_head,
        lr_full=args.lr_full,
        output_dir=args.output_dir,
        smoke=args.smoke,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
