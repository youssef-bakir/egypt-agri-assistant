# الخطوة 03 — التنظيف والتقسيم

## ماذا بنينا؟

بعد تحميل البيانات، نقوم بثلاث عمليات:

1. **حذف النسخ المكررة:** نحسب dHash (بصمة رقمية) لكل صورة ونُجمّع الصور المتشابهة في مجموعات
2. **تنظيف التسميات الخاطئة:** نُدرِّب نموذجاً سريعاً (K-fold) ونحذف الصور التي يختلف فيها النموذج مع تسميتها بثقة عالية
3. **التقسيم العادل:** train/val/test بالنسبة 70/15/15 — بحيث لا تظهر نفس الصورة في أكثر من قسم

## قاعدة الإدراج (Inclusion Rule)

محصول/فئة مدعومة فقط إذا:
- **≥ 150** صورة تدريب (بعد التنظيف)
- **≥ 30** صورة في مجموعات الاختبار الحقلية

المحاصيل دون بيانات كافية **لا تُختلق** — تُعامَل كـ `unknown` وتُذكر في README.

## كيف تُشغّله؟

```bash
# 1. تجميع النسخ المكررة وتقسيم البيانات
python ml/dedup_split.py --data-dir data/raw --output data/manifest.csv

# 2. تنظيف التسميات الخاطئة (يحتاج PyTorch — على ماكينة التدريب)
python ml/clean_labels.py --manifest data/manifest.csv --output data/manifest_clean.csv

# 3. تطبيق قاعدة الإدراج وتحديث config.py
python ml/apply_inclusion_rule.py --manifest data/manifest_clean.csv
```

## الأجزاء الأساسية

1. **`ml/dedup_split.py`** — يحسب dHash لكل صورة، يُجمّع بـ union-find، يُقسّم بالنسبة المطلوبة
2. **`ml/clean_labels.py`** — يستخدم out-of-fold predictions لاكتشاف الصور ذات التسمية الخاطئة
3. **`ml/apply_inclusion_rule.py`** — يطبّق القاعدة ويُعدّل `config.py` تلقائياً
4. **`data/manifest.csv`** — الفهرس الكامل: path, label, source, domain, split, group_id

## الأخطاء الشائعة

- **نفس group_id في train وtest:** خطأ فادح — الاختبارات تتحقق من ذلك
- **source_holdout في train:** ممنوع — الاختبارات تتحقق من ذلك
- **N/A في field images:** إذا لم يكن هناك صور حقلية كافية، سيُستبعد المحصول تلقائياً
