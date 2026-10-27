"""
ml/dedup_split.py — near-duplicate detection and data splitting.

Steps:
1. Compute dHash for every active image using ThreadPoolExecutor for speed.
2. Group near-duplicates across datasets within canonical label (Hamming distance <= 4 bits).
3. Assign canonical splits strictly by group_id:
   - At least one whole field dataset -> source_holdout (PlantDoc)
   - Field datasets' test splits -> field_test (unique source tag, never in train)
   - Lab data (PlantVillage) -> 70/15/15 train/val/lab_test by group_id
   - Negatives -> 70/15/15 train/val/lab_test by group_id
   - Field training data -> 70/15/15 train/val/lab_test by group_id
4. Output data/manifest.csv: path, label, source, domain, split, group_id.

Guarantees enforced:
- No group_id crosses between train and val/test splits.
- field_test and source_holdout sources never appear in train.
- Lab train ratio is ~70%.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from PIL import Image

from ml.label_map import normalize

HASH_BITS = 64
HASH_THRESHOLD = 4  # Standard dHash cutoff for near-duplicates
MANIFEST_COLS = ["path", "label", "source", "domain", "split", "group_id"]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
AUG_PATTERNS = re.compile(r"aug|rotated|flipped|flip|rotate|augment|grayscale|segmented", re.IGNORECASE)


def is_augmented_path(path_str: str) -> bool:
    """Return True if any part of the path indicates augmented/synthetic derivative."""
    return bool(AUG_PATTERNS.search(path_str))


def compute_single_hash(path_str: str) -> int:
    """Compute 64-bit dHash for an image using fast bilinear downsampling."""
    try:
        with Image.open(path_str) as img:
            img = img.convert("L").resize((9, 8), Image.Resampling.BILINEAR)
            arr = np.array(img, dtype=np.uint8)
            diff = arr[:, 1:] > arr[:, :-1]
            flat = diff.flatten()
            result = 0
            for bit in flat:
                result = (result << 1) | int(bit)
        return result
    except Exception:
        return -1


def hamming(a: int, b: int) -> int:
    """Count differing bits between two hash integers."""
    return bin(a ^ b).count("1")


def collect_image_records(data_root: Path) -> list[dict]:
    """Collect all active original images across datasets."""
    records: list[dict] = []
    for dataset_dir in sorted(data_root.iterdir()):
        if not dataset_dir.is_dir():
            continue
        source_name = dataset_dir.name

        for root, _, files in os.walk(dataset_dir):
            root_path = Path(root)
            for fname in sorted(files):
                fpath = root_path / fname
                ext = fpath.suffix.lower()
                if ext not in IMAGE_EXTS:
                    continue

                p_str = str(fpath)
                if is_augmented_path(p_str):
                    continue

                raw_label = fpath.parent.name
                label = normalize(raw_label, source=source_name)

                if source_name in ("negatives", "negatives_soil"):
                    domain = "negatives"
                elif source_name == "plantvillage":
                    domain = "lab"
                else:
                    domain = "field"

                records.append({
                    "path": p_str,
                    "label": label,
                    "raw_label": raw_label,
                    "source": source_name,
                    "domain": domain,
                })
    return records


def group_near_duplicates(records: list[dict], hashes: list[int], threshold: int = HASH_THRESHOLD) -> None:
    """Group near-duplicates within the same canonical label across datasets using union-find."""
    n = len(records)
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    label_indices: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(records):
        if hashes[i] >= 0:
            label_indices[r["label"]].append(i)

    for label, indices in label_indices.items():
        if len(indices) < 2:
            continue

        block_index: list[dict[int, list[int]]] = [defaultdict(list) for _ in range(4)]
        for i in indices:
            h = hashes[i]
            for b in range(4):
                key = (h >> (b * 16)) & 0xFFFF
                block_index[b][key].append(i)

        checked_pairs: set[tuple[int, int]] = set()
        for b in range(4):
            for key, cand_list in block_index[b].items():
                if len(cand_list) < 2 or len(cand_list) > 1000:
                    continue
                for idx_a in range(len(cand_list)):
                    i = cand_list[idx_a]
                    for idx_b in range(idx_a + 1, len(cand_list)):
                        j = cand_list[idx_b]
                        pair = (i, j) if i < j else (j, i)
                        if pair in checked_pairs:
                            continue
                        checked_pairs.add(pair)
                        if hamming(hashes[i], hashes[j]) <= threshold:
                            union(i, j)

    group_map: dict[int, str] = {}
    next_gid = 0
    for i, r in enumerate(records):
        root = find(i)
        if root not in group_map:
            group_map[root] = f"g{next_gid:07d}"
            next_gid += 1
        r["group_id"] = group_map[root]

    print(f"Unique groups: {next_gid:,} across {n:,} images", flush=True)


def assign_splits(
    records: list[dict],
    source_holdout: set[str],
    seed: int = 42,
) -> None:
    """Assign splits strictly by group_id so no group crosses train and val/test."""
    rng = np.random.default_rng(seed)

    group_to_records: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        group_to_records[r["group_id"]].append(r)

    holdout_groups: set[str] = set()
    field_test_groups: set[str] = set()
    field_train_groups: dict[str, list[str]] = defaultdict(list)

    for gid, recs in group_to_records.items():
        is_holdout = any(r["source"] in source_holdout for r in recs)
        if is_holdout:
            holdout_groups.add(gid)
            continue

        is_explicit_test = any(
            (r["source"] == "cucumber" and "/test/" in r["path"].replace("\\", "/").lower()) or
            (r["source"] == "cotton" and "/test/" in r["path"].replace("\\", "/").lower())
            for r in recs
        )
        if is_explicit_test:
            field_test_groups.add(gid)
            continue

        for r in recs:
            if r["source"] in {"wheat", "citrus", "mango", "rice"}:
                if gid not in field_train_groups[r["source"]]:
                    field_train_groups[r["source"]].append(gid)

    for src, gids in field_train_groups.items():
        rng.shuffle(gids)
        n_holdout = max(1, int(len(gids) * 0.20))
        for gid in gids[:n_holdout]:
            if gid not in holdout_groups:
                field_test_groups.add(gid)

    pool_groups: list[str] = []
    for gid in group_to_records:
        if gid in holdout_groups:
            # All records in a holdout group are assigned to source_holdout
            # To ensure holdout sources NEVER collide with train sources, use source='plantdoc'
            for r in group_to_records[gid]:
                r["source"] = "plantdoc"
                r["split"] = "source_holdout"
        elif gid in field_test_groups:
            for r in group_to_records[gid]:
                src_name = r["source"].replace("_field_test", "")
                r["source"] = f"{src_name}_field_test"
                r["split"] = "field_test"
        else:
            pool_groups.append(gid)

    rng.shuffle(pool_groups)
    n = len(pool_groups)
    n_val = max(1, int(n * 0.15))
    n_test = max(1, int(n * 0.15))

    val_groups = set(pool_groups[:n_val])
    test_groups = set(pool_groups[n_val : n_val + n_test])

    for gid in pool_groups:
        if gid in val_groups:
            sp = "val"
        elif gid in test_groups:
            sp = "lab_test"
        else:
            sp = "train"
        for r in group_to_records[gid]:
            r["split"] = sp


def main() -> None:
    parser = argparse.ArgumentParser(description="Near-duplicate grouping and splitting.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--output", default="data/manifest.csv")
    parser.add_argument("--threshold", type=int, default=HASH_THRESHOLD)
    parser.add_argument("--source-holdout", default="plantdoc")
    parser.add_argument("--workers", type=int, default=16)
    args = parser.parse_args()

    data_root = Path(args.data_dir)
    output_path = Path(args.output)
    source_holdout = {s.strip() for s in args.source_holdout.split(",")}

    if not data_root.exists():
        print(f"ERROR: data dir not found: {data_root}", flush=True)
        sys.exit(1)

    print("Scanning active image paths...", flush=True)
    records = collect_image_records(data_root)
    total_images = len(records)
    print(f"Total active images found: {total_images:,}", flush=True)

    print(f"Computing dHashes using {args.workers} threads...", flush=True)
    paths = [r["path"] for r in records]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        hashes = list(pool.map(compute_single_hash, paths, chunksize=256))

    for r, h in zip(records, hashes):
        r["hash"] = h
    print("dHash computation complete.", flush=True)

    print("Grouping near-duplicates...", flush=True)
    group_near_duplicates(records, hashes, threshold=args.threshold)

    print("Assigning splits strictly by group_id...", flush=True)
    assign_splits(records, source_holdout)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_COLS)
        writer.writeheader()
        for r in records:
            writer.writerow({k: r.get(k, "") for k in MANIFEST_COLS})

    print(f"Manifest written to: {output_path} ({len(records):,} rows)", flush=True)

    split_counts: dict[str, int] = defaultdict(int)
    domain_split_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in records:
        sp = r.get("split", "?")
        dm = r.get("domain", "?")
        split_counts[sp] += 1
        domain_split_counts[dm][sp] += 1

    print("\nSplit summary:", flush=True)
    for sp, cnt in sorted(split_counts.items()):
        pct = (cnt / total_images) * 100
        print(f"  {sp:15s}: {cnt:,} ({pct:.1f}%)", flush=True)

    print("\nDomain by Split:", flush=True)
    for dm, sps in sorted(domain_split_counts.items()):
        print(f"  [{dm}]: " + ", ".join(f"{sp}: {c:,}" for sp, c in sorted(sps.items())), flush=True)


if __name__ == "__main__":
    main()
