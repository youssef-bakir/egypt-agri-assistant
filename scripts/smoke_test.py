"""
scripts/smoke_test.py — end-to-end smoke test against a running server.

Usage:
    python scripts/smoke_test.py [--base-url http://localhost:8000]

Runs: register → login → diagnose (with sample image) → soil → history → logout.
Exits 0 on success, 1 on failure.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# httpx is in requirements-train.txt; installed on dev/test machines
try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Run: pip install httpx")
    sys.exit(1)

BASE_URL = "http://localhost:8000"
HEADERS = {"X-Requested-With": "fetch"}

# A tiny 1×1 green JPEG for the diagnose endpoint test
SAMPLE_IMAGE = Path(__file__).parent.parent / "tests" / "fixtures" / "sample_leaf.jpg"


def register(client: httpx.Client, username: str, password: str) -> None:
    r = client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": password},
        headers=HEADERS,
    )
    assert r.status_code in (200, 201, 409), f"register failed: {r.status_code} {r.text}"
    print(f"  register: {r.status_code}")


def login(client: httpx.Client, username: str, password: str) -> None:
    r = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
        headers=HEADERS,
    )
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    print(f"  login: {r.status_code}")


def health(client: httpx.Client) -> None:
    r = client.get("/api/v1/health")
    assert r.status_code == 200, f"health failed: {r.status_code} {r.text}"
    print(f"  health: {r.status_code} — {r.json()}")


def diagnose(client: httpx.Client) -> None:
    if not SAMPLE_IMAGE.exists():
        print("  diagnose: SKIP (no sample image at tests/fixtures/sample_leaf.jpg)")
        return
    with open(SAMPLE_IMAGE, "rb") as f:
        r = client.post(
            "/api/v1/diagnose",
            files={"image": ("leaf.jpg", f, "image/jpeg")},
            headers=HEADERS,
        )
    assert r.status_code == 200, f"diagnose failed: {r.status_code} {r.text}"
    data = r.json()
    assert "status" in data, "diagnose response missing 'status'"
    print(f"  diagnose: {r.status_code} — status={data.get('status')}")


def soil(client: httpx.Client) -> None:
    r = client.post(
        "/api/v1/soil/recommend",
        json={"N": 40, "P": 40, "K": 40, "temperature": 20.0,
              "humidity": 60.0, "ph": 6.5, "rainfall": 200.0},
        headers=HEADERS,
    )
    # 501 is acceptable if FEATURE_SOIL is disabled
    assert r.status_code in (200, 501), f"soil failed: {r.status_code} {r.text}"
    print(f"  soil: {r.status_code}")


def history(client: httpx.Client) -> None:
    r = client.get("/api/v1/history", headers=HEADERS)
    assert r.status_code in (200, 401), f"history failed: {r.status_code} {r.text}"
    print(f"  history: {r.status_code}")


def logout(client: httpx.Client) -> None:
    r = client.post("/api/v1/auth/logout", headers=HEADERS)
    assert r.status_code in (200, 204), f"logout failed: {r.status_code} {r.text}"
    print(f"  logout: {r.status_code}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    username = f"smoketest_{int(time.time())}"
    password = "Smoke1234!"

    print(f"Smoke test → {base}")
    with httpx.Client(base_url=base, timeout=30) as client:
        health(client)
        register(client, username, password)
        login(client, username, password)
        diagnose(client)
        soil(client)
        history(client)
        logout(client)

    print("\n✅ All smoke tests passed.")


if __name__ == "__main__":
    main()
