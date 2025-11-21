import streamlit as st
from datetime import datetime

from fase2_database.data.conexao import SQLiteDB
from fase2_database.data.crud_responsavel import listar_responsaveis, inserir_responsavel
from fase2_database.data.crud_cultura import inserir_cultura
from fase2_database.data.crud_area_plantio import inserir_area_plantio
from fase2_database.data.crud_sensor import inserir_sensor
from fase2_database.data.crud_leitura import inserir_leitura
from fase2_database.data.crud_adubacao import inserir_adubacao
from fase2_database.data.crud_fungicida import inserir_fungicida

from fase1_calculos.calculos import (
    area_retangulo,
    area_circulo,
    area_triangulo,
    area_trapezio,
    area_personalizada,
    calculo_densidade,
    calcular_semeadura,
    calcular_peso_area,
    calcular_produtividade,
    calcular_adubo_soja,
    calcular_adubo_milho,
    calcular_pulverizadores,
    calcular_volume_fungicida,
)

from clima_api import obter_dados_climaticos


st.title("Cadastro de Cultura e Área (Fases 1–3)")


# ============================================================
# 1) RESPONSÁVEL
# ============================================================

# @st.cache_data(ttl=60)
def carregar_responsaveis():
    with SQLiteDB() as db:
        cursor = db.cursor
        return listar_responsaveis(cursor)



st.subheader("Responsável pela área")

responsaveis = carregar_responsaveis()
opcoes_resp = ["-- Selecione --"] + [
    f"{r['cd_responsavel']} - {r['nm_responsavel']}" for r in responsaveis
]

resp_escolhido = st.selectbox(
    "Responsável já cadastrado:",
    options=opcoes_resp,
    index=0,
)

st.markdown("Ou cadastre um novo responsável:")

with st.expander("➕ Cadastrar novo responsável"):
    col1, col2, col3 = st.columns(3)
    with col1:
        novo_nome = st.text_input("Nome")
    with col2:
        novo_tel = st.text_input("Telefone")
    with col3:
        novo_email = st.text_input("Email")

    if st.button("Salvar novo responsável"):
        if not novo_nome:
            st.error("Informe ao menos o nome do responsável.")
        else:
            with SQLiteDB() as db:
                cursor = db.cursor
                inserir_responsavel(cursor, {
                    "nm_responsavel": novo_nome,
                    "nm_telefone": novo_tel,
                    "nm_email": novo_email,
                })
                db.conn.commit()
            st.success("Responsável cadastrado com sucesso! Atualize a página para vê-lo na lista.")


# ============================================================
# 2) CULTURA E ÁREA
# ============================================================

st.subheader("Dados da cultura e área de plantio")

col1, col2 = st.columns(2)
with col1:
    tipo_cultura = st.selectbox("Cultura", ["soja", "milho"])
with col2:
    modo_area = st.radio(
        "Como deseja informar a área?",
        ["Informar direto em hectares", "Calcular pela forma geométrica"],
        horizontal=False,
    )

if modo_area == "Informar direto em hectares":
    area_ha = st.number_input("Área da área de plantio (ha)", min_value=0.0, step=0.1)
else:
    st.markdown("**Calcular área pela forma geométrica**")
    forma = st.selectbox(
        "Forma geométrica do talhão:",
        ["Retângulo", "Círculo", "Triângulo", "Trapézio", "Personalizado"],
    )

    area_ha = 0.0
    if forma == "Retângulo":
        c1, c2 = st.columns(2)
        with c1:
            base = st.number_input("Base (m)", min_value=0.0, step=0.1, key="base_ret")
        with c2:
            altura = st.number_input("Altura (m)", min_value=0.0, step=0.1, key="alt_ret")
        if base > 0 and altura > 0:
            area_m2, area_ha = area_retangulo(base, altura)
            st.info(f"Área calculada: {area_m2:.2f} m² ({area_ha:.2f} ha)")

    elif forma == "Círculo":
        raio = st.number_input("Raio (m)", min_value=0.0, step=0.1, key="raio")
        if raio > 0:
            area_m2, area_ha = area_circulo(raio)
            st.info(f"Área calculada: {area_m2:.2f} m² ({area_ha:.2f} ha)")

    elif forma == "Triângulo":
        c1, c2 = st.columns(2)
        with c1:
            base = st.number_input("Base (m)", min_value=0.0, step=0.1, key="base_tri")
        with c2:
            altura = st.number_input("Altura (m)", min_value=0.0, step=0.1, key="alt_tri")
        if base > 0 and altura > 0:
            area_m2, area_ha = area_triangulo(base, altura)
            st.info(f"Área calculada: {area_m2:.2f} m² ({area_ha:.2f} ha)")

    elif forma == "Trapézio":
        c1, c2, c3 = st.columns(3)
        with c1:
            base_maior = st.number_input("Base maior (m)", min_value=0.0, step=0.1, key="base_maior")
        with c2:
            base_menor = st.number_input("Base menor (m)", min_value=0.0, step=0.1, key="base_menor")
        with c3:
            altura = st.number_input("Altura (m)", min_value=0.0, step=0.1, key="alt_trap")
        if base_maior > 0 and base_menor > 0 and altura > 0:
            area_m2, area_ha = area_trapezio(base_maior, base_menor, altura)
            st.info(f"Área calculada: {area_m2:.2f} m² ({area_ha:.2f} ha)")

    elif forma == "Personalizado":
        st.info("Use a fórmula com x e y. Ex.: x * y / 2")
        formula = st.text_input("Fórmula", value="x * y")
        c1, c2 = st.columns(2)
        with c1:
            x = st.number_input("x", value=1.0, step=0.1, key="x_pers")
        with c2:
            y = st.number_input("y", value=1.0, step=0.1, key="y_pers")
        try:
            area_m2, area_ha = area_personalizada(formula, x, y)
            st.info(f"Área calculada: {area_m2:.2f} m² ({area_ha:.2f} ha)")
        except Exception as e:
            st.error(f"Erro ao calcular fórmula personalizada: {e}")


st.markdown("---")
st.subheader("Parâmetros agronômicos")

c1, c2 = st.columns(2)
with c1:
    germinacao = st.number_input(
        "Poder germinativo das sementes (%)",
        min_value=1.0,
        max_value=100.0,
        value=90.0,
        step=0.5,
    )
with c2:
    peso_mil_graos = st.number_input(
        "Peso de 1000 grãos (g)",
        min_value=1.0,
        step=0.1,
    )

calc_produtividade = st.checkbox("Calcular produtividade estimada?")

produtividade_calc = None
if calc_produtividade:
    if tipo_cultura == "soja":
        c3, c4 = st.columns(2)
        with c3:
            qtd_vagens = st.number_input(
                "Total de vagens em 10 plantas",
                min_value=1.0,
                step=1.0,
            )
        with c4:
            qtd_graos_vagens = st.number_input(
                "Total de grãos nas vagens",
                min_value=1.0,
                step=1.0,
            )
        if qtd_vagens > 0 and qtd_graos_vagens > 0:
            produtividade_calc = calcular_produtividade(
                "soja",
                qtd_vagens=qtd_vagens,
                qtd_graos_vagens=qtd_graos_vagens,
                germinacao=germinacao,
                peso_mil_graos=peso_mil_graos,
            )
            st.info(f"Produtividade estimada (soja): {produtividade_calc:.2f} t/ha")
    else:
        peso_graos = st.number_input(
            "Peso de grãos da amostra (g)",
            min_value=1.0,
            step=1.0,
        )
        if peso_graos > 0:
            produtividade_calc = calcular_produtividade(
                "milho",
                peso_graos=peso_graos,
            )
            st.info(f"Produtividade estimada (milho): {produtividade_calc:.2f} t/ha")

# Cálculos derivados (densidade, taxa, peso/ha)
espacamento = 0.4 if tipo_cultura == "soja" else 0.5
densidade = calculo_densidade(tipo_cultura, espacamento)
taxa_semeadura = calcular_semeadura(densidade, germinacao)
peso_ha = calcular_peso_area(tipo_cultura, peso_mil_graos, germinacao)


# ============================================================
# 3) SENSORES / API DE CLIMA
# ============================================================

st.markdown("---")
st.subheader("Sensores e API de clima")

usar_api_sensores = st.checkbox("Registrar leituras simuladas usando API de clima (umidade do ar)")

umidade_api = None
if usar_api_sensores:
    if st.button("Buscar clima atual da API"):
        try:
            temp_api, umidade_api, chuva_api, cond_api = obter_dados_climaticos()
            st.success(
                f"Clima atual: {temp_api:.1f} °C, {umidade_api:.0f}% umidade, "
                f"chuva {chuva_api} mm, condição: {cond_api}"
            )
        except Exception as e:
            st.error(f"Erro ao obter dados climáticos: {e}")

    st.markdown("Preencha os valores estimados dos sensores de solo:")

    c1, c2, c3 = st.columns(3)
    with c1:
        temperatura_solo = st.number_input(
            "Temperatura do solo estimada (°C)",
            value=25.0,
            step=0.5,
        )
    with c2:
        umidade_solo = st.number_input(
            "Umidade do solo estimada (m³/m³)",
            value=0.25,
            step=0.01,
        )
    with c3:
        ph_solo = st.number_input(
            "pH estimado (0–14)",
            min_value=0.0,
            max_value=14.0,
            value=6.0,
            step=0.1,
        )

    c4, c5, c6 = st.columns(3)
    with c4:
        fosforo = st.number_input("Fósforo (unidade do laboratório)", value=10.0, step=0.5)
    with c5:
        potassio = st.number_input("Potássio (unidade do laboratório)", value=5.0, step=0.5)
    with c6:
        nitrogenio = st.number_input("Nitrogênio (unidade do laboratório)", value=5.0, step=0.5)


# ============================================================
# 4) ADUBAÇÃO
# ============================================================

st.markdown("---")
st.subheader("Adubação")

registrar_adubacao = st.checkbox("Registrar adubação para esta área")

if registrar_adubacao:
    if tipo_cultura == "soja":
        st.markdown("### Parâmetros para soja")
        c1, c2, c3 = st.columns(3)
        with c1:
            p_resina = st.number_input("P (P-resina, mg/dm³)", min_value=0.0, step=0.1)
        with c2:
            k_trocavel = st.number_input("K trocável (cmolc/dm³)", min_value=0.0, step=0.1)
        with c3:
            prod_est = st.number_input("Produtividade esperada (t/ha)", min_value=0.0, step=0.1)
    else:
        st.markdown("### Parâmetros para milho")
        c1, c2 = st.columns(2)
        with c1:
            prod_est = st.number_input(
                "Produtividade esperada (t/ha)",
                min_value=5.0,
                max_value=15.0,
                step=1.0,
            )
        with c2:
            destino = st.selectbox("Finalidade", ["grao", "silagem"])


# ============================================================
# 5) FUNGICIDA
# ============================================================

st.markdown("---")
st.subheader("Aplicação de fungicida")

registrar_fungicida = st.checkbox("Registrar aplicação de fungicida")

if registrar_fungicida:
    nome_fungicida = st.text_input("Nome do produto fungicida")
    c1, c2, c3 = st.columns(3)
    with c1:
        velocidade = st.number_input("Velocidade do trator (m/min)", min_value=0.0, step=0.1)
        tanque = st.number_input("Capacidade do tanque (L)", min_value=0.0, step=1.0)
    with c2:
        vazao = st.number_input("Vazão do pulverizador (L/min)", min_value=0.0, step=0.1)
        num_pulverizadores = st.number_input("Qtd de bicos/pulverizadores", min_value=1, step=1)
    with c3:
        espacadores = st.number_input("Espaçamento entre bicos (cm)", min_value=0.0, step=0.5)
        qtd_lha = st.number_input("Recomendação do fabricante (L/ha)", min_value=0.0, step=0.1)


# ============================================================
# 6) BOTÃO FINAL – SALVAR NO BANCO
# ============================================================

st.markdown("---")
if st.button("💾 Salvar cultura e área no banco"):
    # Validações básicas
    if resp_escolhido == "-- Selecione --":
        st.error("Selecione um responsável já cadastrado ou cadastre um novo.")
    elif area_ha <= 0:
        st.error("A área deve ser maior que zero.")
    else:
        try:
            cd_responsavel = int(resp_escolhido.split(" - ")[0])

            with SQLiteDB() as db:
                cursor = db.cursor

                # 1) Inserir cultura
                inserir_cultura(cursor, {
                    "nm_cultura": tipo_cultura,
                    "tp_cultura": tipo_cultura,
                })
                cd_cultura = cursor.lastrowid

                # 2) Inserir área de plantio
                inserir_area_plantio(cursor, {
                    "vl_area_ha": area_ha,
                    "vl_espacamento": espacamento,
                    "vl_densidade": densidade,
                    "vl_taxa_semeadura": taxa_semeadura,
                    "vl_peso_ha": peso_ha,
                    "cd_cultura": cd_cultura,
                    "cd_responsavel": cd_responsavel,
                    "ds_produtividade": str(produtividade_calc) if produtividade_calc else None,
                })
                cd_area = cursor.lastrowid

                # 3) Sensores / leituras simuladas via API
                if usar_api_sensores:
                    if umidade_api is None:
                        # se o usuário esqueceu de clicar em "Buscar clima"
                        temp_api, umidade_api_local, chuva_api, cond_api = obter_dados_climaticos()
                    else:
                        umidade_api_local = umidade_api

                    for tp, val in [
                        ("umidade", umidade_api_local),
                        ("temperatura", temperatura_solo),
                        ("fosforo", fosforo),
                        ("potassio", potassio),
                        ("nitrogenio", nitrogenio),
                        ("umidade_solo", umidade_solo),
                        ("ph", ph_solo),
                    ]:
                        cd_sensor = inserir_sensor(cursor, tp, "Simulado", cd_area)
                        inserir_leitura(cursor, cd_sensor, datetime.now(), val)

                # 4) Adubação
                if registrar_adubacao:
                    if tipo_cultura == "soja":
                        p2o5_ha, k2o_ha = calcular_adubo_soja(prod_est, p_resina, k_trocavel)
                        inserir_adubacao(cursor, cd_area, p2o5_ha, k2o_ha, None)
                    else:
                        n_ha, p2o5_ha, k2o_ha = calcular_adubo_milho(prod_est, destino)
                        inserir_adubacao(cursor, cd_area, p2o5_ha, k2o_ha, n_ha)

                # 5) Fungicida
                if registrar_fungicida and nome_fungicida:
                    dosagem, taxa_aplicacao, _ = calcular_pulverizadores(
                        qtd_lha,
                        tanque,
                        vazao,
                        velocidade,
                        num_pulverizadores,
                        espacadores,
                    )
                    fungicida_ha, total_fungicida = calcular_volume_fungicida(
                        area_ha, tanque, dosagem, taxa_aplicacao
                    )
                    inserir_fungicida(cursor, cd_area, total_fungicida, nome_fungicida)

                db.conn.commit()

            st.success("✅ Cultura, área e registros associados salvos com sucesso!")

        except Exception as e:
            st.error(f"❌ Erro ao salvar no banco: {e}")
