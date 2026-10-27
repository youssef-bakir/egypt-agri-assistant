# الخطوة 02 — الحصول على البيانات

## ماذا بنينا؟

في هذه الخطوة نقوم بتحميل مجموعات البيانات من مصادر مختلفة وبناء فهرس (inventory) يوثّق محتواها.

## ما تحتاجه للتشغيل

### Kaggle API Token (مطلوب)

1. افتح **https://www.kaggle.com** وسجّل الدخول
2. اضغط على صورة حسابك ← **Settings** ← قسم **API** ← **Create New Token**
3. ضع الملف المُنزَّل في: `C:\Users\<اسمك>\.kaggle\kaggle.json`

### HuggingFace (لا يحتاج حساباً للمجموعات العامة)

## كيف تُشغّله؟

```bash
# تفعيل البيئة
.venv\Scripts\activate

# تثبيت أدوات التدريب (تشمل kaggle و huggingface_hub)
pip install -r requirements-train.txt

# تحميل جميع البيانات
python ml/download_datasets.py --data-dir data/raw

# بناء الفهرس
python ml/inventory.py --data-dir data/raw
```

## البيانات المستهدفة

| المجموعة | المصدر | المحاصيل المتوقعة | النوع |
|----------|--------|-----------------|-------|
| PlantVillage (أصلية بالألوان) | Kaggle: abdallahalidev/plantvillage-dataset | طماطم، بطاطس، فلفل، عنب، فراولة، ذرة، حمضيات | مختبر |
| PlantDoc | Kaggle: pratikkayal/plantdoc-dataset | مختلطة | حقلي |
| Multiple Plant Diseases | Kaggle: alinedobrovsky/plant-diseases-classification | خيار، بصل، قمح، أرز | مختلط |
| Cotton Disease | Kaggle: janmejaybhoi/cotton-disease-dataset | قطن | مختبر |
| Mango Leaf Disease | Kaggle: warcoder/mango-leaf-disease-dataset | مانجو | مختبر |
| Citrus Leaves | Kaggle: dtrilsbeek/citrus-leaves | حمضيات | مختبر |
| Rice Leaf Diseases | Kaggle: vbookshelf/rice-leaf-diseases | أرز | مختبر |
| Wheat Disease | Kaggle: haidershabbirawan/wheat-disease-dataset | قمح | مختبر |
| Cucumber Real-World | Kaggle: kareem25/cucumber-leaves-disease | خيار | حقلي |

## الأجزاء الأساسية في الكود

1. **`ml/label_map.py`** — يحوّل التسميات الخام من كل مجموعة بيانات إلى تنسيق موحّد: `"crop___condition"`
2. **`ml/download_datasets.py`** — يُنزِّل كل مجموعة بيانات بالـ CLI تلقائياً
3. **`ml/inventory.py`** — يمشي على كل الصور ويُنتج `reports/inventory.md`
4. **`reports/inventory.md`** — يوثّق العدد الفعلي لكل فئة من كل مصدر (الأرقام الحقيقية)

## الأخطاء الشائعة

- **401 Unauthorized من Kaggle:** تأكد أن `kaggle.json` في المسار الصحيح: `C:\Users\<اسمك>\.kaggle\`
- **بيانات ناقصة:** `ml/download_datasets.py` يُبلّغ بوضوح عن كل مجموعة فشل تحميلها
- **لا ترفع مجلد `data/` على git** — مُدرج في `.gitignore`
