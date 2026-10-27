"""
ml/download_datasets.py — download all candidate datasets for the disease model.

Usage (run from project root with .venv active and Kaggle token configured):
    python ml/download_datasets.py --data-dir data/raw

Datasets attempted (will report what failed):
  1. PlantVillage (original color) — Kaggle: abdallahalidev/plantvillage-dataset
  2. PlantDoc — Kaggle: pratikkayal/plantdoc-dataset
  3. PlantWild v1/v2 — HuggingFace: ai-agriculture/plant-disease-dataset
  4. Multiple Plant Diseases — Kaggle: alinedobrovsky/plant-diseases-classification
  5. Cucumber real-world — Kaggle: kareem25/cucumber-leaves-disease
  6. Cotton disease — Kaggle: janmejaybhoi/cotton-disease-dataset
  7. Wheat disease — Kaggle: (various — searched in script)
  8. Rice disease — Kaggle: (various — searched in script)
  9. Citrus disease — Kaggle: dtrilsbeek/citrus-leaves
 10. Mango disease — Kaggle: warcoder/mango-leaf-disease-dataset
 11. Negatives — COCO 2017 val (small subset via fiftyone or manual)

Each dataset is downloaded to data/raw/<dataset_name>/
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def run(cmd: list[str], cwd: Path | None = None) -> bool:
    """Run a shell command; return True on success."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FAILED: {result.stderr.strip()[:500]}")
        return False
    return True


def kaggle_download(dataset: str, dest_dir: Path) -> bool:
    """Download a Kaggle dataset to dest_dir."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    return run(
        ["kaggle", "datasets", "download", "-d", dataset, "-p", str(dest_dir), "--unzip"],
    )


def hf_download(repo_id: str, dest_dir: Path) -> bool:
    """Download a HuggingFace dataset snapshot to dest_dir."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id=repo_id, local_dir=str(dest_dir), repo_type="dataset")
        return True
    except Exception as exc:
        print(f"  FAILED: {exc}")
        return False


KAGGLE_DATASETS = [
    # (kaggle_dataset_id, local_folder_name, description)
    ("abdallahalidev/plantvillage-dataset", "plantvillage",
     "PlantVillage original color — main lab dataset"),
    ("pratikkayal/plantdoc-dataset", "plantdoc",
     "PlantDoc — field/in-the-wild images"),
    ("alinedobrovsky/plant-diseases-classification", "multi_plant",
     "Multiple Plant Diseases (cucumber, onion, potato, tomato, wheat, corn, rice, capsicum)"),
    ("kareem25/cucumber-leaves-disease", "cucumber_rw",
     "Cucumber real-world (Mendeley-style)"),
    ("janmejaybhoi/cotton-disease-dataset", "cotton",
     "Cotton leaf disease dataset"),
    ("warcoder/mango-leaf-disease-dataset", "mango",
     "Mango leaf disease dataset"),
    ("dtrilsbeek/citrus-leaves", "citrus",
     "Citrus leaf disease dataset"),
    ("vbookshelf/rice-leaf-diseases", "rice",
     "Rice leaf diseases dataset"),
    ("haidershabbirawan/wheat-disease-dataset", "wheat",
     "Wheat disease dataset"),
]

HF_DATASETS = [
    # (hf_repo_id, local_folder_name, description)
    # PlantWild — try v1; if missing, try v2
    ("trevorchan/plant-disease", "plantwild",
     "PlantWild — real-world plant images from HuggingFace"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Download all candidate datasets.")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--skip-hf", action="store_true", help="Skip HuggingFace downloads")
    parser.add_argument("--skip-kaggle", action="store_true", help="Skip Kaggle downloads")
    args = parser.parse_args()

    data_root = Path(args.data_dir)
    data_root.mkdir(parents=True, exist_ok=True)

    results: list[tuple[str, str, bool]] = []

    if not args.skip_kaggle:
        print("\n=== Kaggle datasets ===")
        for dataset_id, folder, desc in KAGGLE_DATASETS:
            dest = data_root / folder
            print(f"\n[{folder}] {desc}")
            if dest.exists() and any(dest.iterdir()):
                print("  Already downloaded — skipping.")
                results.append((folder, desc, True))
                continue
            ok = kaggle_download(dataset_id, dest)
            results.append((folder, desc, ok))

    if not args.skip_hf:
        print("\n=== HuggingFace datasets ===")
        for repo_id, folder, desc in HF_DATASETS:
            dest = data_root / folder
            print(f"\n[{folder}] {desc}")
            if dest.exists() and any(dest.iterdir()):
                print("  Already downloaded — skipping.")
                results.append((folder, desc, True))
                continue
            ok = hf_download(repo_id, dest)
            results.append((folder, desc, ok))

    print("\n=== Download summary ===")
    for folder, desc, ok in results:
        status = "✅" if ok else "❌ FAILED"
        print(f"  {status}  {folder}: {desc}")

    failed = [f for f, _, ok in results if not ok]
    if failed:
        print(f"\n{len(failed)} datasets failed to download: {failed}")
        print("Check Kaggle token and internet connection.")
        print("See docs/steps/02-data.md for manual instructions.")
        sys.exit(1)
    else:
        print("\nAll datasets downloaded successfully.")


if __name__ == "__main__":
    main()
