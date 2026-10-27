import sys
from pathlib import Path
sys.path.insert(0, ".")
from ml.label_map import normalize

raw = Path("data/raw")
for ds in sorted(raw.iterdir()):
    if not ds.is_dir():
        continue
    parents = sorted({f.parent.name for f in ds.rglob("*.*") if f.suffix.lower() in (".jpg", ".jpeg", ".png")})
    print(f"=== {ds.name} ===")
    for p in parents:
        norm = normalize(p, ds.name)
        print(f'  "{p}" -> {norm}')
