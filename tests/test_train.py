"""
tests/test_train.py — tests for preprocessing and training script helpers.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
from PIL import Image

import config
from ml.preprocess import (
    get_eval_transform,
    get_train_transform,
    preprocess_pil_for_serving,
    load_and_fix_image,
)
from ml.train import compute_manifest_sha256


def test_preprocess_pil_for_serving_shape():
    """Serving preprocess must return float32 tensor of shape (1, 3, H, W)."""
    img = Image.new("RGB", (300, 400), color=(100, 150, 200))
    arr = preprocess_pil_for_serving(img, image_size=config.IMAGE_SIZE)
    assert isinstance(arr, np.ndarray)
    assert arr.shape == (1, 3, config.IMAGE_SIZE, config.IMAGE_SIZE)
    assert arr.dtype == np.float32


def test_load_and_fix_image_from_bytes():
    """load_and_fix_image must correctly decode raw bytes into an RGB image."""
    import io
    img = Image.new("RGB", (64, 64), color=(50, 100, 150))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    loaded = load_and_fix_image(buf.getvalue())
    assert isinstance(loaded, Image.Image)
    assert loaded.mode == "RGB"
    assert loaded.size == (64, 64)


def test_compute_manifest_sha256():
    """Hash helper should return a valid 64-char hex string or 'none'."""
    p = ROOT / "data" / "manifest_clean.csv"
    h = compute_manifest_sha256(p)
    assert isinstance(h, str)
    if p.exists():
        assert len(h) == 64
    else:
        assert h == "none"
