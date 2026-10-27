# Dataset Inventory Report

Generated automatically by `ml/inventory.py`.

## Summary

| Metric | Count |
|--------|-------|
| Total files found | 190,990 |
| Augmented/derivative copies (flagged for exclusion) | 108,611 |
| Active original images | 82,379 |
| Corrupt files | 0 |
| Lab images (active) | 54,305 |
| Field images (active) | 14,120 |
| Negatives (active) | 13,954 |

## Per-source counts (Original Active Images)

| Source | Images | Domain |
|--------|--------|--------|
| plantvillage | 54,305 | lab |
| negatives | 13,798 | negatives |
| mango | 4,000 | field |
| cucumber | 3,754 | field |
| plantdoc | 2,922 | field |
| cotton | 2,310 | field |
| citrus | 607 | field |
| wheat | 407 | field |
| negatives_soil | 156 | negatives |
| rice | 120 | field |

## Per-class counts (canonical labels, Active Images)

| Canonical Class | Total | Crop | Field Images | Lab Images |
|-----------------|-------|------|--------------|------------|
| `unknown` | 13,954 | unknown | 0 | 0 |
| `citrus___greening` | 5,711 | citrus | 204 | 5,507 |
| `tomato___yellow_leaf_curl_virus` | 5,595 | tomato | 238 | 5,357 |
| `soybean___healthy` | 5,155 | soybean | 65 | 5,090 |
| `peach___bacterial_spot` | 2,297 | peach | 0 | 2,297 |
| `tomato___bacterial_spot` | 2,237 | tomato | 110 | 2,127 |
| `tomato___late_blight` | 2,020 | tomato | 111 | 1,909 |
| `squash___powdery_mildew` | 1,965 | squash | 130 | 1,835 |
| `tomato___septoria_leaf_spot` | 1,928 | tomato | 157 | 1,771 |
| `apple___healthy` | 1,733 | apple | 88 | 1,645 |
| `tomato___spider_mites` | 1,678 | tomato | 2 | 1,676 |
| `tomato___healthy` | 1,643 | tomato | 52 | 1,591 |
| `blueberry___healthy` | 1,619 | blueberry | 117 | 1,502 |
| `pepper___healthy` | 1,520 | pepper | 42 | 1,478 |
| `tomato___target_spot` | 1,404 | tomato | 0 | 1,404 |
| `grape___esca` | 1,383 | grape | 0 | 1,383 |
| `maize___common_rust` | 1,309 | maize | 117 | 1,192 |
| `cucumber___downy_mildew` | 1,307 | cucumber | 1,307 | 0 |
| `cotton___disease` | 1,277 | cotton | 1,277 | 0 |
| `grape___black_rot` | 1,259 | grape | 79 | 1,180 |
| `cucumber___healthy` | 1,246 | cucumber | 1,246 | 0 |
| `potato___late_blight` | 1,208 | potato | 208 | 1,000 |
| `cucumber___powdery_mildew` | 1,201 | cucumber | 1,201 | 0 |
| `maize___northern_leaf_blight` | 1,179 | maize | 194 | 985 |
| `potato___early_blight` | 1,171 | potato | 171 | 1,000 |
| `maize___healthy` | 1,162 | maize | 0 | 1,162 |
| `strawberry___leaf_scorch` | 1,109 | strawberry | 0 | 1,109 |
| `tomato___early_blight` | 1,088 | tomato | 88 | 1,000 |
| `pepper___bacterial_spot` | 1,080 | pepper | 83 | 997 |
| `grape___leaf_blight` | 1,076 | grape | 0 | 1,076 |
| `cherry___powdery_mildew` | 1,052 | cherry | 0 | 1,052 |
| `tomato___leaf_mold` | 1,043 | tomato | 91 | 952 |
| `cotton___healthy` | 1,033 | cotton | 1,033 | 0 |
| `cherry___healthy` | 911 | cherry | 57 | 854 |
| `apple___apple_scab` | 723 | apple | 93 | 630 |
| `apple___black_rot` | 621 | apple | 0 | 621 |
| `maize___gray_leaf_spot` | 580 | maize | 67 | 513 |
| `strawberry___healthy` | 552 | strawberry | 96 | 456 |
| `mango___anthracnose` | 500 | mango | 500 | 0 |
| `mango___bacterial_canker` | 500 | mango | 500 | 0 |
| `mango___cutting_weevil` | 500 | mango | 500 | 0 |
| `mango___die_back` | 500 | mango | 500 | 0 |
| `mango___gall_midge` | 500 | mango | 500 | 0 |
| `mango___healthy` | 500 | mango | 500 | 0 |
| `mango___powdery_mildew` | 500 | mango | 500 | 0 |
| `mango___sooty_mould` | 500 | mango | 500 | 0 |
| `grape___healthy` | 498 | grape | 75 | 423 |
| `raspberry___healthy` | 490 | raspberry | 119 | 371 |
| `peach___healthy` | 472 | peach | 112 | 360 |
| `tomato___mosaic_virus` | 427 | tomato | 54 | 373 |
| `apple___cedar_apple_rust` | 381 | apple | 106 | 275 |
| `wheat___yellow_rust` | 208 | wheat | 208 | 0 |
| `citrus___black_spot` | 169 | citrus | 169 | 0 |
| `citrus___canker` | 163 | citrus | 163 | 0 |
| `potato___healthy` | 152 | potato | 0 | 152 |
| `wheat___healthy` | 102 | wheat | 102 | 0 |
| `wheat___septoria` | 97 | wheat | 97 | 0 |
| `citrus___healthy` | 58 | citrus | 58 | 0 |
| `rice___bacterial_leaf_blight` | 40 | rice | 40 | 0 |
| `rice___brown_spot` | 40 | rice | 40 | 0 |
| `rice___leaf_smut` | 40 | rice | 40 | 0 |
| `citrus___melanose` | 13 | citrus | 13 | 0 |

## Imbalance Analysis

- Largest plant class: `citrus___greening` (5,711 images)
- Smallest plant class: `citrus___melanose` (13 images)
- Class imbalance ratio: 439.3x
- Negatives / Unknown count: 13,954 images