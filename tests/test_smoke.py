"""
tests/test_smoke.py — basic sanity checks for Step 1.

These tests verify that the project structure and config are correct.
No running server needed.
"""

from pathlib import Path
import importlib
import sys

ROOT = Path(__file__).parent.parent


def test_config_imports_without_error():
    """config.py must be importable without errors."""
    # Add project root to path if not already there
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    config = importlib.import_module("config")
    assert config.ENV in ("dev", "prod")
    assert config.IMAGE_SIZE > 0
    assert config.MAX_IMAGE_BYTES > 0
    assert config.MIN_IMAGE_SIDE > 0
    assert 0.0 < config.CONFIDENCE_THRESHOLD < 1.0
    assert len(config.PRIORITY_CROPS) > 0
    assert config.USERNAME_MIN_LEN < config.USERNAME_MAX_LEN
    assert config.PASSWORD_MIN_LEN >= 8


def test_required_files_exist():
    """All files mandated by the spec must exist."""
    required = [
        "PROJECT_SPEC.md",
        "PROGRESS.md",
        "DECISIONS.md",
        "README.md",
        ".gitignore",
        ".env.example",
        "config.py",
        "requirements.txt",
        "requirements-train.txt",
        "Dockerfile",
    ]
    for fname in required:
        assert (ROOT / fname).exists(), f"Missing required file: {fname}"


def test_required_directories_exist():
    """All top-level directories must exist."""
    required_dirs = [
        "ml", "soil", "app", "app/api", "app/api/v1",
        "app/services", "app/db",
        "knowledge", "web", "web/css", "web/js", "web/i18n",
        "models", "reports", "scripts", "tests",
        "docs", "docs/steps", "docs/checkpoints",
    ]
    for dname in required_dirs:
        assert (ROOT / dname).is_dir(), f"Missing required directory: {dname}"


def test_gitignore_excludes_secrets():
    """.gitignore must exclude .env and kaggle.json."""
    content = (ROOT / ".gitignore").read_text()
    assert ".env" in content
    assert "kaggle.json" in content
    assert "__pycache__" in content


def test_env_example_has_required_keys():
    """.env.example must document the required environment variables."""
    content = (ROOT / ".env.example").read_text()
    required_keys = ["ENV", "SECRET_KEY", "DATABASE_URL", "DATA_DIR"]
    for key in required_keys:
        assert key in content, f"Missing key in .env.example: {key}"


def test_decisions_has_all_decisions():
    """DECISIONS.md must contain all D1-D13 decisions."""
    content = (ROOT / "DECISIONS.md").read_text()
    for i in range(1, 14):
        assert f"D{i}" in content, f"Missing decision D{i} in DECISIONS.md"


def test_requirements_has_core_packages():
    """requirements.txt must list all required runtime packages."""
    content = (ROOT / "requirements.txt").read_text().lower()
    required = [
        "fastapi", "uvicorn", "pydantic", "sqlalchemy",
        "argon2-cffi", "itsdangerous", "onnxruntime",
        "scikit-learn", "joblib", "numpy", "pillow",
    ]
    for pkg in required:
        assert pkg in content, f"Missing package in requirements.txt: {pkg}"
