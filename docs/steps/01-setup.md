# الخطوة 01 — الإعداد (Setup)

## ماذا بنينا؟

أنشأنا الهيكل الأساسي للمشروع بالكامل:
- مجلدات المشروع (`ml/`, `soil/`, `app/`, `web/`, `knowledge/`, `models/`, `tests/`, `docs/`)
- ملفات الإعداد (`config.py`, `requirements.txt`, `requirements-train.txt`, `.env.example`, `.gitignore`, `Dockerfile`)
- ملفات التوثيق (`README.md`, `DECISIONS.md`, `PROGRESS.md`)
- بيئة Python افتراضية (`.venv/`)
- اختبارات التدخين الأولية (`tests/test_smoke.py`)

## لماذا؟

قبل أي كود، يجب أن يكون الهيكل واضحاً وكاملاً. هذا يسمح لأي شخص — أو أداة ذكاء اصطناعي — باستمرار العمل من نقطة واضحة.

## كيف تُشغّله؟

```bash
# 1. تفعيل البيئة الافتراضية (Windows)
.venv\Scripts\activate

# 2. تثبيت المتطلبات
pip install -r requirements.txt

# 3. تشغيل الاختبارات
pytest tests/test_smoke.py -v
```

## الأجزاء الأساسية في الكود

1. **`config.py`** — كل الإعدادات من متغيرات البيئة بقيم افتراضية آمنة. أي رقم أو مسار في المشروع يأتي من هنا.
2. **`.env.example`** — قالب لملف `.env` الحقيقي الذي لا يُرفع على git.
3. **`.gitignore`** — يمنع رفع الأسرار (`.env`, `kaggle.json`), البيانات الكبيرة, والنماذج الكبيرة.
4. **`requirements.txt`** — ما يحتاجه الخادم فقط. `requirements-train.txt` يُضاف للتدريب.
5. **`tests/test_smoke.py`** — يتحقق أن الهيكل سليم. يُشغَّل بعد كل خطوة.

## الأخطاء الشائعة

- **نسيت تفعيل البيئة الافتراضية:** ستُثبَّت الحزم على Python العام — شغّل `.venv\Scripts\activate` أولاً.
- **`SECRET_KEY` في الإنتاج:** التطبيق سيرفض البدء إذا `ENV=prod` والـ key هو القيمة الافتراضية.
- **لا ترفع `.env` على git** — يحتوي على أسرار.
