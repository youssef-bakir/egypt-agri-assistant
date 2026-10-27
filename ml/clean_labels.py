"""
ml/clean_labels.py — automatic label-noise cleaning using out-of-fold predictions.

Algorithm:
1. Extract fast representations and train with Stratified K-fold cross-validation.
2. For each training image, obtain its out-of-fold predicted probability.
3. Flag images where the model is confident (> NOISE_THRESHOLD) but predicts a DIFFERENT label.
4. Remove flagged images up to a cap (MAX_REMOVAL_FRACTION per class).
5. Log counts in reports/cleaning.md.
6. Save contact sheets in reports/contact_sheets/ (sample of up to 10 images per class).
7. Write data/manifest_clean.csv.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from PIL import Image

NOISE_THRESHOLD = 0.90
MAX_REMOVAL_FRACTION = 0.20
KFOLDS = 3


def extract_features(path_str: str) -> np.ndarray:
    """Extract lightweight color histogram + spatial thumbnail representation."""
    try:
        with Image.open(path_str) as img:
            img = img.convert("RGB").resize((16, 16), Image.Resampling.BILINEAR)
            arr = np.array(img, dtype=np.float32) / 255.0
            return arr.flatten()
    except Exception:
        return np.zeros(16 * 16 * 3, dtype=np.float32)


def make_contact_sheet(image_paths: list[str], output_path: Path, thumb_size: int = 64) -> None:
    """Create a horizontal contact sheet of sample images."""
    if not image_paths:
        return
    imgs = []
    for p in image_paths[:10]:
        try:
            with Image.open(p) as img:
                imgs.append(img.convert("RGB").resize((thumb_size, thumb_size)))
        except Exception:
            pass
    if not imgs:
        return
    w = thumb_size * len(imgs)
    sheet = Image.new("RGB", (w, thumb_size), color=(30, 30, 30))
    for i, im in enumerate(imgs):
        sheet.paste(im, (i * thumb_size, 0))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)


def run_noise_cleaning(manifest_path: Path, output_path: Path) -> None:
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold

    records: list[dict] = []
    with open(manifest_path, encoding="utf-8") as f:
        records = list(csv.DictReader(f))

    train_records = [r for r in records if r["split"] == "train" and r["label"] != "unknown"]
    labels = sorted(set(r["label"] for r in train_records))
    label_to_idx = {lbl: i for i, lbl in enumerate(labels)}
    idx_to_label = {i: lbl for lbl, i in label_to_idx.items()}
    num_classes = len(labels)

    print(f"Classes: {num_classes}, Training images to clean: {len(train_records):,}", flush=True)

    # Sample a representative subset for OOF cleaning if dataset is very large
    # to keep runtime within seconds
    y = np.array([label_to_idx[r["label"]] for r in train_records])
    class_counts = defaultdict(int)
    for lbl_idx in y:
        class_counts[lbl_idx] += 1

    # Keep at least min 2 samples per class for StratifiedKFold
    valid_mask = np.array([class_counts[lbl_idx] >= KFOLDS for lbl_idx in y])
    valid_indices = np.where(valid_mask)[0]

    oof_probs = np.zeros((len(train_records), num_classes), dtype=np.float32)

    # Quick feature extraction on training records
    print("Extracting feature representations for OOF noise estimation...", flush=True)
    from concurrent.futures import ThreadPoolExecutor
    paths = [train_records[i]["path"] for i in valid_indices]
    with ThreadPoolExecutor(max_workers=16) as pool:
        feats_list = list(pool.map(extract_features, paths, chunksize=256))
    X_sub = np.array(feats_list, dtype=np.float32)
    y_sub = y[valid_indices]

    print("Running Stratified K-Fold cross-validation...", flush=True)
    skf = StratifiedKFold(n_splits=KFOLDS, shuffle=True, random_state=42)

    for fold, (train_idx, val_idx) in enumerate(skf.split(X_sub, y_sub)):
        clf = LogisticRegression(max_iter=100, solver="lbfgs", C=1.0)
        clf.fit(X_sub[train_idx], y_sub[train_idx])
        probs = clf.predict_proba(X_sub[val_idx])

        # Map back to full num_classes
        clf_classes = clf.classes_
        for local_i, global_val_i in enumerate(val_idx):
            orig_record_idx = valid_indices[global_val_i]
            for col_idx, cls_idx in enumerate(clf_classes):
                oof_probs[orig_record_idx, cls_idx] = probs[local_i, col_idx]

    # Flag noisy images
    flagged_paths: set[str] = set()
    class_flagged: dict[str, int] = defaultdict(int)
    class_total: dict[str, int] = defaultdict(int)
    class_images: dict[str, list[str]] = defaultdict(list)

    for i, r in enumerate(train_records):
        lbl = r["label"]
        class_total[lbl] += 1
        class_images[lbl].append(r["path"])
        pred_idx = int(np.argmax(oof_probs[i]))
        pred_label = idx_to_label.get(pred_idx, "unknown")
        confidence = float(oof_probs[i, pred_idx])
        if pred_label != lbl and confidence > NOISE_THRESHOLD:
            class_flagged[lbl] += 1
            flagged_paths.add(r["path"])

    # Apply removal cap per class (never remove > MAX_REMOVAL_FRACTION)
    removed_paths: set[str] = set()
    class_removed: dict[str, int] = defaultdict(int)

    for r in train_records:
        lbl = r["label"]
        if r["path"] in flagged_paths:
            cap = int(class_total[lbl] * MAX_REMOVAL_FRACTION)
            if class_removed[lbl] < cap:
                removed_paths.add(r["path"])
                class_removed[lbl] += 1

    print(f"Flagged noisy images: {len(flagged_paths):,}, Removed after cap: {len(removed_paths):,}", flush=True)

    # Write cleaned manifest
    with open(manifest_path, encoding="utf-8") as fin, \
         open(output_path, "w", newline="", encoding="utf-8") as fout:
        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=reader.fieldnames)
        writer.writeheader()
        kept = 0
        for row in reader:
            if row["path"] in removed_paths:
                continue
            writer.writerow(row)
            kept += 1

    print(f"Cleaned manifest written to: {output_path} ({kept:,} rows)", flush=True)

    # Contact sheets (1 per class)
    contact_dir = Path("reports/contact_sheets")
    contact_dir.mkdir(parents=True, exist_ok=True)
    for lbl, img_list in class_images.items():
        make_contact_sheet(img_list, contact_dir / f"{lbl}.png")

    # Write cleaning report
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    report_lines = [
        "# Label Noise Cleaning Report",
        "",
        "Generated automatically by `ml/clean_labels.py` using out-of-fold cross-validation.",
        "",
        "## Summary",
        "",
        f"- Total training images examined: {len(train_records):,}",
        f"- Noise threshold: {NOISE_THRESHOLD}",
        f"- Max removal cap per class: {MAX_REMOVAL_FRACTION*100:.0f}%",
        f"- Total flagged as noisy: {len(flagged_paths):,}",
        f"- Total removed after cap: {len(removed_paths):,}",
        f"- Contact sheets generated in: `reports/contact_sheets/`",
        "",
        "## Per-class Cleaning Breakdown",
        "",
        "| Class | Total | Flagged | Removed | Removal Rate |",
        "|-------|-------|---------|---------|--------------|",
    ]
    for lbl in sorted(class_total.keys()):
        tot = class_total[lbl]
        flg = class_flagged.get(lbl, 0)
        rem = class_removed.get(lbl, 0)
        rate = (rem / tot * 100) if tot > 0 else 0.0
        report_lines.append(f"| `{lbl}` | {tot:,} | {flg:,} | {rem:,} | {rate:.1f}% |")

    report_path = reports_dir / "cleaning.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Cleaning report written to: {report_path}", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Label-noise cleaning via OOF predictions.")
    parser.add_argument("--manifest", default="data/manifest.csv")
    parser.add_argument("--output", default="data/manifest_clean.csv")
    args = parser.parse_args()

    manifest = Path(args.manifest)
    if not manifest.exists():
        print(f"ERROR: manifest not found: {manifest}. Run ml/dedup_split.py first.", flush=True)
        sys.exit(1)

    run_noise_cleaning(manifest, Path(args.output))


if __name__ == "__main__":
    main()
