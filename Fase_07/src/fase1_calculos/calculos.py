import math

# ============================================================
# FUNÇÕES DE CÁLCULO DE ÁREA (SEM INPUT/PRINT)
# ============================================================

def area_retangulo(base_m: float, altura_m: float):
    """
    Calcula a área de um retângulo em m² e hectares.
    Retorna (area_m2, area_ha).
    """
    area_m2 = base_m * altura_m
    return area_m2, area_m2 / 10_000


def area_circulo(raio_m: float):
    """
    Calcula a área de um círculo em m² e hectares.
    """
    area_m2 = math.pi * (raio_m ** 2)
    return area_m2, area_m2 / 10_000


def area_triangulo(base_m: float, altura_m: float):
    """
    Calcula a área de um triângulo em m² e hectares.
    """
    area_m2 = (base_m * altura_m) / 2
    return area_m2, area_m2 / 10_000


def area_trapezio(base_maior_m: float, base_menor_m: float, altura_m: float):
    """
    Calcula a área de um trapézio em m² e hectares.
    """
    area_m2 = ((base_maior_m + base_menor_m) * altura_m) / 2
    return area_m2, area_m2 / 10_000


def area_personalizada(formula: str, x: float, y: float):
    """
    Calcula a área a partir de uma fórmula personalizada usando x e y.
    Exemplo de fórmula: "x * y / 2"
    Retorna (area_m2, area_ha).

    ATENÇÃO: usa eval, então é para uso controlado.
    """
    try:
        area_m2 = eval(formula, {"x": x, "y": y, "math": math})
    except Exception as e:
        raise ValueError(f"Erro ao calcular fórmula personalizada: {e}")
    return area_m2, area_m2 / 10_000


# ============================================================
# ADUBAÇÃO
# ============================================================

def calcular_adubo_soja(produtividade, p_resina, k_trocavel):
    """
    Calcula a quantidade de P2O5 e K2O recomendados (kg/ha)
    para soja, com base na produtividade esperada, P-resina e K trocável.

    Retorna (p2o5_ha, k2o_ha).
    """
    # Tabela de recomendação de P2O5 (kg/ha) com base na produtividade esperada e P-resina (mg/dm³)
    tabela_p2o5 = {
        ("<2.0", (50, 40, 30, 20)),
        ("2.0-2.5", (60, 50, 40, 20)),
        ("2.5-3.0", (80, 60, 40, 20)),
        ("3.0-3.5", (90, 70, 50, 30)),
        (">3.5", (80, 50, 40, 0)),
    }

    # Tabela de recomendação de K2O (kg/ha) com base no potássio trocável (mmolc/dm³)
    tabela_k2o = {
        ("<2.0", (60, 40, 20, 0)),
        ("2.0-2.5", (70, 50, 30, 20)),
        ("2.5-3.0", (70, 50, 50, 20)),
        ("3.0-3.5", (80, 60, 50, 30)),
        (">3.5", (80, 60, 60, 40)),
    }

    def encontrar_valor(tabela, produtividade_):
        for chave, valores in tabela:
            if "-" in chave:
                lim_inf, lim_sup = map(float, chave.split("-"))
                if lim_inf <= produtividade_ <= lim_sup:
                    return valores
            elif "<" in chave and produtividade_ < float(chave[1:]):
                return valores
            elif ">" in chave and produtividade_ > float(chave[1:]):
                return valores
        return None

    valores_p2o5 = encontrar_valor(tabela_p2o5, produtividade)
    valores_k2o = encontrar_valor(tabela_k2o, produtividade)

    if not valores_p2o5 or not valores_k2o:
        raise ValueError("Não foi possível encontrar os valores na tabela de adubação de soja.")

    # Selecionar a quantidade de P2O5 conforme P-resina
    if p_resina < 7:
        p2o5_ha = valores_p2o5[0]
    elif 7 <= p_resina < 16:
        p2o5_ha = valores_p2o5[1]
    elif 16 <= p_resina < 40:
        p2o5_ha = valores_p2o5[2]
    else:
        p2o5_ha = valores_p2o5[3]

    # Selecionar a quantidade de K2O conforme K trocável
    if k_trocavel < 0.8:
        k2o_ha = valores_k2o[0]
    elif 0.8 <= k_trocavel < 1.5:
        k2o_ha = valores_k2o[1]
    elif 1.5 <= k_trocavel < 3.0:
        k2o_ha = valores_k2o[2]
    else:
        k2o_ha = valores_k2o[3]

    return p2o5_ha, k2o_ha


def calcular_adubo_milho(produtividade, tipo):
    """
    Calcula a quantidade de N, P2O5 e K2O (kg/ha) para milho,
    com base na produtividade esperada (ton/ha) e no tipo de milho.

    :param produtividade: Produtividade esperada (ton/ha), entre 5 e 15.
    :param tipo: Tipo de milho ('grao' ou 'silagem')
    :return: (N_kg_ha, P2O5_kg_ha, K2O_kg_ha)
    """
    tabela_adubacao = {
        5:  {'grao': (120, 85, 31),  'silagem': (195, 105, 145)},
        6:  {'grao': (144, 102, 37), 'silagem': (234, 126, 174)},
        7:  {'grao': (168, 119, 43), 'silagem': (273, 147, 203)},
        8:  {'grao': (192, 136, 49), 'silagem': (312, 168, 232)},
        9:  {'grao': (216, 153, 55), 'silagem': (351, 189, 261)},
        10: {'grao': (240, 170, 61), 'silagem': (390, 210, 290)},
        11: {'grao': (264, 187, 68), 'silagem': (429, 231, 319)},
        12: {'grao': (288, 204, 74), 'silagem': (468, 252, 348)},
        13: {'grao': (312, 221, 80), 'silagem': (507, 273, 377)},
        14: {'grao': (336, 238, 86), 'silagem': (546, 294, 406)},
        15: {'grao': (360, 255, 92), 'silagem': (585, 315, 435)},
    }

    if produtividade not in tabela_adubacao:
        raise ValueError("Produtividade fora da faixa disponível (5–15 ton/ha).")
    if tipo not in ['grao', 'silagem']:
        raise ValueError("Tipo inválido. Use 'grao' ou 'silagem'.")

    return tabela_adubacao[produtividade][tipo]


# ============================================================
# DENSIDADE, SEMEADURA, PRODUTIVIDADE
# ============================================================

def calculo_densidade(tipo_cultura, espacamento):
    """
    Calcula a densidade de plantas por metro linear, dado o espaçamento (m)
    e o tipo de cultura (soja ou milho).
    """
    if tipo_cultura == 'soja':
        densidade = (300_000 * espacamento) / 10_000
    else:
        densidade = (60_000 * espacamento) / 10_000
    return densidade


def calcular_semeadura(densidade, germinacao):
    """
    Calcula a taxa de semeadura (sementes por metro),
    dado a densidade desejada e o % de germinação.
    """
    taxa_semeadura = (densidade * 100) / germinacao
    return taxa_semeadura


def calcular_peso_area(tipo_cultura, peso_mil_graos, germinacao):
    """
    Calcula o peso de grãos por hectare, considerando perda de 10% de produção.
    Retorna kg/ha.
    """
    if tipo_cultura == 'soja':
        qtd_por_hectare = ((300_000 * 100) / germinacao) * 1.1
        peso_por_hectare = (qtd_por_hectare * peso_mil_graos) / 1000
    else:
        qtd_por_hectare = ((60_000 * 100) / germinacao) * 1.1
        peso_por_hectare = (qtd_por_hectare * peso_mil_graos) / 1000

    return peso_por_hectare


def calcular_produtividade(
    tipo_cultura,
    qtd_vagens=None,
    qtd_graos_vagens=None,
    germinacao=None,
    peso_mil_graos=None,
    peso_graos=None,
):
    """
    Calcula a produtividade estimada (t/ha) para soja ou milho.

    Para soja:
      - qtd_vagens: nº total de vagens em 10 plantas
      - qtd_graos_vagens: nº total de grãos nessas vagens
      - germinacao: % de germinação
      - peso_mil_graos: peso de 1000 grãos (g)

    Para milho:
      - peso_graos: peso de grãos (g) em área amostral padrão
    """
    if tipo_cultura == 'soja':
        vagens_planta = qtd_vagens / 10
        grao_vagem = qtd_graos_vagens / qtd_vagens

        produtividade = (
            (((300_000 * 100) / germinacao) * 1.1)
            * vagens_planta
            * grao_vagem
            * peso_mil_graos
        )
        produtividade = produtividade / 60_000 / 1000  # conversão final para t/ha
    else:
        produtividade = ((peso_graos / 1000) * 60_000) / 1000

    return round(produtividade, 2)


# ============================================================
# PULVERIZAÇÃO E FUNGICIDA
# ============================================================

def calcular_pulverizadores(qtd_recomendado, tanque, vazao_pulverizador, velocidade, num_pulverizadores, espacadores):
    """
    Calcula:
      - área tratada (ha/min),
      - taxa de aplicação (L/ha),
      - dosagem por pulverizador (L).

    qtd_recomendado: dose recomendada (L/ha)
    tanque: volume do tanque (L)
    vazao_pulverizador: vazão total (L/min)
    velocidade: velocidade de deslocamento (m/min)
    num_pulverizadores: nº de bicos
    espacadores: espaçamento entre bicos (cm)
    """
    area_tratada = (velocidade * (num_pulverizadores * (espacadores / 100))) / 10_000
    taxa_aplicacao = vazao_pulverizador / area_tratada
    dosagem = (tanque * qtd_recomendado) / taxa_aplicacao
    return dosagem, taxa_aplicacao, area_tratada


def calcular_volume_fungicida(area, tanque, dosagem, taxa_aplicacao):
    """
    area: área a tratar (ha)
    tanque: volume do tanque (L)
    dosagem: dose do produto (L/ha)
    taxa_aplicacao: taxa de aplicação (L/ha)

    Retorna:
      - fungicida_ha: quantos hectares um tanque cobre
      - total_fungicida: volume total de produto necessário (L)
    """
    fungicida_ha = tanque / taxa_aplicacao
    total_fungicida = (area / fungicida_ha) * dosagem
    return fungicida_ha, total_fungicida
