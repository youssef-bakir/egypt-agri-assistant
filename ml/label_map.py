"""
ml/label_map.py — explicit mapping from raw dataset labels -> canonical crop___condition.

Rules:
- Canonical format:  "crop___condition"  (three underscores, lowercase, underscores for spaces)
- Healthy leaves:    "crop___healthy"
- Unknown/unsupported: "unknown"
- This file is the SINGLE source of truth for label normalization.

Any raw label not in RAW_TO_CANONICAL maps to "unknown" automatically.
"""

from __future__ import annotations

# Raw label (or source::raw_label) -> canonical label
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

    # ── PlantVillage — Citrus ──────────────────────────────────────────────
    "Citrus___greening": "citrus___greening",
    "Citrus___healthy": "citrus___healthy",
    "Orange___Haunglongbing_(Citrus_greening)": "citrus___greening",

    # ── PlantVillage — Squash ──────────────────────────────────────────────
    "Squash___Powdery_mildew": "squash___powdery_mildew",

    # ── PlantVillage — Peach ───────────────────────────────────────────────
    "Peach___Bacterial_spot": "peach___bacterial_spot",
    "Peach___healthy": "peach___healthy",

    # ── PlantVillage — Cherry ──────────────────────────────────────────────
    "Cherry_(including_sour)___Powdery_mildew": "cherry___powdery_mildew",
    "Cherry_(including_sour)___healthy": "cherry___healthy",

    # ── PlantVillage — Soybean ─────────────────────────────────────────────
    "Soybean___healthy": "soybean___healthy",

    # ── PlantVillage — Raspberry ───────────────────────────────────────────
    "Raspberry___healthy": "raspberry___healthy",

    # ── PlantVillage — Blueberry ───────────────────────────────────────────
    "Blueberry___healthy": "blueberry___healthy",

    # ── PlantVillage — Apple ───────────────────────────────────────────────
    "Apple___Apple_scab": "apple___apple_scab",
    "Apple___Black_rot": "apple___black_rot",
    "Apple___Cedar_apple_rust": "apple___cedar_apple_rust",
    "Apple___healthy": "apple___healthy",

    # ── PlantDoc (Field domain) ───────────────────────────────────────────
    "Apple_Scab_Leaf": "apple___apple_scab",
    "Apple_leaf": "apple___healthy",
    "Apple_rust_leaf": "apple___cedar_apple_rust",
    "Bell_pepper_leaf": "pepper___healthy",
    "Bell_pepper_leaf_spot": "pepper___bacterial_spot",
    "Blueberry_leaf": "blueberry___healthy",
    "Cherry_leaf": "cherry___healthy",
    "Corn_Gray_leaf_spot": "maize___gray_leaf_spot",
    "Corn_leaf_blight": "maize___northern_leaf_blight",
    "Corn_rust_leaf": "maize___common_rust",
    "Peach_leaf": "peach___healthy",
    "Potato_leaf_early_blight": "potato___early_blight",
    "Potato_leaf_late_blight": "potato___late_blight",
    "Raspberry_leaf": "raspberry___healthy",
    "Soyabean_leaf": "soybean___healthy",
    "Squash_Powdery_mildew_leaf": "squash___powdery_mildew",
    "Strawberry_leaf": "strawberry___healthy",
    "Tomato_Early_blight_leaf": "tomato___early_blight",
    "Tomato_Septoria_leaf_spot": "tomato___septoria_leaf_spot",
    "Tomato_leaf": "tomato___healthy",
    "Tomato_leaf_bacterial_spot": "tomato___bacterial_spot",
    "Tomato_leaf_late_blight": "tomato___late_blight",
    "Tomato_leaf_mosaic_virus": "tomato___mosaic_virus",
    "Tomato_leaf_yellow_virus": "tomato___yellow_leaf_curl_virus",
    "Tomato_mold_leaf": "tomato___leaf_mold",
    "Tomato_two_spotted_spider_mites_leaf": "tomato___spider_mites",
    "grape_leaf": "grape___healthy",
    "grape_leaf_black_rot": "grape___black_rot",

    # ── Cucumber ───────────────────────────────────────────────────────────
    "Downy_mildew": "cucumber___downy_mildew",
    "Healthy_leaves": "cucumber___healthy",
    "Powdery_mildew": "cucumber___powdery_mildew",
    "cucumber::Downy_mildew": "cucumber___downy_mildew",
    "cucumber::Healthy_leaves": "cucumber___healthy",
    "cucumber::Powdery_mildew": "cucumber___powdery_mildew",
    "Cucumber___Diseased": "cucumber___disease",
    "Cucumber___Healthy": "cucumber___healthy",
    "Downy Mildew": "cucumber___downy_mildew",
    "Powdery Mildew": "cucumber___powdery_mildew",
    "Gummy Stem Blight": "cucumber___gummy_stem_blight",

    # ── Wheat ──────────────────────────────────────────────────────────────
    "wheat::Healthy": "wheat___healthy",
    "wheat::septoria": "wheat___septoria",
    "wheat::stripe_rust": "wheat___yellow_rust",
    "wheat_healthy": "wheat___healthy",
    "Wheat___Healthy": "wheat___healthy",
    "wheat_loose_smut": "wheat___loose_smut",
    "wheat_crown_root_rot": "wheat___crown_and_root_rot",
    "wheat_leaf_blight": "wheat___leaf_blight",
    "Wheat___Yellow_Rust": "wheat___yellow_rust",
    "Wheat___Brown_Rust": "wheat___brown_rust",
    "Wheat___Septoria": "wheat___septoria",

    # ── Rice ───────────────────────────────────────────────────────────────
    "rice::Healthy": "rice___healthy",
    "rice::Bacterial leaf blight": "rice___bacterial_leaf_blight",
    "rice::Brown spot": "rice___brown_spot",
    "rice::Leaf smut": "rice___leaf_smut",
    "Bacterial leaf blight": "rice___bacterial_leaf_blight",
    "Brown spot": "rice___brown_spot",
    "Leaf smut": "rice___leaf_smut",
    "Leaf_Blast": "rice___leaf_blast",
    "Neck_Blast": "rice___neck_blast",
    "Brown_Spot": "rice___brown_spot",
    "Hispa": "rice___hispa",
    "Dead_Heart": "rice___dead_heart",
    "Bacterial_Leaf_Blight": "rice___bacterial_leaf_blight",

    # ── Cotton ─────────────────────────────────────────────────────────────
    "diseased cotton leaf": "cotton___disease",
    "diseased cotton plant": "cotton___disease",
    "fresh cotton leaf": "cotton___healthy",
    "fresh cotton plant": "cotton___healthy",
    "cotton::diseased cotton leaf": "cotton___disease",
    "cotton::diseased cotton plant": "cotton___disease",
    "cotton::fresh cotton leaf": "cotton___healthy",
    "cotton::fresh cotton plant": "cotton___healthy",
    "Cotton___Bacterial_Blight": "cotton___bacterial_blight",
    "Cotton___Curl_Virus": "cotton___curl_virus",
    "Cotton___Fussarium_Wilt": "cotton___fusarium_wilt",
    "Cotton___Healthy": "cotton___healthy",

    # ── Citrus ─────────────────────────────────────────────────────────────
    "citrus::Black spot": "citrus___black_spot",
    "citrus::Canker": "citrus___canker",
    "citrus::Greening": "citrus___greening",
    "citrus::Healthy": "citrus___healthy",
    "citrus::Melanose": "citrus___melanose",
    "Black spot": "citrus___black_spot",
    "Canker": "citrus___canker",
    "Greening": "citrus___greening",
    "Melanose": "citrus___melanose",

    # ── Mango ──────────────────────────────────────────────────────────────
    "mango::Anthracnose": "mango___anthracnose",
    "mango::Bacterial Canker": "mango___bacterial_canker",
    "mango::Cutting Weevil": "mango___cutting_weevil",
    "mango::Die Back": "mango___die_back",
    "mango::Gall Midge": "mango___gall_midge",
    "mango::Healthy": "mango___healthy",
    "mango::Powdery Mildew": "mango___powdery_mildew",
    "mango::Sooty Mould": "mango___sooty_mould",
    "Mango___Anthracnose": "mango___anthracnose",
    "Mango___Bacterial_Canker": "mango___bacterial_canker",
    "Mango___Cutting_Weevil": "mango___cutting_weevil",
    "Mango___Die_Back": "mango___die_back",
    "Mango___Gall_Midge": "mango___gall_midge",
    "Mango___Healthy": "mango___healthy",
    "Mango___Powdery_Mildew": "mango___powdery_mildew",
    "Mango___Sooty_Mould": "mango___sooty_mould",

    # ── Onion / Beans / Peas aliases ──────────────────────────────────────
    "Onion___Healthy": "onion___healthy",
    "Onion___Anthracnose": "onion___anthracnose",
    "Onion___Iris_Yellow_Spot_Virus": "onion___iris_yellow_spot_virus",
    "Onion___Purple_Blotch": "onion___purple_blotch",
    "Onion___Stemphylium_Blight": "onion___stemphylium_blight",
    "Eggplant___Healthy": "eggplant___healthy",
    "Eggplant___Little_Leaf_Disease": "eggplant___little_leaf_disease",
    "Eggplant___Cercospora_Leaf_Spot": "eggplant___cercospora_leaf_spot",
    "Eggplant___Mosaic_Virus": "eggplant___mosaic_virus",
    "Eggplant___White_Mold": "eggplant___white_mold",
    "Bean___Healthy": "beans___healthy",
    "Bean___Angular_Leaf_Spot": "beans___angular_leaf_spot",
    "Bean___Bean_Rust": "beans___bean_rust",
    "Pea___Healthy": "peas___healthy",
    "Pea___Powdery_Mildew": "peas___powdery_mildew",

    # ── Corn aliases ───────────────────────────────────────────────────────
    "corn_healthy": "maize___healthy",
    "corn_common_rust": "maize___common_rust",
    "corn_gray_leaf_spot": "maize___gray_leaf_spot",
    "corn_northern_leaf_blight": "maize___northern_leaf_blight",

    # ── Negatives (non-plant, background, soil) ───────────────────────────
    "unknown": "unknown",
    "background": "unknown",
    "non_plant": "unknown",
    "airplane": "unknown",
    "car": "unknown",
    "cat": "unknown",
    "dog": "unknown",
    "flower": "unknown",
    "fruit": "unknown",
    "motorbike": "unknown",
    "person": "unknown",
    "Black Soil": "unknown",
    "Cinder Soil": "unknown",
    "Laterite Soil": "unknown",
    "Peat Soil": "unknown",
    "Yellow Soil": "unknown",
}


def normalize(raw_label: str, source: str = "") -> str:
    """Return canonical label for a raw label; unknown if not in map.

    If source is provided, checks scoped `source::raw_label` before `raw_label`.
    """
    if source:
        scoped = f"{source}::{raw_label}"
        if scoped in RAW_TO_CANONICAL:
            return RAW_TO_CANONICAL[scoped]
    return RAW_TO_CANONICAL.get(raw_label, "unknown")


def canonical_crop(canonical_label: str) -> str:
    """Extract crop name from canonical label (before the first ___).

    Example: "tomato___early_blight" -> "tomato"
    """
    return canonical_label.split("___")[0]


def canonical_condition(canonical_label: str) -> str:
    """Extract condition name from canonical label (after the first ___).

    Example: "tomato___early_blight" -> "early_blight"
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
