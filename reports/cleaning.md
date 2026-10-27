# Label Noise Cleaning Report

Generated automatically by `ml/clean_labels.py` using out-of-fold cross-validation.

## Summary

- Total training images examined: 44,706
- Noise threshold: 0.9
- Max removal cap per class: 20%
- Total flagged as noisy: 286
- Total removed after cap: 285
- Contact sheets generated in: `reports/contact_sheets/`

## Per-class Cleaning Breakdown

| Class | Total | Flagged | Removed | Removal Rate |
|-------|-------|---------|---------|--------------|
| `apple___apple_scab` | 426 | 5 | 5 | 1.2% |
| `apple___black_rot` | 457 | 4 | 4 | 0.9% |
| `apple___cedar_apple_rust` | 198 | 2 | 2 | 1.0% |
| `apple___healthy` | 1,175 | 7 | 7 | 0.6% |
| `blueberry___healthy` | 1,048 | 5 | 5 | 0.5% |
| `cherry___healthy` | 592 | 7 | 7 | 1.2% |
| `cherry___powdery_mildew` | 727 | 16 | 16 | 2.2% |
| `citrus___black_spot` | 102 | 2 | 2 | 2.0% |
| `citrus___canker` | 94 | 12 | 12 | 12.8% |
| `citrus___greening` | 3,926 | 19 | 19 | 0.5% |
| `citrus___healthy` | 29 | 0 | 0 | 0.0% |
| `citrus___melanose` | 6 | 0 | 0 | 0.0% |
| `cotton___disease` | 861 | 6 | 6 | 0.7% |
| `cotton___healthy` | 704 | 5 | 5 | 0.7% |
| `cucumber___downy_mildew` | 878 | 22 | 22 | 2.5% |
| `cucumber___healthy` | 705 | 3 | 3 | 0.4% |
| `cucumber___powdery_mildew` | 811 | 21 | 21 | 2.6% |
| `grape___black_rot` | 822 | 2 | 2 | 0.2% |
| `grape___esca` | 985 | 1 | 1 | 0.1% |
| `grape___healthy` | 295 | 3 | 3 | 1.0% |
| `grape___leaf_blight` | 749 | 0 | 0 | 0.0% |
| `maize___common_rust` | 626 | 0 | 0 | 0.0% |
| `maize___gray_leaf_spot` | 381 | 4 | 4 | 1.0% |
| `maize___healthy` | 806 | 1 | 1 | 0.1% |
| `maize___northern_leaf_blight` | 667 | 1 | 1 | 0.1% |
| `mango___anthracnose` | 279 | 2 | 2 | 0.7% |
| `mango___bacterial_canker` | 257 | 0 | 0 | 0.0% |
| `mango___cutting_weevil` | 316 | 1 | 1 | 0.3% |
| `mango___die_back` | 405 | 0 | 0 | 0.0% |
| `mango___gall_midge` | 263 | 3 | 3 | 1.1% |
| `mango___healthy` | 318 | 1 | 1 | 0.3% |
| `mango___powdery_mildew` | 242 | 4 | 4 | 1.7% |
| `mango___sooty_mould` | 280 | 7 | 7 | 2.5% |
| `peach___bacterial_spot` | 1,581 | 9 | 9 | 0.6% |
| `peach___healthy` | 265 | 1 | 1 | 0.4% |
| `pepper___bacterial_spot` | 706 | 22 | 22 | 3.1% |
| `pepper___healthy` | 1,050 | 13 | 13 | 1.2% |
| `potato___early_blight` | 705 | 2 | 2 | 0.3% |
| `potato___healthy` | 107 | 0 | 0 | 0.0% |
| `potato___late_blight` | 704 | 2 | 2 | 0.3% |
| `raspberry___healthy` | 259 | 2 | 2 | 0.8% |
| `rice___bacterial_leaf_blight` | 20 | 2 | 2 | 10.0% |
| `rice___brown_spot` | 17 | 4 | 3 | 17.6% |
| `rice___leaf_smut` | 25 | 3 | 3 | 12.0% |
| `soybean___healthy` | 3,573 | 2 | 2 | 0.1% |
| `squash___powdery_mildew` | 1,274 | 0 | 0 | 0.0% |
| `strawberry___healthy` | 304 | 3 | 3 | 1.0% |
| `strawberry___leaf_scorch` | 787 | 10 | 10 | 1.3% |
| `tomato___bacterial_spot` | 1,468 | 3 | 3 | 0.2% |
| `tomato___early_blight` | 708 | 1 | 1 | 0.1% |
| `tomato___healthy` | 1,095 | 0 | 0 | 0.0% |
| `tomato___late_blight` | 1,302 | 15 | 15 | 1.2% |
| `tomato___leaf_mold` | 662 | 2 | 2 | 0.3% |
| `tomato___mosaic_virus` | 271 | 0 | 0 | 0.0% |
| `tomato___septoria_leaf_spot` | 1,216 | 7 | 7 | 0.6% |
| `tomato___spider_mites` | 1,179 | 2 | 2 | 0.2% |
| `tomato___target_spot` | 989 | 2 | 2 | 0.2% |
| `tomato___yellow_leaf_curl_virus` | 3,773 | 5 | 5 | 0.1% |
| `wheat___healthy` | 61 | 1 | 1 | 1.6% |
| `wheat___septoria` | 54 | 6 | 6 | 11.1% |
| `wheat___yellow_rust` | 121 | 1 | 1 | 0.8% |