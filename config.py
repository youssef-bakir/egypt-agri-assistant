"""
config.py — central configuration for Egypt Agri Assistant.

All settings come from environment variables with safe dev defaults.
Import this module wherever you need app-wide constants or settings.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv  # python-dotenv (listed in requirements.txt)

# Load .env from project root (silently ignored if the file does not exist)
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# ── Environment ──────────────────────────────────────────────────────────────
ENV: str = os.getenv("ENV", "dev")  # "dev" | "prod"
IS_PROD: bool = ENV == "prod"

# ── Secret key ────────────────────────────────────────────────────────────────
_DEFAULT_KEY = "insecure-dev-key-do-not-use-in-production"
SECRET_KEY: str = os.getenv("SECRET_KEY", _DEFAULT_KEY)
if IS_PROD and SECRET_KEY == _DEFAULT_KEY:
    raise RuntimeError("SECRET_KEY must be set to a secure value in production.")

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "sqlite+aiosqlite:///./egypt_agri.db"
)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR: Path = Path(__file__).parent
DATA_DIR: Path = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
MODELS_DIR: Path = BASE_DIR / "models"
UPLOAD_DIR: Path = DATA_DIR / "uploads"  # outside web root, random names
KNOWLEDGE_DIR: Path = BASE_DIR / "knowledge"
WEB_DIR: Path = BASE_DIR / "web"

# ── Disease model ──────────────────────────────────────────────────────────────
IMAGE_SIZE: int = 224          # px (square); see benchmark step for final choice
MAX_IMAGE_BYTES: int = 8 * 1024 * 1024  # 8 MB upload limit
MIN_IMAGE_SIDE: int = 64       # px — smaller images are rejected as too_small
CONFIDENCE_THRESHOLD: float = 0.60   # below → uncertain (tuned in Step 7)
UNKNOWN_CLASS: str = "unknown"

# ── Supported crops (inclusion rule applied in Step 3 — do not edit manually) ──
# Each entry: "crop___condition"   (three underscores, as in PlantVillage naming)
# This list is populated automatically by ml/inventory.py after cleaning.
SUPPORTED_CLASSES: list[str] = ['apple___apple_scab', 'apple___cedar_apple_rust', 'apple___healthy', 'blueberry___healthy', 'cherry___healthy', 'citrus___greening', 'cotton___disease', 'cotton___healthy', 'cucumber___downy_mildew', 'cucumber___healthy', 'cucumber___powdery_mildew', 'grape___black_rot', 'grape___healthy', 'maize___common_rust', 'maize___gray_leaf_spot', 'maize___northern_leaf_blight', 'mango___anthracnose', 'mango___bacterial_canker', 'mango___cutting_weevil', 'mango___die_back', 'mango___gall_midge', 'mango___healthy', 'mango___powdery_mildew', 'mango___sooty_mould', 'peach___healthy', 'pepper___bacterial_spot', 'pepper___healthy', 'potato___early_blight', 'potato___late_blight', 'raspberry___healthy', 'soybean___healthy', 'squash___powdery_mildew', 'strawberry___healthy', 'tomato___bacterial_spot', 'tomato___early_blight', 'tomato___healthy', 'tomato___late_blight', 'tomato___leaf_mold', 'tomato___mosaic_virus', 'tomato___septoria_leaf_spot', 'tomato___yellow_leaf_curl_virus']  # TODO: filled by Step 3

# Egyptian priority crops (used to filter datasets in Step 2)
PRIORITY_CROPS: list[str] = [
    # vegetables
    "tomato", "potato", "cucumber", "pepper", "eggplant",
    "onion", "squash", "peas", "beans",
    # field crops
    "wheat", "maize", "corn", "rice", "cotton",
    # fruits
    "grape", "citrus", "strawberry", "mango",
]

# Minimum images per class after cleaning (inclusion rule — section 1 of spec)
MIN_TRAIN_IMAGES: int = 150
MIN_FIELD_TEST_IMAGES: int = 30

# ── Soil model ────────────────────────────────────────────────────────────────
# Feature order MUST match the training data (set in soil/train.py)
SOIL_FEATURE_NAMES: list[str] = [
    "N", "P", "K", "temperature", "humidity", "ph", "rainfall"
]
SOIL_TOP_K: int = 3  # how many crops to return

# ── Feature switches ──────────────────────────────────────────────────────────
FEATURE_SOIL: bool = os.getenv("FEATURE_SOIL", "true").lower() == "true"
FEATURE_FEEDBACK: bool = os.getenv("FEATURE_FEEDBACK", "true").lower() == "true"

# ── Auth ──────────────────────────────────────────────────────────────────────
SESSION_COOKIE_NAME: str = "session"
LOGIN_THROTTLE_MAX_ATTEMPTS: int = 5
LOGIN_THROTTLE_WINDOW_SECONDS: int = 15 * 60  # 15 minutes
USERNAME_MIN_LEN: int = 3
USERNAME_MAX_LEN: int = 30
PASSWORD_MIN_LEN: int = 8

# ── Serving ───────────────────────────────────────────────────────────────────
API_VERSION: str = "v1"
MODEL_VERSION: str = "0.0.0"  # updated when a model is exported
LATENCY_WARMUP_RUNS: int = 3   # inference runs on startup to warm up ONNX
