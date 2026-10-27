"""
ml/apply_inclusion_rule.py — automatically apply the inclusion rule to finalize SUPPORTED_CLASSES.

Inclusion rule (from spec section 1):
  A crop/class is SUPPORTED only if, after cleaning and de-duplication:
    - at least MIN_TRAIN_IMAGES training images
    - at least MIN_FIELD_TEST_IMAGES images in the held-out test sets (field_test or source_holdout)

Classes failing this rule → treated as "unknown" in the manifest.
Writes the final SUPPORTED_CLASSES list into config.py.

Usage:
    python ml/apply_inclusion_rule.py --manifest data/manifest_clean.csv
"""

from __future__ import annotations

import argparse
import ast
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import config


def load_manifest(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compute_class_counts(records: list[dict]) -> dict[str, dict[str, int]]:
    """Return per-class counts for train, field_test, and source_holdout splits."""
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in records:
        label = r["label"]
        split = r["split"]
        if label == "unknown":
            continue
        counts[label][split] += 1
    return counts


def apply_rule(
    counts: dict[str, dict[str, int]],
    min_train: int = config.MIN_TRAIN_IMAGES,
    min_field: int = config.MIN_FIELD_TEST_IMAGES,
) -> tuple[list[str], list[str]]:
    """Return (supported_classes, excluded_classes) after applying the inclusion rule."""
    supported = []
    excluded = []
    for label, splits in sorted(counts.items()):
        train_count = splits.get("train", 0)
        field_count = splits.get("field_test", 0) + splits.get("source_holdout", 0)
        if train_count >= min_train and field_count >= min_field:
            supported.append(label)
        else:
            excluded.append(label)
    return supported, excluded


def write_report(
    supported: list[str],
    excluded: list[str],
    counts: dict[str, dict[str, int]],
    output: Path,
) -> None:
    lines = [
        "# Inclusion Rule Report",
        "",
        f"Min train images: {config.MIN_TRAIN_IMAGES}",
        f"Min field/holdout test images: {config.MIN_FIELD_TEST_IMAGES}",
        "",
        f"## Supported classes ({len(supported)})",
        "",
        "| Class | Train | Field/Holdout |",
        "|-------|-------|---------------|",
    ]
    for lbl in supported:
        sp = counts[lbl]
        field = sp.get("field_test", 0) + sp.get("source_holdout", 0)
        lines.append(f"| {lbl} | {sp.get('train',0)} | {field} |")

    lines += [
        "",
        f"## Excluded classes ({len(excluded)}) — treated as `unknown`",
        "",
        "| Class | Train | Field/Holdout | Reason |",
        "|-------|-------|---------------|--------|",
    ]
    for lbl in excluded:
        sp = counts[lbl]
        train = sp.get("train", 0)
        field = sp.get("field_test", 0) + sp.get("source_holdout", 0)
        reasons = []
        if train < config.MIN_TRAIN_IMAGES:
            reasons.append(f"train {train} < {config.MIN_TRAIN_IMAGES}")
        if field < config.MIN_FIELD_TEST_IMAGES:
            reasons.append(f"field {field} < {config.MIN_FIELD_TEST_IMAGES}")
        lines.append(f"| {lbl} | {train} | {field} | {'; '.join(reasons)} |")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to: {output}")


def patch_config(supported: list[str]) -> None:
    """Overwrite SUPPORTED_CLASSES in config.py with the real list."""
    config_path = ROOT / "config.py"
    content = config_path.read_text(encoding="utf-8")

    new_list_repr = repr(supported)
    # Replace the SUPPORTED_CLASSES = [] line
    import re
    pattern = r"SUPPORTED_CLASSES:\s*list\[str\]\s*=\s*\[.*?\]"
    replacement = f"SUPPORTED_CLASSES: list[str] = {new_list_repr}"
    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if count == 0:
        print("WARNING: Could not find SUPPORTED_CLASSES in config.py — not updated.")
        return
    config_path.write_text(new_content, encoding="utf-8")
    print(f"config.py updated: SUPPORTED_CLASSES = {len(supported)} classes")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply inclusion rule to finalize supported classes.")
    parser.add_argument("--manifest", default="data/manifest_clean.csv")
    parser.add_argument("--report-out", default="reports/inclusion_rule.md")
    parser.add_argument("--patch-config", action="store_true", default=True)
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        # Try the un-cleaned version
        manifest_path = Path("data/manifest.csv")
        if not manifest_path.exists():
            print(f"ERROR: manifest not found. Run ml/dedup_split.py first.")
            sys.exit(1)
        print(f"WARNING: using uncleaned manifest: {manifest_path}")

    records = load_manifest(manifest_path)
    counts = compute_class_counts(records)
    supported, excluded = apply_rule(counts)

    print(f"\nInclusion rule result:")
    print(f"  Supported: {len(supported)} classes")
    print(f"  Excluded: {len(excluded)} classes")

    write_report(supported, excluded, counts, Path(args.report_out))

    if args.patch_config:
        patch_config(supported)


if __name__ == "__main__":
    main()
