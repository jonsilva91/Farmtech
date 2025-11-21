import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from clima_api import obter_dados_climaticos
from fase2_database.data.conexao import SQLiteDB
from fase2_database.data.crud_cultura import listar_culturas_com_area
from fase2_database.data.crud_adubacao import listar_adubacoes
from fase2_database.data.crud_fungicida import listar_fungicidas
from irrigar import decidir_irriga
import joblib
import numpy as np
import os

# ——— 1) Configuração da página ———
st.set_page_config(
    page_title="Dashboard Agrícola - Irrigação",
    page_icon="🌾",
    layout="centered"
)

st.markdown(
    """
    <style>
      /* valor da métrica */
      [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
      }
      /* rótulo da métrica */
      [data-testid="stMetricLabel"] {
        font-size: 0.5rem !important;
      }
    </style>
    """,
    unsafe_allow_html=True
)
# ——— 2) Carregamento dos modelos (pré-cacheado) ———
@st.cache_resource
def load_models():
    depths = [30, 60, 90, 120, 150]
    models = {}
    for d in depths:
        try:
            models[d] = joblib.load(f"model/soil_model_{d}cm.pkl")
        except FileNotFoundError:
            st.warning(f"Modelo para {d}cm não encontrado em model/soil_model_{d}cm.pkl")
    return models

soil_models = load_models()

# ——— 3) Interface de Irrigação ———
st.title("🌱 Dashboard de Monitoramento Agrícola - Irrigação")



st.markdown("---")

# ——— 4) Bloco de dados do banco separado ———
try:
    with SQLiteDB() as db:
        cursor = db.cursor

        culturas = listar_culturas_com_area(cursor)
        if not culturas:
            st.warning("Nenhuma cultura cadastrada.")
            st.stop()

        # Escolha de cultura/área
        opcoes = [
            f"{c['nm_cultura'].capitalize()} - Área {c['cd_area']} ({c['vl_area_ha']:.2f} ha)"
            for c in culturas
        ]
        escolha = st.selectbox("Selecione a cultura / área:", opcoes)
        sel = culturas[opcoes.index(escolha)]
        cd_area = sel['cd_area']

        # Leituras de sensores
        st.markdown("## 📊 Leituras de Sensores")
        cursor.execute("""
            SELECT s.tp_sensor, l.dt_leitura, l.vl_valor
            FROM Leitura_Sensor l
            JOIN Sensor s ON s.cd_sensor = l.cd_sensor
            WHERE s.cd_area = ?
            ORDER BY l.dt_leitura DESC
        """, (cd_area,))
        leituras = cursor.fetchall()

        if leituras:
            df = pd.DataFrame([dict(r) for r in leituras])
            df['dt_leitura'] = pd.to_datetime(df['dt_leitura'])
            df['tp_sensor'] = df['tp_sensor'].str.strip().str.lower()
            tipos = df['tp_sensor'].unique()
            cols = st.columns(len(tipos))
            for i, tipo in enumerate(tipos):
                df_t = df[df['tp_sensor'] == tipo]
                titulo = {
                    'ph':'pH','fosforo':'P','potassio':'K',
                    'nitrogenio':'N','umidade_solo':'Umidade Solo'
                }.get(tipo, tipo.capitalize())
                with cols[i]:
                    st.markdown(f"#### {titulo}")
                    fig, ax = plt.subplots()
                    ax.plot(df_t['dt_leitura'], df_t['vl_valor'], marker='o', linewidth=1)
                    ax.set_xticks(df_t['dt_leitura'][::max(1, len(df_t)//4)])
                    ax.tick_params(axis='x', rotation=45)
                    ax.set_ylabel('Valor')
                    ax.grid(True)
                    st.pyplot(fig)
        else:
            st.warning("Nenhuma leitura registrada.")

        st.markdown("---")

        # Aplicações
        st.markdown("## 🧪 Aplicações")
        adubacoes = [r for r in listar_adubacoes(cursor) if r['cd_area'] == cd_area]
        fungicidas = [r for r in listar_fungicidas(cursor) if r['cd_area'] == cd_area]

        if adubacoes:
            st.markdown("### 🌾 Adubação")
            df_ad = pd.DataFrame([dict(r) for r in adubacoes])
            st.dataframe(
                df_ad[['dt_aplicacao','vl_quantidade','vl_fosforo','vl_potassio','vl_nitrogenio']],
                use_container_width=True
            )
        else:
            st.info("Nenhuma adubação registrada.")

        if fungicidas:
            st.markdown("### 🛡️ Fungicida")
            df_fun = pd.DataFrame([dict(r) for r in fungicidas])
            st.dataframe(
                df_fun[['dt_aplicacao','nm_produto','vl_quantidade']],
                use_container_width=True
            )
        else:
            st.info("Nenhuma aplicação de fungicida registrada.")

except Exception as e:
    st.error(f"Erro ao carregar dados do banco: {e}")


st.markdown("---")
# Dados atuais de clima
temperatura, umidade, precipitacao, condicao = obter_dados_climaticos()


# Dados do banco de dados
umidade_solo = next((l['vl_valor'] for l in leituras if l['tp_sensor'] == 'umidade_solo'), None)
temperatura_solo = next((l['vl_valor'] for l in leituras if l['tp_sensor'] == 'temperatura'), None)

# Seleção de profundidade
depths = list(soil_models.keys())
sel_depth = st.selectbox("Profundidade simulada (cm):", depths)

# Exibição das métricas
c1, c2, c3, c4 = st.columns(4)
c1.metric("🌡️ Temperatura (°C)", f"{temperatura:.1f}")
c2.metric("💧 Umidade (%)",    f"{umidade:.0f}")
c3.metric("🌧️ Precipitação (mm)", f"{precipitacao:.1f}")
# Predição de VW do solo: se não tiver no banco usa a do API 

if umidade_solo is not None:
    umidade_pred = umidade_solo
else:
    umidade_pred = umidade
    
if temperatura_solo is not None:
    temperatura_pred = temperatura_solo
else:
    temperatura_pred = temperatura

try:
    model = soil_models[sel_depth]
    X_new = [[umidade_pred,temperatura_pred]]
    vw_pred = float(model.predict(X_new)[0])
except Exception as e:
    vw_pred = None
    st.error(f"Erro ao prever VW do solo: {e}")
if vw_pred is not None:
    c4.metric(f"🌊CVA previsto solo ({sel_depth}cm)", f"{vw_pred:.2f} m³/m³")
st.caption(f"Condição: {condicao.capitalize()}")

if vw_pred is not None:
    status = decidir_irriga(vw_pred)
    st.write(f"**Status de Irrigação:** {status}")

   # if umidade < 65:
       # st.error("🚨 Irrigação recomendada (umidade do ar abaixo de 65%)")
    #else:
        #st.success("✅ Umidade do ar adequada")

# ─── 5) Previsão de Fertilizante ───────────────────────────────────────────────
st.markdown("---")
st.markdown("## 🧪 Previsão de Fertilizante")

@st.cache_resource
def load_fertilizer_model():
    here      = os.path.dirname(__file__)
    model_dir = os.path.abspath(os.path.join(here, "..", "src/model"))
    model_path = os.path.join(model_dir, "xgb_fertilizer_recommendation.pkl")

    
    if not os.path.exists(model_path):
        st.error(f"❌ Modelo não encontrado em {model_path}")
        return None, None, None, None, None  # ou quantos forem necessários

    loaded = joblib.load(model_path)
    

    # Agora é só extrair do dict
    model     = loaded.get("model")
    scaler    = loaded.get("scaler")
    le_crop   = loaded.get("le_crop")
    le_fert   = loaded.get("le_fert")
    features  = loaded.get("features")

    return model, scaler, le_crop, le_fert, features

fert_model, fert_scaler, crop_label_enc, fert_label_enc, feat_names = load_fertilizer_model()


if fert_model is not None:
    st.markdown("---")

    # pega valores que você já tinha
    nitrogenio = next((l["vl_valor"] for l in leituras if l["tp_sensor"]=="nitrogenio"), 0)
    fosforo    = next((l["vl_valor"] for l in leituras if l["tp_sensor"]=="fosforo"), 0)
    potassio   = next((l["vl_valor"] for l in leituras if l["tp_sensor"]=="potassio"), 0)

    st.write(f"- 🌡 Temperatura: **{temperatura_pred:.1f}** °C")
    st.write(f"- 💧 Umidade do solo: **{umidade_pred:.1f}** %")
    st.write(f"- 🌱 N: **{nitrogenio:.1f}**, P: **{fosforo:.1f}**, K: **{potassio:.1f}**")

    if st.button("🔮 Prever Fertilizante"):
        # monta o dict de entrada zerado
        x0 = {f: 0 for f in feat_names}
        x0["Temperature"]  = temperatura_pred
        x0["Moisture"]     = umidade_pred
        x0["Nitrogen"]     = nitrogenio
        x0["Phosphorous"]  = fosforo
        x0["Potassium"]    = potassio
        # se quiser usar cultivo corrente:
        # cultivo = sel['nm_cultura']
        # x0["CropEnc"] = crop_label_enc.transform([cultivo])[0]
        # soils: você pode buscar o tipo de solo atual e setar x0[f"Soil_{tipo}"]=1

        # DataFrame na ordem certa
        X_new = pd.DataFrame([x0], columns=feat_names)
        # escala
        X_scaled = fert_scaler.transform(X_new)
        # predict
        y_pred = fert_model.predict(X_scaled)
        rec    = fert_label_enc.inverse_transform(y_pred)[0]
        st.success(f"**{rec}**")
