import json, time, joblib, requests
from pathlib import Path
import pandas as pd
import numpy as np

MODEL = joblib.load("model.joblib")
RAW = Path("../data/raw/telemetry.jsonl")
SERVER = "https://participated-bet-unions-realtor.trycloudflare.com"
FEATURES = ["temperatura_c","umidade_relativa_pct","pressao_hpa","umidade_solo_pct"]

def to_float(x):
    try: return float(x)
    except: return np.nan

def follow(fp):
    fp.seek(0,2)
    while True:
        line = fp.readline()
        if not line:
            time.sleep(0.2); continue
        yield line

if __name__ == "__main__":
    with RAW.open(encoding="utf-8", errors="ignore") as f:
        for line in follow(f):
            try:
                obj = json.loads(line)
            except:
                continue

           
            xdict = {k: to_float(obj.get(k)) for k in FEATURES}
            X = pd.DataFrame([xdict])

            proba = float(MODEL.predict_proba(X)[0,1])
            label = "saudavel" if proba >= 0.5 else "nao_saudavel"

            out = {
                **obj,
                "pred_label": label,
                "pred_prob_saudavel": round(proba, 4),
                "missing_features": [k for k,v in xdict.items() if pd.isna(v)]
            }
            print(out)

            
            try:
                requests.post(f"{SERVER}/inference", json=out, timeout=5)
            except Exception as e:
                print("WARN: POST /inference falhou:", e)