# الخطوة 02 — الحصول على البيانات (Data Collection & Inventory)

## ماذا بنينا وأنجزنا؟

في هذه الخطوة تم تحميل وفهرسة مجموعات البيانات من مصادر حقيقية عبر Kaggle CLI، ثم توحيد التسميات (Label Mapping) وفحص الصور وإصدار تقرير الجرد الشامل `reports/inventory.md`.

## الأرقام الحقيقية للبيانات المجمعة (من الكود الفعلي)

- **إجمالي الملفات المفحوصة:** 190,990 ملف
- **النسخ المشتقة والمكررة المستبعدة (Augmented/Grayscale/Segmented):** 108,611 ملف (تم استبعاد نسخ Grayscale و Segmented من PlantVillage وفقاً لقواعد المشروع D4 والقسم 6)
- **الصور الأصلية النشطة (Active Original Images):** 82,379 صورة
- **صور المختبر (Lab):** 54,305 صورة (PlantVillage الأصلية الملونة)
- **صور الحقل الحقيقية (Field):** 14,120 صورة (PlantDoc, Cucumber, Cotton, Mango, Wheat, Citrus, Rice)
- **الصور السلبية (Negatives / Background / Soil):** 13,954 صورة

## مصادر البيانات الفعلية على القرص

| المصدر | المعرّف (Dataset ID) | إجمالي الصور النشطة | المجال (Domain) |
|--------|---------------------|--------------------|-----------------|
| `plantvillage` | `abdallahalidev/plantvillage-dataset` | 54,305 | مختبر (Lab) |
| `negatives` | `prasunroy/natural-images` | 13,798 | صور سلبية غير نباتية |
| `mango` | `warcoder/mango-leaf-disease-dataset` | 4,000 | حقل (Field) |
| `cucumber` | `kaushigihanml/cucumber-leaf-disease-dataset` | 3,754 | حقل (Field) |
| `plantdoc` | `nirmalsankalana/plantdoc-dataset` | 2,922 | حقل (Field) |
| `cotton` | `janmejaybhoi/cotton-disease-dataset` | 2,310 | حقل (Field) |
| `citrus` | `myprojectdictionary/citrus-leaf-disease-image` | 607 | حقل (Field) |
| `wheat` | `olyadgetch/wheat-leaf-dataset` | 407 | حقل (Field) |
| `negatives_soil` | `prasanshasatpathy/soil-types` | 156 | تربة سلبية |
| `rice` | `vbookshelf/rice-leaf-diseases` | 120 | حقل (Field) |

## الأجزاء البرمجية المنجزة

1. **`ml/label_map.py`**:
   - قاموس صريح وشامل يربط أسماء المجلدات الخام بالتسميات المعيارية بصيغة `crop___condition`
   - يدعم التسميات المقيدة بالمصدر (`source::label`) لحل أي تعارض في أسماء الفئات المشتركة مثل `Healthy`
   - ربط الصور غير النباتية بفئة `unknown`

2. **`ml/inventory.py`**:
   - مسح ذكي لجميع المجلدات الفرعية
   - كشف النسخ المعالجة والمكررة واستبعادها تلقائياً
   - إنتاج التقرير التفصيلي `reports/inventory.md` بأعداد كل فئة ومصدر ونطاق

3. **اختبارات الوحدة**:
   - `tests/test_label_map.py` اجتاز 8/8 اختبارات بنجاح
