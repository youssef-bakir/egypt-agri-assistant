# Inclusion Rule Report

Min train images: 150
Min field/holdout test images: 30

## Supported classes (41)

| Class | Train | Field/Holdout |
|-------|-------|---------------|
| apple___apple_scab | 421 | 93 |
| apple___cedar_apple_rust | 196 | 106 |
| apple___healthy | 1168 | 88 |
| blueberry___healthy | 1043 | 117 |
| cherry___healthy | 585 | 57 |
| citrus___greening | 3907 | 34 |
| cotton___disease | 855 | 63 |
| cotton___healthy | 699 | 65 |
| cucumber___downy_mildew | 856 | 36 |
| cucumber___healthy | 702 | 261 |
| cucumber___powdery_mildew | 790 | 45 |
| grape___black_rot | 820 | 79 |
| grape___healthy | 292 | 75 |
| maize___common_rust | 626 | 389 |
| maize___gray_leaf_spot | 377 | 67 |
| maize___northern_leaf_blight | 666 | 194 |
| mango___anthracnose | 277 | 99 |
| mango___bacterial_canker | 257 | 149 |
| mango___cutting_weevil | 315 | 76 |
| mango___die_back | 405 | 44 |
| mango___gall_midge | 260 | 146 |
| mango___healthy | 317 | 78 |
| mango___powdery_mildew | 238 | 160 |
| mango___sooty_mould | 273 | 102 |
| peach___healthy | 264 | 112 |
| pepper___bacterial_spot | 684 | 83 |
| pepper___healthy | 1037 | 42 |
| potato___early_blight | 703 | 171 |
| potato___late_blight | 702 | 208 |
| raspberry___healthy | 257 | 119 |
| soybean___healthy | 3571 | 66 |
| squash___powdery_mildew | 1274 | 130 |
| strawberry___healthy | 301 | 96 |
| tomato___bacterial_spot | 1465 | 110 |
| tomato___early_blight | 707 | 88 |
| tomato___healthy | 1095 | 52 |
| tomato___late_blight | 1287 | 111 |
| tomato___leaf_mold | 660 | 91 |
| tomato___mosaic_virus | 271 | 54 |
| tomato___septoria_leaf_spot | 1209 | 157 |
| tomato___yellow_leaf_curl_virus | 3768 | 238 |

## Excluded classes (20) — treated as `unknown`

| Class | Train | Field/Holdout | Reason |
|-------|-------|---------------|--------|
| apple___black_rot | 453 | 0 | field 0 < 30 |
| cherry___powdery_mildew | 711 | 0 | field 0 < 30 |
| citrus___black_spot | 100 | 34 | train 100 < 150 |
| citrus___canker | 82 | 35 | train 82 < 150 |
| citrus___healthy | 29 | 8 | train 29 < 150; field 8 < 30 |
| citrus___melanose | 6 | 4 | train 6 < 150; field 4 < 30 |
| grape___esca | 984 | 0 | field 0 < 30 |
| grape___leaf_blight | 749 | 0 | field 0 < 30 |
| maize___healthy | 805 | 0 | field 0 < 30 |
| peach___bacterial_spot | 1572 | 0 | field 0 < 30 |
| potato___healthy | 107 | 0 | train 107 < 150; field 0 < 30 |
| rice___bacterial_leaf_blight | 18 | 7 | train 18 < 150; field 7 < 30 |
| rice___brown_spot | 14 | 8 | train 14 < 150; field 8 < 30 |
| rice___leaf_smut | 22 | 8 | train 22 < 150; field 8 < 30 |
| strawberry___leaf_scorch | 777 | 0 | field 0 < 30 |
| tomato___spider_mites | 1177 | 2 | field 2 < 30 |
| tomato___target_spot | 987 | 0 | field 0 < 30 |
| wheat___healthy | 60 | 14 | train 60 < 150; field 14 < 30 |
| wheat___septoria | 48 | 25 | train 48 < 150; field 25 < 30 |
| wheat___yellow_rust | 120 | 41 | train 120 < 150 |