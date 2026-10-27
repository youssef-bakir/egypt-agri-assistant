"""
ml/inventory.py — scan downloaded datasets and produce reports/inventory.md.

Usage:
    python ml/inventory.py --data-dir data/raw

Output: reports/inventory.md with:
  - counts per class / source / domain
  - corrupt files
  - size statistics
  - imbalance analysis
  - augmented-copy detection
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.label_map import normalize, canonical_crop

REPORTS_DIR = Path(__file__).parent.parent / "reports"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
AUG_PATTERNS = re.compile(r"aug|rotated|flipped|flip|rotate|augment|grayscale|segmented", re.IGNORECASE)


def is_augmented_path(path: Path) -> bool:
    """Return True if the file or any parent folder looks like an augmented/synthetic copy."""
    for part in path.parts:
        if AUG_PATTERNS.search(part):
            return True
    return False


def get_domain(source_name: str, path: Path) -> str:
    """Determine domain: lab, field, or negatives."""
    src = source_name.lower()
    if src in ("negatives", "negatives_soil"):
        return "negatives"
    if src == "plantvillage":
        return "lab"
    return "field"


def is_corrupt(path: Path) -> bool:
    """Check if the image file can be opened and verified by Pillow."""
    try:
        from PIL import Image
        with Image.open(path) as img:
            img.verify()
        return False
    except Exception:
        return True


def scan_dataset(dataset_dir: Path, source_name: str) -> list[dict]:
    """Walk a dataset directory and collect per-image metadata."""
    records: list[dict] = []
    
    for root, _dirs, files in os.walk(dataset_dir):
        root_path = Path(root)
        for fname in files:
            fpath = root_path / fname
            if fpath.suffix.lower() not in IMAGE_EXTS:
                continue

            raw_label = fpath.parent.name
            augmented = is_augmented_path(fpath)
            domain = get_domain(source_name, fpath)
            canonical = normalize(raw_label, source=source_name)

            try:
                size_bytes = fpath.stat().st_size
            except OSError:
                size_bytes = 0

            records.append({
                "path": str(fpath),
                "raw_label": raw_label,
                "canonical": canonical,
                "source": source_name,
                "domain": domain,
                "augmented": augmented,
                "size_bytes": size_bytes,
                "corrupt": False,
            })
    return records


def build_report(records: list[dict]) -> str:
    """Build a markdown report string from the inventory records."""
    total = len(records)
    augmented = sum(1 for r in records if r["augmented"])
    corrupt = sum(1 for r in records if r["corrupt"])

    # Active original records (non-augmented)
    active_records = [r for r in records if not r["augmented"]]
    active_total = len(active_records)

    # Counts per canonical label (active)
    label_counts: dict[str, int] = defaultdict(int)
    for r in active_records:
        label_counts[r["canonical"]] += 1

    # Counts per source (active)
    source_counts: dict[str, int] = defaultdict(int)
    for r in active_records:
        source_counts[r["source"]] += 1

    # Counts per domain (active)
    domain_counts: dict[str, int] = defaultdict(int)
    for r in active_records:
        domain_counts[r["domain"]] += 1

    lines: list[str] = [
        "# Dataset Inventory Report",
        "",
        "Generated automatically by `ml/inventory.py`.",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total files found | {total:,} |",
        f"| Augmented/derivative copies (flagged for exclusion) | {augmented:,} |",
        f"| Active original images | {active_total:,} |",
        f"| Corrupt files | {corrupt:,} |",
        f"| Lab images (active) | {domain_counts['lab']:,} |",
        f"| Field images (active) | {domain_counts['field']:,} |",
        f"| Negatives (active) | {domain_counts['negatives']:,} |",
        "",
        "## Per-source counts (Original Active Images)",
        "",
        "| Source | Images | Domain |",
        "|--------|--------|--------|",
    ]
    for src, cnt in sorted(source_counts.items(), key=lambda x: -x[1]):
        dom = "lab" if src == "plantvillage" else ("negatives" if "negatives" in src else "field")
        lines.append(f"| {src} | {cnt:,} | {dom} |")

    lines += [
        "",
        "## Per-class counts (canonical labels, Active Images)",
        "",
        "| Canonical Class | Total | Crop | Field Images | Lab Images |",
        "|-----------------|-------|------|--------------|------------|",
    ]
    for lbl, cnt in sorted(label_counts.items(), key=lambda x: -x[1]):
        crop = canonical_crop(lbl)
        field_cnt = sum(1 for r in active_records if r["canonical"] == lbl and r["domain"] == "field")
        lab_cnt = sum(1 for r in active_records if r["canonical"] == lbl and r["domain"] == "lab")
        lines.append(f"| `{lbl}` | {cnt:,} | {crop} | {field_cnt:,} | {lab_cnt:,} |")

    lines += [
        "",
        "## Imbalance Analysis",
        "",
    ]
    leaf_classes = {k: v for k, v in label_counts.items() if k != "unknown"}
    if leaf_classes:
        max_cls = max(leaf_classes, key=leaf_classes.get)  # type: ignore[arg-type]
        min_cls = min(leaf_classes, key=leaf_classes.get)  # type: ignore[arg-type]
        ratio = leaf_classes[max_cls] / max(1, leaf_classes[min_cls])
        lines += [
            f"- Largest plant class: `{max_cls}` ({leaf_classes[max_cls]:,} images)",
            f"- Smallest plant class: `{min_cls}` ({leaf_classes[min_cls]:,} images)",
            f"- Class imbalance ratio: {ratio:.1f}x",
            f"- Negatives / Unknown count: {label_counts.get('unknown', 0):,} images",
        ]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dataset inventory.")
    parser.add_argument("--data-dir", default="data/raw", help="Root of raw datasets")
    parser.add_argument("--check-corrupt", action="store_true", help="Check each file for corruption (slow)")
    args = parser.parse_args()

    data_root = Path(args.data_dir)
    if not data_root.exists():
        print(f"ERROR: data directory does not exist: {data_root}")
        sys.exit(1)

    all_records: list[dict] = []

    for dataset_dir in sorted(data_root.iterdir()):
        if not dataset_dir.is_dir():
            continue
        source_name = dataset_dir.name
        print(f"Scanning: {source_name} ...", end=" ", flush=True)
        records = scan_dataset(dataset_dir, source_name)
        print(f"{len(records):,} images")

        if args.check_corrupt:
            print("  Checking for corrupt files...")
            for r in records:
                r["corrupt"] = is_corrupt(Path(r["path"]))

        all_records.extend(records)

    print(f"\nTotal: {len(all_records):,} images across {len(set(r['source'] for r in all_records))} datasets")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_text = build_report(all_records)
    report_path = REPORTS_DIR / "inventory.md"
    report_path.write_text(report_text, encoding="utf-8")
    print(f"Report written to: {report_path}")


if __name__ == "__main__":
    main()
