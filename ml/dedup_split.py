"""
ml/dedup_split.py — near-duplicate detection and data splitting.

Steps:
1. Compute dHash (difference hash) for every image (implemented with Pillow + numpy — no OpenCV).
2. Group near-duplicates across ALL datasets (Hamming distance ≤ HASH_THRESHOLD).
3. Assign canonical split per group (train/val/test) using the spec's 70/15/15 rule for lab data.
4. Field dataset's own test splits → field_test; at least one whole field dataset → source_holdout.
5. Write data/manifest.csv: path, label, source, domain, split, group_id.

Tests ensure: no group_id appears in both train and val/test; field_test/source_holdout not in train.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path
from collections import defaultdict
from typing import Iterator

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from PIL import Image

from ml.label_map import normalize

HASH_BITS = 64        # dHash size: 8×8 grid → 64 bits
HASH_THRESHOLD = 8    # max Hamming distance to consider near-duplicate
MANIFEST_COLS = ["path", "label", "source", "domain", "split", "group_id"]

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

# Datasets that are treated as field data source_holdout (excluded from training)
SOURCE_HOLDOUT_DATASETS = {"plantdoc"}  # will be confirmed after Step 2 inventory


def dhash(image_path: Path, size: int = 8) -> int:
    """Compute dHash for an image. Returns an integer (size*size bits)."""
    try:
        with Image.open(image_path) as img:
            img = img.convert("L").resize((size + 1, size), Image.LANCZOS)
            arr = np.array(img, dtype=np.uint8)
            # Horizontal differences: compare adjacent pixels
            diff = arr[:, 1:] > arr[:, :-1]  # shape (size, size)
            # Pack bits into integer
            flat = diff.flatten()
            result = 0
            for bit in flat:
                result = (result << 1) | int(bit)
        return result
    except Exception:
        return -1  # corrupt / unreadable


def hamming(a: int, b: int) -> int:
    """Count differing bits between two hash integers."""
    return bin(a ^ b).count("1")


def assign_split(
    records: list[dict],
    source_holdout: set[str],
    field_test_sources: set[str],
    seed: int = 42,
) -> None:
    """Assign split to each record in-place.

    Rules:
    - source_holdout records → split = "source_holdout"
    - field_test_sources records → split = "field_test"
    - Others: group by group_id, assign 70/15/15 train/val/test by group
    """
    rng = np.random.default_rng(seed)

    # Collect groups for lab/train data
    group_to_records: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        if r["source"] in source_holdout:
            r["split"] = "source_holdout"
        elif r["source"] in field_test_sources:
            r["split"] = "field_test"
        else:
            group_to_records[r["group_id"]].append(r)

    # Shuffle groups and assign 70/15/15
    groups = list(group_to_records.keys())
    rng.shuffle(groups)
    n = len(groups)
    n_val = max(1, int(n * 0.15))
    n_test = max(1, int(n * 0.15))

    val_groups = set(groups[:n_val])
    test_groups = set(groups[n_val : n_val + n_test])

    for gid, recs in group_to_records.items():
        if gid in val_groups:
            split = "val"
        elif gid in test_groups:
            split = "lab_test"
        else:
            split = "train"
        for r in recs:
            r["split"] = split


def iter_images(data_root: Path) -> Iterator[dict]:
    """Iterate all images in data_root, yielding metadata dicts."""
    import re
    aug_pattern = re.compile(r"aug|rotated|flipped|augment", re.IGNORECASE)

    for dataset_dir in sorted(data_root.iterdir()):
        if not dataset_dir.is_dir():
            continue
        source = dataset_dir.name
        for root, _, files in sorted(
            [(r, d, f) for r, d, f in __import__("os").walk(dataset_dir)],
            key=lambda x: x[0],
        ):
            root_path = Path(root)
            for fname in sorted(files):
                fpath = root_path / fname
                if fpath.suffix.lower() not in IMAGE_EXTS:
                    continue

                # Skip augmented copies
                rel = str(fpath.relative_to(dataset_dir))
                if aug_pattern.search(rel):
                    continue

                rel_parts = fpath.relative_to(dataset_dir).parts
                raw_label = rel_parts[0] if len(rel_parts) > 1 else "unknown"
                label = normalize(raw_label)

                path_lower = str(fpath).lower()
                domain = "field" if any(
                    kw in path_lower for kw in ["field", "wild", "plantdoc", "real"]
                ) else "lab"

                yield {
                    "path": str(fpath),
                    "label": label,
                    "source": source,
                    "domain": domain,
                    "raw_label": raw_label,
                }


def main() -> None:
    parser = argparse.ArgumentParser(description="Near-duplicate grouping and splitting.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--output", default="data/manifest.csv")
    parser.add_argument("--threshold", type=int, default=HASH_THRESHOLD)
    parser.add_argument("--source-holdout", default="plantdoc",
                        help="Comma-separated dataset names to use as source_holdout")
    args = parser.parse_args()

    data_root = Path(args.data_dir)
    output_path = Path(args.output)
    source_holdout = set(args.source_holdout.split(","))

    if not data_root.exists():
        print(f"ERROR: data dir not found: {data_root}")
        sys.exit(1)

    print("Computing dHashes...")
    records: list[dict] = []
    hashes: list[int] = []

    for i, record in enumerate(iter_images(data_root)):
        h = dhash(Path(record["path"]))
        record["hash"] = h
        records.append(record)
        hashes.append(h)
        if (i + 1) % 1000 == 0:
            print(f"  {i+1:,} images processed...")

    print(f"Total images: {len(records):,}")

    # Near-duplicate grouping via union-find
    print(f"Grouping near-duplicates (threshold ≤ {args.threshold} bits)...")
    parent = list(range(len(records)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        parent[find(a)] = find(b)

    # O(n²) — acceptable for up to ~50k images; for larger use LSH
    for i in range(len(records)):
        if hashes[i] < 0:
            continue
        for j in range(i + 1, len(records)):
            if hashes[j] < 0:
                continue
            if hamming(hashes[i], hashes[j]) <= args.threshold:
                union(i, j)

    for i, r in enumerate(records):
        r["group_id"] = f"g{find(i):07d}"

    # Field test sources: all field-domain datasets except source_holdout
    field_sources = {
        r["source"] for r in records
        if r["domain"] == "field" and r["source"] not in source_holdout
    }

    print(f"Source holdout: {source_holdout}")
    print(f"Field test sources: {field_sources}")

    assign_split(records, source_holdout, field_sources)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_COLS)
        writer.writeheader()
        for r in records:
            writer.writerow({k: r.get(k, "") for k in MANIFEST_COLS})

    print(f"Manifest written to: {output_path} ({len(records):,} rows)")

    # Summary
    split_counts: dict[str, int] = defaultdict(int)
    for r in records:
        split_counts[r.get("split", "?")] += 1
    print("\nSplit summary:")
    for sp, cnt in sorted(split_counts.items()):
        print(f"  {sp}: {cnt:,}")


if __name__ == "__main__":
    main()
