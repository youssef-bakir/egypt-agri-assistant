"""
ml/preprocess.py — THE ONLY preprocessing definition for the disease model.

This module is used identically in:
  - Training (ml/train.py)
  - Evaluation / benchmark (ml/evaluate.py)
  - ONNX serving (app/services/inference.py)

Changes here automatically propagate everywhere. NEVER define image transforms elsewhere.

Transform pipeline:
  Training:   random resized crop → flips → small rotation → color jitter → blur → random erasing → normalize
  Eval/serve: center crop → normalize   (deterministic)

Image size: from config.IMAGE_SIZE (default 224).
"""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image
import numpy as np

# Config import (no torch needed here; transforms are lazy-built)
import config

# ── Constants ─────────────────────────────────────────────────────────────────
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def get_train_transform(image_size: int = config.IMAGE_SIZE):
    """Return torchvision transform for training (data augmentation included)."""
    from torchvision import transforms
    return transforms.Compose([
        transforms.RandomResizedCrop(image_size, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(p=0.1),
        transforms.RandomRotation(degrees=15),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
        transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        transforms.RandomErasing(p=0.2, scale=(0.02, 0.1)),
    ])


def get_eval_transform(image_size: int = config.IMAGE_SIZE):
    """Return torchvision transform for evaluation and serving (deterministic)."""
    from torchvision import transforms
    return transforms.Compose([
        transforms.Resize(int(image_size * 1.143)),   # e.g., 256 for size=224
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def preprocess_pil_for_serving(
    pil_image: Image.Image,
    image_size: int = config.IMAGE_SIZE,
) -> np.ndarray:
    """Preprocess a PIL Image for ONNX serving.

    Returns a numpy array of shape (1, 3, H, W) with dtype float32.
    This mirrors get_eval_transform exactly, without torch (uses numpy only).
    """
    import math

    # Resize: short side to int(image_size * 1.143), preserve aspect ratio
    w, h = pil_image.size
    target_short = int(image_size * 1.143)
    scale = target_short / min(w, h)
    new_w = math.ceil(w * scale)
    new_h = math.ceil(h * scale)
    img = pil_image.resize((new_w, new_h), Image.LANCZOS)

    # Center crop
    left = (new_w - image_size) // 2
    top = (new_h - image_size) // 2
    img = img.crop((left, top, left + image_size, top + image_size))

    # To numpy float32 [0, 1]
    arr = np.array(img, dtype=np.float32) / 255.0

    # Normalize (HWC)
    mean = np.array(IMAGENET_MEAN, dtype=np.float32)
    std = np.array(IMAGENET_STD, dtype=np.float32)
    arr = (arr - mean) / std

    # HWC → NCHW
    arr = arr.transpose(2, 0, 1)[np.newaxis, :]  # (1, 3, H, W)
    return arr.astype(np.float32)


def load_and_fix_image(path_or_bytes) -> Image.Image:
    """Open an image file, apply EXIF orientation, return RGB PIL image.

    Accepts a file path (str/Path) or bytes.
    Raises ValueError on corrupt/non-image input.
    """
    try:
        if isinstance(path_or_bytes, (str, Path)):
            img = Image.open(path_or_bytes)
        else:
            import io
            img = Image.open(io.BytesIO(path_or_bytes))

        # Apply EXIF orientation
        try:
            from PIL.ImageOps import exif_transpose
            img = exif_transpose(img)
        except Exception:
            pass  # non-critical

        return img.convert("RGB")
    except Exception as exc:
        raise ValueError(f"Cannot open image: {exc}") from exc
