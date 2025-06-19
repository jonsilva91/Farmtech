import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib
import warnings
import matplotlib.pyplot as plt

from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, top_k_accuracy_score, confusion_matrix, classification_report, ConfusionMatrixDisplay
from sklearn.model_selection import cross_val_score

from xgboost import XGBClassifier

warnings.filterwarnings('ignore')

# ─── PATHS ───────────────────────────────────────────────────────────────────
HERE = os.path.dirname(__file__)
DATA_PATH = os.path.abspath(os.path.join(HERE, '..', '..', 'document', 'fertilizer_recommendation_dataset.csv'))
MODEL_DIR = os.path.abspath(os.path.join(HERE, '..', 'model'))
os.makedirs(MODEL_DIR, exist_ok=True)

# ─── LOAD DATA ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

df = load_data(DATA_PATH)

st.title("🚀 XGBoost - Recomendação de Fertilizantes")

# ─── PREPROCESS ─────────────────────────────────────────────────────────────
# One-hot encode soil types
soil_dummies = pd.get_dummies(df['Soil'], prefix='Soil')
# Label encode crop and fertilizer
le_crop = LabelEncoder()
le_fert = LabelEncoder()

df['CropEnc'] = le_crop.fit_transform(df['Crop'])
df['FertEnc'] = le_fert.fit_transform(df['Fertilizer'])

# Assemble features
FEATURES = ['Temperature','Moisture','Rainfall','PH','Nitrogen','Phosphorous','Potassium','Carbon']
X = pd.concat([ df[FEATURES], soil_dummies, df[['CropEnc']] ], axis=1)
y = df['FertEnc']
# Drop unused columns
# df = df.drop(columns=['Soil','Crop','Fertilizer','Remark'])

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
st.sidebar.header("Configuração de Split")
test_pct = st.sidebar.slider("Tamanho do teste (%)", 10, 50, 20, 5)

st.sidebar.header("Hiperparâmetros XGBoost")
n_estimators = st.sidebar.slider("n_estimators", 50, 2000, 200, 50)
max_depth = st.sidebar.slider("max_depth", 3, 15, 6, 1)
learning_rate = st.sidebar.slider("learning_rate", 0.01, 0.5, 0.1, 0.01)
subsample = st.sidebar.slider("subsample", 0.5, 1.0, 0.8, 0.05)
colsample = st.sidebar.slider("colsample_bytree", 0.5, 1.0, 0.8, 0.05)
gamma = st.sidebar.slider("gamma", 0.0, 5.0, 0.0, 0.1)

params = {
    'n_estimators': int(n_estimators),
    'max_depth': int(max_depth),
    'learning_rate': float(learning_rate),
    'subsample': float(subsample),
    'colsample_bytree': float(colsample),
    'gamma': float(gamma),
    'objective': 'multi:softprob',
    'num_class': len(le_fert.classes_),
    'use_label_encoder': False,
    'eval_metric': 'mlogloss'
}

# ─── SPLIT & SCALE ──────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=test_pct/100,
    stratify=y,
    random_state=42
)

scaler = StandardScaler().fit(X_train)
X_train_s = scaler.transform(X_train)
X_test_s = scaler.transform(X_test)

# ─── TREINO ──────────────────────────────────────────────────────────────────
with st.spinner("Treinando XGBoost…"):
    model = XGBClassifier(**params)
    model.fit(X_train_s, y_train)

# ─── AVALIAÇÃO ───────────────────────────────────────────────────────────────
st.subheader("Avaliação no Conjunto de Teste")

# Previsões
y_pred = model.predict(X_test_s)
proba = model.predict_proba(X_test_s)

acc = accuracy_score(y_test, y_pred)
top3 = top_k_accuracy_score(y_test, proba, k=3)

st.metric("Acurácia (Top-1)", f"{acc:.4f}")
st.metric("Top-3 Accuracy", f"{top3:.4f}")
#
acc_train = accuracy_score(y_test, model.predict(X_test_s))
st.metric("⚙️ Acurácia Treino", f"{acc_train:.4f}")
st.metric("🎯 Acurácia Teste", f"{acc:.4f}")

cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
st.write(f"📊 CV Accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
# Matriz de Confusão

cm = confusion_matrix(y_test, y_pred, normalize='true')
fig, ax = plt.subplots(figsize=(6,6))
disp = ConfusionMatrixDisplay(cm, display_labels=le_fert.classes_)
disp.plot(
    ax=ax,
    cmap='Blues',
    values_format='.2f'      # mostra percentuais
)
plt.xticks(rotation=90, ha='right')
plt.yticks(rotation=0)
plt.title("Matriz de Confusão Normalizada", pad=20)
st.pyplot(fig)


# Classification Report
st.text_area("Classification Report", classification_report(y_test, y_pred, target_names=le_fert.classes_))

# Importância de Features
importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
st.subheader("Importância das Features")
st.bar_chart(importances)

# ─── SALVAR MODELO ──────────────────────────────────────────────────────────
if st.button("💾 Salvar Modelo XGBoost"):
    joblib.dump({'model': model, 'scaler': scaler, 'le_crop': le_crop, 'le_fert': le_fert, 'features': list(X.columns)},
                os.path.join(MODEL_DIR, 'xgb_fertilizer_recommendation.pkl'))
    st.success("Modelo salvo em `model/xgb_fertilizer_recommendation.pkl`")

st.info("Use `joblib.load` para recarregar o modelo, scaler e encoders.")
