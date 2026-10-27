# Egypt Agri Assistant — مساعد المزارع المصري

> **موقع ثنائي اللغة للتشخيص الزراعي** يساعد المزارع المصري على:
> - تشخيص أمراض النباتات من صورة ورقة واحدة
> - الحصول على توصية بأفضل المحاصيل بناءً على بيانات التربة والمناخ

---

## What it does

| Feature | Description |
|---------|-------------|
| 🌿 Plant Disease Diagnosis | Upload/photograph a leaf → get crop, disease, confidence, symptoms, actions, and sourced pesticide guidance |
| 🌱 Soil & Crop Advisor | Enter soil/climate values → best crops to grow, with "why" for each input |
| 👤 User Accounts | Register/login to save diagnosis history and soil analyses |
| 📜 History | View and delete past scans and analyses |

## Supported crops (decided automatically in Step 3 — see reports/inventory.md)

> TODO: list will be filled after data collection and cleaning (Step 3).

## Architecture

```
egypt-agri-assistant/
├── app/           FastAPI backend (routers → services → db)
├── ml/            Disease model scripts (label_map, train, evaluate, export)
├── soil/          Soil model scripts
├── web/           Static HTML + CSS + JS (no framework, no build step)
├── knowledge/     Bilingual JSON knowledge base (diseases, soil crops)
├── models/        Trained artifacts (NOT in git if > 50 MB)
├── reports/       Auto-generated evaluation reports
├── tests/         pytest test suite
└── docs/          All documentation
```

## Quick start

```bash
# 1. Clone
git clone https://github.com/youssef-bakir/egypt-agri-assistant.git
cd egypt-agri-assistant

# 2. Create virtual environment (Python 3.11 required)
py -3.11 -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/Mac
# Edit .env as needed

# 5. Run
uvicorn app.main:app --reload

# 6. Open http://localhost:8000
```

## Run tests

```bash
pytest tests/ -v
```

## Retraining the disease model

See `docs/steps/04-training.md` (created in Step 4).

## Adding a crop

See `docs/EXTENDING.md`.

## Honest limits

- No real Egyptian farm photos were used for training; real-farm accuracy may differ.
- The soil advisor uses a clean research dataset; treat its output as a starting point.
- Always consult a licensed agricultural engineer before applying any pesticide.

## License

Educational use only. Data licenses vary by source (see `docs/DATA.md`).
