# PROGRESS.md — Egypt Agri Assistant

> Updated after every step. A new chat can continue from PROJECT_SPEC.md + PROGRESS.md + DECISIONS.md alone.

---

## Current status

**Phase:** A — Foundation and data
**Last completed step:** Step 1 — Setup
**Next step:** Step 2 — Get the data

---

## Step log

| Step | Status | Date | Notes |
|------|--------|------|-------|
| Step 1 — Setup | ✅ Done | 2026-10-27 | Folder structure, config, requirements, venv, first commit |
| Step 2 — Get the data | 🔜 Next | — | Need Kaggle token (instructions below) |
| Step 3 — Clean and split | ⏳ Pending | — | After Step 2 |
| Checkpoint A | ⏳ Pending | — | After Step 3 |

---

## Key paths

| Item | Path |
|------|------|
| Virtual environment | `.venv/` |
| Config | `config.py` |
| App entry point | `app/main.py` (created in Step 9) |
| Disease model | `models/model.onnx` (created in Step 8) |
| Soil model | `models/soil_model.joblib` (created in Step 13) |
| Labels | `models/labels.json` |
| Knowledge base | `knowledge/diseases.json` |
| Manifest | `data/manifest.csv` (created in Step 3) |
| Reports | `reports/` |

---

## Commands to resume

```bash
# Activate venv (Windows)
.venv\Scripts\activate

# Activate venv (Linux/Mac)
source .venv/bin/activate

# Install runtime deps
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run app (after Step 9)
uvicorn app.main:app --reload
```

---

## Open problems

- [ ] **Step 2 needs Kaggle API token** — see instructions in `docs/steps/02-data.md` once created.
- [ ] Supported class list empty — will be filled by Step 3 automatically.

---

## Git tags

| Tag | Meaning |
|-----|---------|
| `checkpoint-A` | After Step 3 (Checkpoint A) |
| `checkpoint-B` | After Step 8 (Checkpoint B) |
| `checkpoint-C` | After Step 12 (Checkpoint C) |
| `checkpoint-D` | After Step 14 (Checkpoint D) |
| `checkpoint-E` | After Step 18 (Checkpoint E) |
