import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error

st.title("📈 Regressão de Umidade do Solo")
st.markdown("Previsão do conteúdo volumétrico de água no solo usando RandomForestRegressor sobre todas as estações.")

# Parâmetros de modelagem
depths = [30, 60, 90, 120, 150]
sel_depth = st.selectbox("Profundidade (cm):", depths)
horizon  = st.number_input("Horizonte de previsão (horas à frente):", min_value=1, max_value=24, value=1)

@st.cache_data
def load_hourly_data():
    paths = glob.glob("CAF_sensors/Hourly/*.txt")
    dfs = []
    for path in paths:
        df = pd.read_csv(path, sep="\t")
        df['Station']   = os.path.basename(path).replace('.txt','')
        df['Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)
    data.set_index('Timestamp', inplace=True)
    return data

def prepare_data(data, depth, horizon):
    feat     = f"VW_{depth}cm"
    temp_col = f"T_{depth}cm"
    data = data.copy()
    data['target'] = data[feat].shift(-horizon)
    data_model    = data.dropna(subset=[feat, temp_col, 'target'])
    X = data_model[[feat, temp_col]]
    y = data_model['target']
    split = int(len(X) * 0.8)
    return X.iloc[:split], X.iloc[split:], y.iloc[:split], y.iloc[split:]

def train_model(X_train, y_train):
    m = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    m.fit(X_train, y_train)
    return m

if st.button("Treinar e Avaliar Modelo"):
    data = load_hourly_data()

    feat     = f"VW_{sel_depth}cm"
    temp_col = f"T_{sel_depth}cm"
    if feat not in data.columns or temp_col not in data.columns:
        st.error(f"Colunas {feat} ou {temp_col} não encontradas.")
        st.stop()

    X_train, X_test, y_train, y_test = prepare_data(data, sel_depth, horizon)

    with st.spinner("Treinando o modelo..."):
        model = train_model(X_train, y_train)

    # Avaliação
    y_pred = model.predict(X_test)
    mae    = mean_absolute_error(y_test, y_pred)
    mse    = mean_squared_error(y_test, y_pred)
    rmse   = mse ** 0.5
    r2     = model.score(X_test, y_test)

    st.write(f"**R² no teste:** {r2:.3f}")
    st.write(f"**MAE:** {mae:.3f}")
    st.write(f"**RMSE:** {rmse:.3f}")

    # Real vs Previsto
    st.subheader("Real x Previsto")
    res = pd.DataFrame({'Real': y_test, 'Previsto': y_pred}, index=y_test.index)
    res = res.tail(200)
    st.line_chart(res)

    # Importância das Features
    st.subheader("Importância das Features")
    fig, ax = plt.subplots()
    ax.bar([feat, temp_col], model.feature_importances_)
    ax.set_ylabel("Importância")
    st.pyplot(fig)

    # Validação Temporal
    st.subheader("Validação Temporal (TimeSeriesSplit)")
    tscv   = TimeSeriesSplit(n_splits=5)
    scores = []
    X_all = pd.concat([X_train, X_test])
    y_all = pd.concat([y_train, y_test])
    for tr, te in tscv.split(X_all):
        m = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
        m.fit(X_all.iloc[tr], y_all.iloc[tr])
        scores.append(m.score(X_all.iloc[te], y_all.iloc[te]))
    st.write(f"R² médio (CV): {pd.Series(scores).mean():.3f} ± {pd.Series(scores).std():.3f}")

    # Salvar modelo
    os.makedirs('model', exist_ok=True)
    model_path = f'model/soil_model_{sel_depth}cm.pkl'
    joblib.dump(model, model_path)
    st.success(f'Modelo salvo em {model_path}')
