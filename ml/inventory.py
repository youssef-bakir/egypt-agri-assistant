"""
ml/inventory.py — scan downloaded datasets and produce reports/inventory.md.

Usage:
    python ml/inventory.py --data-dir data/raw

Output: reports/inventory.md with:
  - counts per class / source / domain
  - corrupt files
  - size statistics
  - imbalance analysis
  - augmented-copy detection (folders/filenames with 'aug')
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.label_map import normalize, canonical_crop

REPORTS_DIR = Path(__file__).parent.parent / "reports"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
AUG_PATTERNS = re.compile(r"aug|rotated|flipped|flip|rotate|augment", re.IGNORECASE)


def is_augmented_path(path: Path) -> bool:
    """Return True if the file or any parent folder looks like an augmented copy."""
    for part in path.parts:
        if AUG_PATTERNS.search(part):
            return True
    return False


def guess_domain(path: Path) -> str:
    """Guess lab vs field from path segments."""
    path_str = str(path).lower()
    if any(kw in path_str for kw in ["field", "wild", "real", "farm", "plantdoc", "plantwild"]):
        return "field"
    return "lab"


def is_corrupt(path: Path) -> bool:
    """Quick check: try to open the file header."""
    try:
        from PIL import Image
        with Image.open(path) as img:
            img.verify()
        return False
    except Exception:
        return True


def scan_dataset(
    dataset_dir: Path,
    source_name: str,
) -> list[dict]:
    """Walk a dataset directory and collect per-image metadata."""
    records: list[dict] = []
    for root, _dirs, files in os.walk(dataset_dir):
        root_path = Path(root)
        for fname in files:
            fpath = root_path / fname
            if fpath.suffix.lower() not in IMAGE_EXTS:
                continue

            # The folder name relative to dataset_dir[1st level] is the raw label
            rel = fpath.relative_to(dataset_dir)
            raw_label = rel.parts[0] if len(rel.parts) > 1 else "unknown"

            records.append({
                "path": str(fpath),
                "raw_label": raw_label,
                "canonical": normalize(raw_label),
                "source": source_name,
                "domain": guess_domain(fpath),
                "augmented": is_augmented_path(fpath),
                "size_bytes": fpath.stat().st_size,
                "corrupt": False,  # checked separately for speed
            })
    return records


def build_report(records: list[dict]) -> str:
    """Build a markdown report string from the inventory records."""
    total = len(records)
    augmented = sum(1 for r in records if r["augmented"])
    corrupt = sum(1 for r in records if r["corrupt"])

    # Counts per canonical label
    label_counts: dict[str, int] = defaultdict(int)
    for r in records:
        label_counts[r["canonical"]] += 1

    # Counts per source
    source_counts: dict[str, int] = defaultdict(int)
    for r in records:
        source_counts[r["source"]] += 1

    # Counts per domain
    domain_counts: dict[str, int] = defaultdict(int)
    for r in records:
        domain_counts[r["domain"]] += 1

    lines: list[str] = [
        "# Dataset Inventory Report",
        "",
        f"Generated automatically by `ml/inventory.py`.",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total images | {total:,} |",
        f"| Augmented copies (excluded) | {augmented:,} |",
        f"| Corrupt files | {corrupt:,} |",
        f"| Lab images | {domain_counts['lab']:,} |",
        f"| Field images | {domain_counts['field']:,} |",
        "",
        "## Per-source counts",
        "",
        "| Source | Images |",
        "|--------|--------|",
    ]
    for src, cnt in sorted(source_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {src} | {cnt:,} |")

    lines += [
        "",
        "## Per-class counts (canonical labels)",
        "",
        "| Class | Count | Crop | Domain guess |",
        "|-------|-------|------|--------------|",
    ]
    for lbl, cnt in sorted(label_counts.items(), key=lambda x: -x[1]):
        crop = canonical_crop(lbl)
        # Rough domain breakdown per label
        field_cnt = sum(1 for r in records if r["canonical"] == lbl and r["domain"] == "field")
        lines.append(f"| {lbl} | {cnt:,} | {crop} | field:{field_cnt} lab:{cnt-field_cnt} |")

    lines += [
        "",
        "## Imbalance",
        "",
    ]
    if label_counts:
        max_cls = max(label_counts, key=label_counts.get)  # type: ignore[arg-type]
        min_cls = min(label_counts, key=label_counts.get)  # type: ignore[arg-type]
        lines += [
            f"- Largest class: `{max_cls}` ({label_counts[max_cls]:,} images)",
            f"- Smallest class: `{min_cls}` ({label_counts[min_cls]:,} images)",
            f"- Ratio: {label_counts[max_cls] / max(1, label_counts[min_cls]):.1f}×",
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

    # Each sub-folder of data/raw is treated as a separate dataset (source)
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
