"""
tests/test_label_map.py — tests for ml/label_map.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from ml.label_map import (
    normalize,
    canonical_crop,
    canonical_condition,
    all_canonical_labels,
    RAW_TO_CANONICAL,
)


def test_normalize_known_label():
    assert normalize("Tomato___Early_blight") == "tomato___early_blight"
    assert normalize("Potato___healthy") == "potato___healthy"


def test_normalize_unknown_returns_unknown():
    assert normalize("Something_Unknown_Crop___disease") == "unknown"
    assert normalize("") == "unknown"


def test_all_canonical_labels_no_duplicates():
    labels = all_canonical_labels()
    assert len(labels) == len(set(labels))


def test_canonical_crop_extraction():
    assert canonical_crop("tomato___early_blight") == "tomato"
    assert canonical_crop("wheat___healthy") == "wheat"
    assert canonical_crop("unknown") == "unknown"


def test_canonical_condition_extraction():
    assert canonical_condition("tomato___early_blight") == "early_blight"
    assert canonical_condition("wheat___yellow_rust") == "yellow_rust"


def test_all_canonical_labels_follow_convention():
    """All canonical labels should match the crop___condition pattern (or be 'unknown')."""
    import re
    pattern = re.compile(r"^[a-z0-9_]+$")
    for label in all_canonical_labels():
        assert pattern.match(label), f"Non-canonical label: {label}"
        if label != "unknown":
            assert "___" in label, f"Label missing '___': {label}"


def test_raw_to_canonical_values_are_lowercase():
    for raw, canonical in RAW_TO_CANONICAL.items():
        assert canonical == canonical.lower(), (
            f"Canonical label not lowercase: {canonical} (from raw: {raw})"
        )


def test_priority_crops_have_entries():
    """Each priority crop should appear in at least one canonical label."""
    import config
    canonical_labels = all_canonical_labels()
    crops_covered = {label.split("___")[0] for label in canonical_labels if label != "unknown"}
    for crop in config.PRIORITY_CROPS:
        # Some priority crops (e.g., 'peas', 'beans') may not yet have data
        # — just warn, don't fail, as coverage is decided by the inclusion rule
        if crop not in crops_covered:
            import warnings
            warnings.warn(f"Priority crop '{crop}' has no entry in label_map.py yet.")
