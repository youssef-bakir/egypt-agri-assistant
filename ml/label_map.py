"""
ml/label_map.py — explicit mapping from raw dataset labels → canonical crop___condition.

Rules:
- Canonical format:  "crop___condition"  (three underscores, lowercase, underscores for spaces)
- Healthy leaves:    "crop___healthy"
- Unknown/unsupported: "unknown"
- This file is the SINGLE source of truth for label normalization.

Any raw label not in RAW_TO_CANONICAL maps to "unknown" automatically.
Add new entries here as new datasets are added — never hard-code strings elsewhere.
"""

from __future__ import annotations

# ── Canonical label format ────────────────────────────────────────────────────
# Pattern:  "<crop>___<condition>"
# All lowercase; spaces replaced with "_".
# Diseases with multiple names: pick the most specific common name.

# Raw label (as it appears in the dataset) → canonical label
RAW_TO_CANONICAL: dict[str, str] = {
    # ── PlantVillage — Tomato ──────────────────────────────────────────────
    "Tomato___Bacterial_spot": "tomato___bacterial_spot",
    "Tomato___Early_blight": "tomato___early_blight",
    "Tomato___Late_blight": "tomato___late_blight",
    "Tomato___Leaf_Mold": "tomato___leaf_mold",
    "Tomato___Septoria_leaf_spot": "tomato___septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite": "tomato___spider_mites",
    "Tomato___Target_Spot": "tomato___target_spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "tomato___yellow_leaf_curl_virus",
    "Tomato___Tomato_mosaic_virus": "tomato___mosaic_virus",
    "Tomato___healthy": "tomato___healthy",

    # ── PlantVillage — Potato ──────────────────────────────────────────────
    "Potato___Early_blight": "potato___early_blight",
    "Potato___Late_blight": "potato___late_blight",
    "Potato___healthy": "potato___healthy",

    # ── PlantVillage — Pepper ──────────────────────────────────────────────
    "Pepper,_bell___Bacterial_spot": "pepper___bacterial_spot",
    "Pepper,_bell___healthy": "pepper___healthy",

    # ── PlantVillage — Grape ───────────────────────────────────────────────
    "Grape___Black_rot": "grape___black_rot",
    "Grape___Esca_(Black_Measles)": "grape___esca",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "grape___leaf_blight",
    "Grape___healthy": "grape___healthy",

    # ── PlantVillage — Strawberry ──────────────────────────────────────────
    "Strawberry___Leaf_scorch": "strawberry___leaf_scorch",
    "Strawberry___healthy": "strawberry___healthy",

    # ── PlantVillage — Corn/Maize ──────────────────────────────────────────
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "maize___gray_leaf_spot",
    "Corn_(maize)___Common_rust_": "maize___common_rust",
    "Corn_(maize)___Northern_Leaf_Blight": "maize___northern_leaf_blight",
    "Corn_(maize)___healthy": "maize___healthy",

    # ── PlantVillage — Wheat ───────────────────────────────────────────────
    # (PlantVillage does not have wheat; added via other datasets)

    # ── PlantVillage — Rice ────────────────────────────────────────────────
    # (PlantVillage does not have rice; added via other datasets)

    # ── PlantVillage — Citrus ──────────────────────────────────────────────
    "Citrus___greening": "citrus___greening",
    "Citrus___healthy": "citrus___healthy",

    # ── PlantVillage — Squash ──────────────────────────────────────────────
    "Squash___Powdery_mildew": "squash___powdery_mildew",

    # ── PlantVillage — Peach (not priority, but included if data sufficient)
    "Peach___Bacterial_spot": "peach___bacterial_spot",
    "Peach___healthy": "peach___healthy",

    # ── PlantVillage — Cherry ─────────────────────────────────────────────
    "Cherry_(including_sour)___Powdery_mildew": "cherry___powdery_mildew",
    "Cherry_(including_sour)___healthy": "cherry___healthy",

    # ── PlantVillage — Soybean ────────────────────────────────────────────
    "Soybean___healthy": "soybean___healthy",

    # ── PlantVillage — Raspberry ──────────────────────────────────────────
    "Raspberry___healthy": "raspberry___healthy",

    # ── PlantVillage — Orange ─────────────────────────────────────────────
    "Orange___Haunglongbing_(Citrus_greening)": "citrus___greening",

    # ── PlantVillage — Blueberry ─────────────────────────────────────────
    "Blueberry___healthy": "blueberry___healthy",

    # ── PlantVillage — Apple ──────────────────────────────────────────────
    "Apple___Apple_scab": "apple___apple_scab",
    "Apple___Black_rot": "apple___black_rot",
    "Apple___Cedar_apple_rust": "apple___cedar_apple_rust",
    "Apple___healthy": "apple___healthy",

    # ── External datasets — Wheat ──────────────────────────────────────────
    # (labels to be added when datasets are inspected in Step 2)
    "wheat_healthy": "wheat___healthy",
    "Wheat___Healthy": "wheat___healthy",
    "wheat_loose_smut": "wheat___loose_smut",
    "wheat_crown_root_rot": "wheat___crown_and_root_rot",
    "wheat_leaf_blight": "wheat___leaf_blight",
    "Wheat___Yellow_Rust": "wheat___yellow_rust",
    "Wheat___Brown_Rust": "wheat___brown_rust",
    "Wheat___Septoria": "wheat___septoria",

    # ── External datasets — Rice ───────────────────────────────────────────
    "Healthy": "rice___healthy",  # context-dependent; used only in rice datasets
    "Leaf_Blast": "rice___leaf_blast",
    "Neck_Blast": "rice___neck_blast",
    "Brown_Spot": "rice___brown_spot",
    "Hispa": "rice___hispa",
    "Dead_Heart": "rice___dead_heart",
    "Bacterial_Leaf_Blight": "rice___bacterial_leaf_blight",

    # ── External datasets — Cotton ─────────────────────────────────────────
    "diseased cotton leaf": "cotton___disease",
    "diseased cotton plant": "cotton___disease",
    "fresh cotton leaf": "cotton___healthy",
    "fresh cotton plant": "cotton___healthy",
    "Cotton___Bacterial_Blight": "cotton___bacterial_blight",
    "Cotton___Curl_Virus": "cotton___curl_virus",
    "Cotton___Fussarium_Wilt": "cotton___fusarium_wilt",
    "Cotton___Healthy": "cotton___healthy",

    # ── External datasets — Cucumber ───────────────────────────────────────
    "Cucumber___Diseased": "cucumber___disease",
    "Cucumber___Healthy": "cucumber___healthy",
    "Downy Mildew": "cucumber___downy_mildew",
    "Powdery Mildew": "cucumber___powdery_mildew",
    "Gummy Stem Blight": "cucumber___gummy_stem_blight",

    # ── External datasets — Mango ──────────────────────────────────────────
    "Mango___Anthracnose": "mango___anthracnose",
    "Mango___Bacterial_Canker": "mango___bacterial_canker",
    "Mango___Cutting_Weevil": "mango___cutting_weevil",
    "Mango___Die_Back": "mango___die_back",
    "Mango___Gall_Midge": "mango___gall_midge",
    "Mango___Healthy": "mango___healthy",
    "Mango___Powdery_Mildew": "mango___powdery_mildew",
    "Mango___Sooty_Mould": "mango___sooty_mould",

    # ── Negatives (non-plant / unsupported) ────────────────────────────────
    "unknown": "unknown",
    "background": "unknown",
    "non_plant": "unknown",
}


def normalize(raw_label: str) -> str:
    """Return canonical label for a raw label; unknown if not in map."""
    return RAW_TO_CANONICAL.get(raw_label, "unknown")


def canonical_crop(canonical_label: str) -> str:
    """Extract crop name from canonical label (before the first ___).

    Example: "tomato___early_blight" → "tomato"
    """
    return canonical_label.split("___")[0]


def canonical_condition(canonical_label: str) -> str:
    """Extract condition name from canonical label (after the first ___).

    Example: "tomato___early_blight" → "early_blight"
    """
    parts = canonical_label.split("___", 1)
    return parts[1] if len(parts) > 1 else ""


def all_canonical_labels() -> list[str]:
    """Return all unique canonical labels (excluding duplicates from aliases)."""
    return sorted(set(RAW_TO_CANONICAL.values()))


if __name__ == "__main__":
    labels = all_canonical_labels()
    print(f"Total unique canonical labels: {len(labels)}")
    for lbl in labels:
        print(f"  {lbl}")
