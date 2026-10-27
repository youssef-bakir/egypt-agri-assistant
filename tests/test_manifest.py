"""
tests/test_manifest.py — integrity tests for the data manifest.

These tests run after ml/dedup_split.py produces data/manifest.csv.
They enforce the data split guarantees specified in section 8 Step 3:
  - No group_id appears in both train and val/test
  - field_test / source_holdout never in train
  - All required columns exist
  - No empty labels
"""

from __future__ import annotations

import csv
import pytest
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent
MANIFEST_PATH = ROOT / "data" / "manifest.csv"
MANIFEST_CLEAN_PATH = ROOT / "data" / "manifest_clean.csv"

REQUIRED_COLS = {"path", "label", "source", "domain", "split", "group_id"}
VALID_SPLITS = {"train", "val", "lab_test", "field_test", "source_holdout"}


def load_manifest(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


# Skip all tests if manifest doesn't exist (Step 2/3 not run yet)
pytestmark = pytest.mark.skipif(
    not MANIFEST_PATH.exists(),
    reason="data/manifest.csv not found — run Step 2 and Step 3 first",
)


@pytest.fixture(scope="module")
def manifest() -> list[dict]:
    return load_manifest(MANIFEST_PATH)


def test_manifest_has_required_columns(manifest):
    """All required columns must be present in the manifest."""
    assert manifest, "Manifest is empty"
    actual_cols = set(manifest[0].keys())
    assert REQUIRED_COLS.issubset(actual_cols), (
        f"Missing columns: {REQUIRED_COLS - actual_cols}"
    )


def test_all_splits_are_valid(manifest):
    """All split values must be from the known set."""
    invalid = {r["split"] for r in manifest if r["split"] not in VALID_SPLITS}
    assert not invalid, f"Invalid split values found: {invalid}"


def test_no_empty_labels(manifest):
    """Every row must have a non-empty label."""
    empty = [r["path"] for r in manifest if not r.get("label", "").strip()]
    assert not empty, f"Rows with empty labels: {empty[:5]}"


def test_no_group_id_crosses_train_and_test(manifest):
    """No group_id may appear in both train and any test split."""
    train_groups: set[str] = set()
    test_groups: set[str] = set()

    for r in manifest:
        gid = r["group_id"]
        split = r["split"]
        if split == "train":
            train_groups.add(gid)
        elif split in ("lab_test", "field_test", "source_holdout"):
            test_groups.add(gid)

    overlap = train_groups & test_groups
    assert not overlap, (
        f"Data leak! {len(overlap)} group_id(s) appear in both train and test: "
        f"{sorted(overlap)[:5]}"
    )


def test_no_group_id_crosses_train_and_val(manifest):
    """No group_id may appear in both train and val."""
    train_groups: set[str] = set()
    val_groups: set[str] = set()

    for r in manifest:
        gid = r["group_id"]
        if r["split"] == "train":
            train_groups.add(gid)
        elif r["split"] == "val":
            val_groups.add(gid)

    overlap = train_groups & val_groups
    assert not overlap, (
        f"Data leak! {len(overlap)} group_id(s) appear in both train and val."
    )


def test_source_holdout_not_in_train(manifest):
    """source_holdout records must never appear in the training split."""
    # A source assigned to source_holdout should not also appear in train
    holdout_sources: set[str] = {r["source"] for r in manifest if r["split"] == "source_holdout"}
    violations = [
        r for r in manifest
        if r["split"] == "train" and r["source"] in holdout_sources
    ]
    assert not violations, (
        f"Source holdout data leaked into training! "
        f"Sources: {holdout_sources}, first violation: {violations[0]}"
    )


def test_field_test_not_in_train(manifest):
    """field_test records must never appear in the training split."""
    field_test_sources: set[str] = {r["source"] for r in manifest if r["split"] == "field_test"}
    violations = [
        r for r in manifest
        if r["split"] == "train" and r["source"] in field_test_sources
    ]
    assert not violations, (
        f"Field test data leaked into training! Sources: {field_test_sources}"
    )


def test_split_ratios_are_reasonable(manifest):
    """train/val/test should be roughly 70/15/15 for lab data."""
    split_counts: dict[str, int] = defaultdict(int)
    for r in manifest:
        if r["domain"] == "lab":
            split_counts[r["split"]] += 1

    total_lab = sum(split_counts.values())
    if total_lab < 10:
        pytest.skip("Too few lab images to check ratios")

    train_frac = split_counts["train"] / total_lab
    # Allow generous tolerance: 50-85% train
    assert 0.50 <= train_frac <= 0.85, (
        f"Train fraction unexpected: {train_frac:.2f} (expected ~0.70)"
    )
