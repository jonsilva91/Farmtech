import json, numpy as np, pandas as pd, joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

RAW = Path("../data/raw/telemetry.jsonl")
OUT = Path("../data/processed/dataset.csv")
OUT.parent.mkdir(parents=True, exist_ok=True)

rows = []
with RAW.open(encoding="utf-8", errors="ignore") as f:
    for line in f:
        try:
            rows.append(json.loads(line))
        except:
            pass
df = pd.DataFrame(rows)

FEATURES = ["temperatura_c","umidade_relativa_pct","pressao_hpa","umidade_solo_pct"]

def to_float(x):
    try: return float(x)
    except: return np.nan

for c in FEATURES:
    df[c] = df.get(c, np.nan).map(to_float)


def auto_label(r):
    t, h, s = r["temperatura_c"], r["umidade_relativa_pct"], r["umidade_solo_pct"]
    ok_t = (20 <= t <= 32) if pd.notna(t) else True
    ok_h = (50 <= h <= 80) if pd.notna(h) else True  # se não tiver UR (BMP), não penaliza
    ok_s = (35 <= s <= 65) if pd.notna(s) else False
    return "saudavel" if (ok_t and ok_h and ok_s) else "nao_saudavel"

if "label" not in df.columns:
    df["label"] = df.apply(auto_label, axis=1)

df.to_csv(OUT, index=False)

X = df[FEATURES]
y = df["label"].map({"nao_saudavel":0, "saudavel":1})

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)

pipe = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=500))
])
pipe.fit(Xtr, ytr)

print(confusion_matrix(yte, pipe.predict(Xte)))
print(classification_report(yte, pipe.predict(Xte), target_names=["nao_saudavel","saudavel"]))

joblib.dump(pipe, "model.joblib")
print("✅ modelo salvo em ml/model.joblib")
