# PROJECT_SPEC.md — Egypt Agri Assistant (مساعد المزارع المصري)

> You are an AI coding agent. This file is the single source of truth. Follow it strictly.
> The owner is a CS student (Egyptian Arabic speaker) who wants to do **as little manual work as possible** but still understand and be able to explain the project. You do the work; he supervises at checkpoints.

---

## 0. How you work (read first, apply always)

### 0.1 Autopilot
1. **Do everything that can be automated yourself** using the terminal: create folders/files, install packages, download datasets (Kaggle CLI, `huggingface_hub`, `git`), run tests, train (via Kaggle CLI, see Step 5), build Docker, commit, push. Never ask me to do something you can do.
2. **Run steps continuously inside a phase.** Stop ONLY when: (a) you reach a **checkpoint**, (b) you hit a blocking problem you could not fix after 2 serious attempts, or (c) you need something only I can provide (a login, a token, a click in a website).
3. **When you need me to do something**, give exact click-by-click instructions in simple Arabic (what to open, what to click, what to paste back), keep it to the minimum, and wait.
4. **Resumability:** after every step update `PROGRESS.md` (done / next / key paths / commands to resume / open problems). A brand new chat, or another tool, must be able to continue from `PROJECT_SPEC.md` + `PROGRESS.md` + `DECISIONS.md` alone.
5. **Quota awareness:** my AI quota is limited. Don't loop, don't re-read big files needlessly, run heavy work as scripts, and keep chat messages short.

### 0.2 Quality rules
6. **Never invent anything:** numbers, dataset sizes, accuracy, sources, agronomy facts. Every number in a document comes from code you ran. Unknown -> write `TODO` and say so.
7. **Keep code simple:** Python 3.11, type hints, English names, short English comments, functions under ~40 lines, one responsibility per file, no clever tricks.
8. **Only the libraries in section 4.** If you truly need another, explain in one line and add it to `DECISIONS.md`; ask me only if it changes the architecture.
9. **Tests:** every step with logic adds pytest tests; a step is not done while tests fail.
10. **Robustness:** validate inputs, handle expected failures with stable error codes, log errors with context, never swallow exceptions, never return stack traces to users.
11. **Security:** no secrets in git (use `.env`, add it to `.gitignore`), never print tokens, never trust uploaded files, never use `innerHTML` with server data.
12. **Safety of my computer:** work only inside the project folder; no destructive commands (`rm -rf`, force-push, deleting outside the project); ask before installing anything system-wide.

### 0.3 Documentation and understanding (cheap for me)
13. After each step write a **short** `docs/steps/NN-name.md` in simple Arabic: what we built, why, how to run it, the 3-5 key code parts, common mistakes.
14. Record each decision in `DECISIONS.md`: Problem / Options / Choice / Evidence (a real number or a design reason) / Why not the others.
15. **At each checkpoint** write `docs/checkpoints/X.md` in simple Arabic: a one-page summary, the real results, a "what to look at" list, and **5 questions** to test my understanding with the answers hidden in a separate section. Then stop and wait for me to say `continue`. If I say `skip questions`, continue without them.

### 0.4 Git and GitHub
16. The repository name is **`egypt-agri-assistant`**, default branch `main`. If `origin` is not configured yet, ask me ONCE for the repo URL (I create an empty repo on github.com).
17. Commit after every step with messages like `step-03: cross-dataset dedup + split`, `git push` after each commit, and tag each checkpoint (`checkpoint-A`, ...). Never commit data, `.onnx`, large files, or secrets (`.gitignore`). Large model files: document where they live (see Step 17), do not push them to git unless under 50 MB and I agree.

---

## 1. Product

A bilingual website (**Arabic by default RTL, full English LTR, switch anytime**) with:

1. **Plant disease diagnosis** (`/diagnose`): upload/take a photo of one leaf -> crop + disease (or healthy), calibrated confidence, top-3, or an honest `uncertain` / `not_supported` / `bad_quality`. Shows symptoms, cultural actions, and **pesticide guidance** (see D8).
2. **Soil and crop advisor** (`/soil`): enter soil and climate values -> best crops to grow with probabilities and "why" (see D13). A separate page with its own model.
3. **Accounts** (`/register`, `/login`, logout): users have accounts; logged-in users get history of scans and saved soil analyses. Guests can use diagnosis and the soil page without saving anything.
4. **History** (`/history`) for logged-in users.

Pages: `index.html` (home), `diagnose.html`, `soil.html`, `history.html`, `login.html`, `register.html`.

**Core principle:** an honest "I'm not sure, retake the photo" beats a confident wrong answer.

**Disease coverage — Egyptian priority list** (final list decided automatically in Step 3):
vegetables: tomato, potato, cucumber, pepper, eggplant, onion, squash/zucchini, peas/beans; field crops: wheat, maize, rice, cotton; fruits: grape, citrus, strawberry, mango.

**Inclusion rule (automatic):** a crop/class is supported only if, after cleaning and de-duplication, it has at least ~150 training images and at least ~30 field-style images in a held-out test set. Crops without enough data are NOT faked: their leaves are treated as `unknown`, and the README states honestly which crops are missing.

**Out of v1** (the architecture must make them easy to add later): weather integration, severity estimation, object detection, chatbot, email/SMS, payments, native app, admin dashboard, password reset by email.

---

## 2. Honest accuracy (disease model)

Four separate test sets, always reported separately, never merged into one flattering number:

| Test set | Meaning |
|---|---|
| `lab_test` | easy lab-style images (leak-free split) — reported, not a success metric |
| `field_test` | field/in-the-wild images from the field datasets' own test splits; never used for training, tuning, or thresholds |
| `source_holdout` | at least one whole field dataset excluded from training and used only for testing |
| `negative_test` | non-plant / unsupported images |

Targets (report honestly, never edit data to hit them): rejection of `negative_test` >= 95%; CPU latency per image <= 500 ms after warm-up; ONNX file <= 50 MB; full server memory <= 450 MB; ECE reported before/after calibration; field top-1/top-3 and macro-F1 reported per class.
**Per-class reliability:** any class with field recall < 60% is marked `low_reliability` in `models/class_reliability.json`, and the UI shows a warning for it.
Lab accuracy will be much higher than field accuracy; explain this gap in the docs instead of hiding it. Also state clearly that no photos taken on Egyptian farms were used, so real-farm performance may differ.

---

## 3. Architecture and extensibility

- Backend split into **routers** (HTTP only), **services** (logic, no HTTP), **db** (storage). API versioned under `/api/v1`.
- Each feature is a module: router + service + tables + page + translations + tests. Adding a new feature must not require changing the diagnosis code.
- Feature switches in `config.py` (e.g. `FEATURE_SOIL = True`, `FEATURE_FEEDBACK = True`).
- All settings from environment variables with safe dev defaults: `DATABASE_URL`, `SECRET_KEY`, `DATA_DIR`, `ENV` (`dev`/`prod`).
- Write `docs/EXTENDING.md`: how to add a crop, a language, a feature module, and how to move from SQLite to PostgreSQL.

---

## 4. Fixed tech stack

Python 3.11 everywhere; web pages in plain HTML + CSS + JavaScript (ES modules allowed, no framework, no build step, no CDN, no external fonts).

- Disease model: `torch`, `torchvision`, `timm`, `numpy`, `Pillow`, `scikit-learn`, `matplotlib`; serving with `onnxruntime`, export with `onnx`.
- Soil model: `scikit-learn`, `pandas` (training only), `joblib`.
- Backend: `fastapi`, `uvicorn`, `python-multipart`, `pydantic`, `sqlalchemy` (2.x), `argon2-cffi`, `itsdangerous`.
- Data tools (training machine only): `kaggle`, `huggingface_hub`.
- Tests: `pytest`, `httpx`.
- Training scripts are plain `.py` (not notebooks).

`requirements.txt` = what the running app needs only (fastapi, uvicorn, python-multipart, pydantic, sqlalchemy, argon2-cffi, itsdangerous, onnxruntime, scikit-learn, joblib, numpy, Pillow). `requirements-train.txt` = training extras. Pin exact versions after the first successful install.

**Forbidden:** React/Vue/Tailwind/Bootstrap, Flask/Django, Celery/Redis, a separate DB server in v1, docker-compose, TensorFlow, OpenCV (use Pillow+numpy), LLM API calls, YOLO/ultralytics inside the product.

---

## 5. Decisions already made (write each into DECISIONS.md with Arabic explanation)

- **D1 Classification** of one leaf photo -> crop+condition (detection needs box labels most datasets lack).
- **D2 Pretrained backbone + fine-tuning**, not from scratch: better accuracy with less data/time.
- **D3 No YOLO in the product** (task is single-image classification; YOLO needs boxes). An optional offline comparison (Step 7b) gives me numbers for my mentor.
- **D4 Data = lab + field + negatives**; lab-only data gives fake accuracy because models learn backgrounds.
- **D5 Unknown handling inside the pipeline:** explicit `unknown` class + temperature-scaled confidence threshold + image-quality gate. No "green pixel" hacks.
- **D6 ONNX Runtime serving**; model loaded and warmed up at startup, never lazily.
- **D7 FastAPI + static files**, one Python service.
- **D8 Pesticide guidance policy.** Show *recommended active ingredients* (المادة الفعالة) and cultural/preventive actions, never invented. Rules: (a) every chemical recommendation needs a `source` (title + URL) from an official or recognized agricultural source (Egyptian Ministry of Agriculture / Agricultural Research Center bulletins, Egypt's pesticide committee lists, FAO, university extension services); no source -> do not show it; (b) do not recommend an ingredient that is banned in Egypt; if you cannot verify its status, leave it out; (c) numeric doses only if a cited source states them, otherwise write "follow the dose on the product label"; (d) always show safety lines: protective equipment, pre-harvest interval, never exceed the label, keep away from children/water, rotate modes of action; (e) for viral diseases state that chemicals do not cure the plant and show vector/hygiene control; (f) every entry has `reviewed: false` and the UI shows a translated notice "informational only — consult an agricultural engineer".
- **D9 Database:** SQLAlchemy 2.x + SQLite in v1; `DATABASE_URL` switches to PostgreSQL later. Tables are created at startup; add Alembic only when we first change an existing table (explain to me then). Reviewed knowledge stays in JSON files, dynamic data in the DB.
- **D10 Bilingual:** all UI text in `web/i18n/ar.json` and `en.json` with identical keys (a test enforces it). The API returns **codes**, never display sentences. Knowledge and crop names stored as `{ar, en}`. Language switch flips `lang`/`dir`, is remembered in `localStorage`, and the browser language is respected on first visit. Use logical CSS properties (`margin-inline-start`, `text-align: start`).
- **D11 Modular & versioned** (section 3).
- **D12 Authentication:** username + password (no email in v1). Passwords hashed with **argon2id**; server-side signed cookie session (`HttpOnly`, `SameSite=Lax`, `Secure` when `ENV=prod`) storing only the user id; rotate the session on login; logout clears it; login throttling (5 failures / 15 minutes per username+IP, stored in memory or DB); generic error messages (don't reveal whether a username exists); password min 8 chars; username 3-30 chars `[a-zA-Z0-9_.]`; CSRF defense = SameSite + required custom header (`X-Requested-With: fetch`) on every state-changing request; `SECRET_KEY` required in prod; `DELETE /api/v1/auth/me` deletes the account and all its data (scans, soil analyses, photos). Roles: `is_admin` column exists, no admin UI in v1; `scripts/create_admin.py` creates an admin.
- **D13 Soil advisor design:** a RandomForest (or gradient-boosting) classifier from `scikit-learn` on a public crop-recommendation dataset (N, P, K, pH, temperature, humidity, rainfall -> crop; the common Kaggle "Crop Recommendation Dataset" with 22 crops is the first candidate; first search for a better dataset that includes Egyptian crops like wheat/potato/tomato/cucumber). Known problems you MUST handle and document honestly: (1) that dataset is very clean, so its ~99% accuracy is not real-world accuracy — report cross-validation, but never present it as field accuracy; (2) it contains crops not grown in Egypt and lacks many that are (wheat, potato, tomato, cucumber, onion) — keep only crops relevant to Egypt, list exactly which crops are covered on the page; (3) Egypt farming is irrigated, so the "rainfall" input must be presented as "annual water supply including irrigation (mm)" — explain this in the docs; (4) N/P/K units must be defined clearly on the form with help text (check what the dataset's numbers actually mean, do not guess). Besides the top-3 probabilities, show **why**: for each input, whether it is inside or outside the typical range of that crop in the training data, with warnings. The page says it is an estimate and a lab soil test + agricultural engineer are needed for decisions.

---

## 6. Data for the disease model (you do it automatically)

Candidate sources (verify each exists, how to download it by CLI, its real classes and counts; report what failed): PlantVillage (ORIGINAL color images, never an augmented copy); PlantDoc; PlantWild (v1/v2, Hugging Face); PlantSeg (image-level labels only); Kaggle "Multiple Plant Diseases" (includes cucumber, onion, potato, tomato, wheat, corn, rice, capsicum); a cucumber real-world dataset (Mendeley); cotton, wheat, rice, citrus and mango leaf datasets (Mendeley/Kaggle, originals only); negatives from any large non-plant image set.

Automatic hygiene (no work for me):
1. Remove augmented copies (names/folders with `aug`, rotated/flipped duplicates).
2. Near-duplicate grouping across ALL datasets with a perceptual hash (implement dHash yourself with Pillow+numpy).
3. **Automatic label-noise cleaning:** train a quick model with cross-validation (or out-of-fold predictions), flag images where the model confidently disagrees with the label, remove them (cap the removed share per class, log counts in `reports/cleaning.md`). Also save a small contact sheet per class as a PNG; looking at them is optional for me.
4. Tag every image with `domain` (lab/field) and `source`; record each dataset's source URL in `docs/DATA.md`.
5. Negatives must include: random non-plant objects/scenes; non-leaf field content (soil, hands, fruit only, tools, whole fields); leaves of unsupported crops. Roughly as many as an average class (up to ~3,000).
6. To save my disk and time, resize images to a max side of ~320 px during preparation and keep the originals out of the repo. Prefer running data preparation inside Kaggle when downloads are large.

---

## 7. Repository layout (create when a step needs it)

```
egypt-agri-assistant/
├── PROJECT_SPEC.md  PROGRESS.md  DECISIONS.md  README.md  MODEL_CARD.md
├── config.py  requirements.txt  requirements-train.txt  Dockerfile  .env.example  .gitignore
├── ml/            # disease model: label_map, inventory, dedup_split, clean_labels, preprocess,
│                  #   train, benchmark, calibrate, evaluate, export_onnx
├── soil/          # soil model: prepare_data.py, train.py, evaluate.py
├── app/
│   ├── main.py  schemas.py
│   ├── api/v1/    # auth.py diagnose.py soil.py history.py feedback.py health.py classes.py
│   ├── services/  # inference.py quality.py knowledge.py soil_advisor.py auth.py
│   └── db/        # base.py models.py repo.py
├── knowledge/     # diseases.json (bilingual, sources, reviewed flag), soil_crops.json
├── web/
│   ├── index.html diagnose.html soil.html history.html login.html register.html
│   ├── css/style.css   js/ (common.js i18n.js auth.js diagnose.js soil.js history.js)
│   └── i18n/ ar.json en.json
├── models/        # disease: model.onnx labels.json calibration.json class_reliability.json model_meta.json
│                  # soil: soil_model.joblib soil_meta.json
├── reports/  scripts/ (smoke_test.py create_admin.py)  tests/
└── docs/  steps/ checkpoints/ ARCHITECTURE.md DATA.md API.md TEST_PLAN.md DEPLOY.md EXTENDING.md GLOSSARY_AR.md defense_qa.md presentation_outline.md
```

---

## 8. Steps and checkpoints

### PHASE A — Foundation and data  (ends with Checkpoint A)

**Step 1 — Setup.** Folder structure, `.gitignore`, `.env.example`, `README.md` stub, `DECISIONS.md` (D1-D13 in Arabic with reasons), `PROGRESS.md`, `config.py` skeleton (crops, image size, thresholds, feature switches, paths, env settings), both requirements files, virtual environment, `tests/test_smoke.py`, first commit. Ask me ONCE for the GitHub repo URL if `origin` is missing, then push.

**Step 2 — Get the data.** Check which tools you need (Kaggle token, Hugging Face access). If I must create a Kaggle API token, give me click-by-click Arabic instructions. Download every dataset you can by CLI. Write `ml/label_map.py` (explicit mapping to `crop___condition` or `unknown`) and `ml/inventory.py` -> `reports/inventory.md` (counts per class/source/domain, corrupt files, size stats, imbalance, augmented-copy detection).

**Step 3 — Clean and split.** Apply the automatic hygiene (section 6), apply the inclusion rule automatically to fix the supported class list in `config.py`, then split: lab data by near-duplicate group into train/val/test (70/15/15); each field dataset's own test split -> `field_test`; at least one whole field dataset -> `source_holdout`; negatives split likewise. Output `data/manifest.csv` (`path,label,source,domain,split,group_id`). Tests: no `group_id` across splits; `field_test`/`source_holdout` never in train/val.

**CHECKPOINT A:** results of Steps 1-3 (which crops made it in and which did not, with real counts), 5 questions.

### PHASE B — Disease model  (ends with Checkpoint B)

**Step 4 — Shared preprocessing and training script.** `ml/preprocess.py` is the ONLY preprocessing definition (training eval, benchmarks, serving). `ml/train.py`: `timm` pretrained backbone with a new head (including `unknown`); phase A head only, phase B unfreeze with lower LR; AdamW, cosine schedule, label smoothing 0.1, mixed precision, fixed seeds, early stopping on validation macro-F1; **domain-balanced + class-balanced sampling** so lab images do not dominate; augmentation: random resized crop, flips, small rotation, color jitter, blur, random erasing. Saves weights, `labels.json`, `model_meta.json` (git commit, config, manifest hash, date, metrics).

**Step 5 — Train on a free GPU, automated.** Use the Kaggle CLI (`kaggle kernels push` with a GPU kernel, then poll status and download output) so I do not have to open notebooks. Do a tiny smoke run first (1 epoch on a small subset) to protect my weekly GPU quota. If the CLI route fails after 2 attempts, write `docs/how_to_train_on_kaggle.md` with the manual route and tell me.

**Step 6 — Benchmark.** Same settings for `mobilenetv3_large_100`, `efficientnet_b0`, and one slightly stronger model that fits the limits; also test image size 224 vs ~288-320 for the best one. Selection rule written BEFORE running: highest `source_holdout` + `field_test` macro-F1 among models meeting latency/size/memory limits. Results to `reports/benchmark.md` and `DECISIONS.md`.
**Step 7b (optional, offline):** a YOLO-classification comparison on the same split; results only in `DECISIONS.md`; never in requirements or the app.

**Step 7 — Calibration and unknown logic.** Temperature scaling on validation; choose the confidence threshold on validation negatives + valid leaves; save `models/calibration.json`. Rule: predicted `unknown` -> `not_supported`; calibrated confidence < threshold -> `uncertain`; else `ok`. Evaluate on `negative_test` (not used to choose the threshold).

**Step 8 — Honest evaluation and export.** `ml/evaluate.py` -> `reports/eval.md` + `reports/confusion_matrix.png`: per-class precision/recall/F1, top-1/top-3 for each of the four test sets, negative rejection, ECE before/after, 20 worst failures, most confused class pairs; write `class_reliability.json`. `ml/export_onnx.py` -> `models/model.onnx`; test PyTorch vs ONNX logits match (1e-4) on 20 images; measure median CPU latency (50 runs after warm-up) and memory. Do NOT tune on test sets. If a class is poor, say so and propose data fixes.

**CHECKPOINT B:** the real numbers for all four test sets, which classes are unreliable, the benchmark table, 5 questions.

### PHASE C — Backend: accounts, database, diagnosis  (ends with Checkpoint C)

**Step 9 — Database and accounts.** `app/db/` (SQLAlchemy models + repo). Tables: `users(id, username unique, password_hash, display_name NULL, language, is_admin, created_at)`, `scans(id, user_id NULL, created_at, predicted_label, confidence, status, model_version, language, image_path NULL)`, `feedback(id, scan_id, is_correct, correct_label NULL, note NULL, created_at)`, `soil_analyses(id, user_id, created_at, inputs_json, result_json, model_version)`. Endpoints: `POST /api/v1/auth/register`, `/login`, `/logout`, `GET /me`, `DELETE /me`; implement D12 completely. Tests: register/login/logout flow, wrong password, throttling, duplicate username, CSRF header missing, session cookie flags, account deletion removes data, password stored as an argon2 hash.

**Step 10 — Diagnosis API.** Load the ONNX session once at startup + warm-up inference; serve `web/` as static files. Endpoints: `GET /api/v1/health`, `GET /api/v1/classes`, `POST /api/v1/diagnose` (multipart). Upload safety: max 8 MB, verify by decoding with Pillow (not by extension), apply EXIF orientation, reject extreme dimensions, ignore file names, no saving unless the user consents (Step 12). `services/quality.py`: blur (variance of a Laplacian with numpy), brightness, minimum resolution -> `bad_quality` with reason code (`blurry`, `too_dark`, `too_bright`, `too_small`). Response (pydantic): `status`, `top3` (label, confidence, translatable keys), `low_reliability`, `knowledge` (only for `ok`/`uncertain`), `quality`, `model_version`, `latency_ms`. Structured logging with request ids. Tests: valid leaf, non-image file, oversized file, tiny, blurry, non-plant, corrupt JPEG, wrong content type, empty upload.

**Step 11 — Knowledge base (diseases + pesticide guidance).** `knowledge/diseases.json`, one entry per supported label, bilingual `{ar,en}`: `crop`, `name`, `symptoms`, `cause`, `cultural_actions`, `chemical_options` (list of `{active_ingredient, notes, dose_note, source}` following D8 exactly), `safety`, `call_expert_when`, `sources`, `reviewed:false`. Use web search to find real sources; entries you cannot source get cultural actions only. `ml/list_unreviewed.py` lists unreviewed entries. Tests: every supported label has an entry; every chemical option has a source; no entry misses a field; English gaps are listed (not silently empty).

**Step 12 — History and feedback.** Every diagnosis is logged (without the image; `user_id` if logged in). `GET /api/v1/history` (logged-in only), `POST /api/v1/feedback` ("was this correct?"). Photos saved ONLY if the user ticks consent, outside the web root, random file names, deleted with the scan/account. `ml/export_feedback.py` exports consented images + feedback for future retraining. Tests: consent off -> no file; deleting removes the file; users cannot read each other's history.

**CHECKPOINT C:** demo commands (curl/httpx) showing register -> login -> diagnose -> history -> logout; test report; 5 questions.

### PHASE D — Soil and crop advisor  (ends with Checkpoint D)

**Step 13 — Soil data and model.** Follow D13: search for the best dataset, prepare `soil/prepare_data.py`, restrict to crops relevant to Egypt, train and compare 2-3 simple models by cross-validation (RandomForest, gradient boosting, logistic regression baseline) in `soil/train.py`, choose with a rule written before running, save `models/soil_model.joblib` + `soil_meta.json` (features, units, crop list, per-crop typical ranges, CV metrics, date). `soil/evaluate.py` -> `reports/soil_eval.md` with honest wording about the dataset's limits.

**Step 14 — Soil API.** `POST /api/v1/soil/recommend` (validate numeric ranges with clear error codes; return top-3 crops with probabilities, per-input in-range/out-of-range flags, warnings, `model_version`; save to `soil_analyses` when logged in), `GET /api/v1/soil/crops` (covered crops + required inputs + units + help keys), `GET /api/v1/soil/history`. `knowledge/soil_crops.json` bilingual crop names. Tests: valid input, out-of-range, missing fields, extreme values, deterministic output.

**CHECKPOINT D:** the soil model's real CV numbers with the honest caveats, the list of covered crops, 5 questions.

### PHASE E — Frontend  (ends with Checkpoint E)

**Step 15 — Shell, i18n, auth pages.** Shared layout/nav (Home, Diagnose, Soil, History, Login/Account, language switch), `js/i18n.js` with `t(key)` and `data-i18n`, RTL/LTR switching, login/register pages calling the auth API (header `X-Requested-With: fetch`), logout, account page with delete-my-data. Mobile-first, accessible (labels, focus states, contrast, big tap targets), system font stack with Arabic support. No hardcoded user-visible text in HTML/JS. `textContent` only for server data.

**Step 16 — Diagnose page.** Camera/gallery via `<input type="file" accept="image/*" capture="environment">`, preview, client-side resize (max side 1024, JPEG ~0.85), states idle/loading/result/error, distinct designs for `ok`/`uncertain`/`not_supported`/`bad_quality`, top-3 bars, photo-taking tips, symptoms/cultural actions/pesticide guidance with safety lines and the "informational only" notice, consent checkbox for saving the photo, feedback buttons.

**Step 17 — Soil page and History page.** Soil form with units and help text, results with top-3, "why" per input (in range / out of range), warnings, and the limits notice; History page listing the user's scans and soil analyses with delete buttons. Guests see a friendly "log in to save" message.

**Step 18 — Frontend tests.** Automated: `ar.json` and `en.json` have identical keys; every `data-i18n` key and every status/reason/error code used by JS exists in both files; HTML pages load without missing assets (a test crawls the served pages). Manual checks are optional (browser device emulation in both languages is enough).

**CHECKPOINT E:** screenshots-by-description or the list of pages with what works, test results, 5 questions.

### PHASE F — Ship and document  (ends with Final checkpoint)

**Step 19 — Docker and deployment prep.** `Dockerfile` (python slim, CPU, non-root, healthcheck, `PORT` from env), local build + run + `scripts/smoke_test.py` end-to-end (register, login, diagnose with sample image, soil, history, logout) + memory check against the limit. The model files are not in git: document how the image gets them (build argument or download step) in `docs/DEPLOY.md`. `docs/DEPLOY.md` in simple Arabic: (1) run locally, (2) run with Docker, (3) deploy to a free host. Free-host terms change often, so search for the CURRENT terms yourself, present the best options with their limits (sleep policy, RAM, disk persistence), and recommend one. Explain that many free hosts have a temporary disk, so SQLite data and saved photos may vanish on restart, and give the options (persistent disk, external PostgreSQL via `DATABASE_URL`, or accept data loss for a demo). I will do the final deployment clicks myself later, so give me exact instructions.

**Step 20 — Documentation.** `README.md` (Arabic + English: what it is, supported crops and honestly which are missing, architecture diagram in ASCII, setup, run, API usage, retraining, adding a crop), `docs/ARCHITECTURE.md`, `docs/DATA.md`, `docs/API.md`, `docs/TEST_PLAN.md`, `docs/EXTENDING.md`, `docs/GLOSSARY_AR.md` (every technical term in simple Arabic), `MODEL_CARD.md` for both models (intended use, data, metrics per test set, failure modes, limits), `docs/defense_qa.md` (questions a mentor will ask — why pretrained, why not YOLO, why FastAPI, why argon2, what is the unknown class, why field accuracy is lower than lab accuracy, why some crops are missing, why the soil model is only advisory, how pesticide advice is sourced — with answers quoting OUR real numbers and decisions), `docs/presentation_outline.md` (10 slides).

**FINAL CHECKPOINT:** quality gates (section 9), a "how to continue developing" list, 5 questions.

---

## 9. Quality gates (a phase is not finished until all pass)

- `pytest` passes and `python -m compileall .` has no errors.
- The app starts from a clean clone following only the README.
- `scripts/smoke_test.py` passes against a running server.
- No number in any document is invented; all come from reports produced by code.
- Every decision is in `DECISIONS.md` with "why not the others".
- `PROGRESS.md` is up to date; everything is committed and pushed.

---

## 10. First instruction

Read this whole file. Reply in simple Arabic with (1) a 5-line summary of what we are building and (2) the exact list of things you need from me in the next hour (keep it minimal). Then start **Step 1** and continue automatically until Checkpoint A.
