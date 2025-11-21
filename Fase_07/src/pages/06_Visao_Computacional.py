import streamlit as st
from fase6_visao.inferencia_yolo import analisar_imagem_lavoura

st.title("Fase 6 – Visão Computacional da Lavoura")

arquivo = st.file_uploader("Envie uma imagem da lavoura", type=["jpg", "jpeg", "png"])

if arquivo is not None:
    with open("temp_lavoura.jpg", "wb") as f:
        f.write(arquivo.read())

    caminho_out, deteccoes = analisar_imagem_lavoura("temp_lavoura.jpg")

    st.subheader("Imagem analisada")
    st.image(caminho_out)

    st.subheader("Detecções")
    if not deteccoes:
        st.write("Nenhum problema detectado.")
    else:
        for det in deteccoes:
            st.write(f"- {det['classe']} (confiança: {det['score']:.2f})")
