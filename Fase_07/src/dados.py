from Fase_07.src.fase2_database.data.conexao import SQLiteDB
from fase2_database.data.crud_cultura import *
from fase2_database.data.crud_adubacao import *
from fase2_database.data.crud_fungicida import *
from fase2_database.data.crud_leitura import *
from fase2_database.data.crud_area_plantio import *
from fase2_database.data.crud_responsavel import *
from fase2_database.data.crud_sensor import *
from fase1_calculos.calculos_fase1 import *
from validacao_dados import *
from clima_api import obter_dados_climaticos
from datetime import datetime
import traceback


def entrada_responsavel():
    """
    Captura inputs para cadastro de responsável e persiste no banco.
    """
    nome = input("Nome do responsável: ")
    telefone = input("Telefone: ")
    email = input("Email: ")
    with SQLiteDB() as db:
        cursor = db.cursor
        inserir_responsavel(cursor, {
            'nm_responsavel': nome,
            'nm_telefone': telefone,
            'nm_email': email
        })
        db.conn.commit()
    print("✅ Responsável cadastrado com sucesso!\n")


def entrada_dados():
    """
    Captura inputs para cultura, área, sensores, adubação e fungicida, e persiste no banco.
    """
    with SQLiteDB() as db:
        cursor = db.cursor
        try:
            print("\nEntrada de Dados:\n")

            # Simulação dos sensores (manual, como monitor serial do ESP32)
            if entrada_yn("Deseja registrar leitura simulada de sensores? (Y/N): ") == 'y':
                _, umidade, _, _ = obter_dados_climaticos()
                print(f"💧 Umidade coletada da API: {umidade}%")
                temperatura_solo = entrada_float("Valor de temperatura do solo estimado (°C): ")
                umidade_solo = entrada_float("Valor de umidade do solo estimado (m³/m³): ")
                fosforo = entrada_float("Valor do Fósforo: ")
                potassio = entrada_float("Valor do Potássio: ")
                nitrogenio = entrada_float("Valor do Nitrogênio: ")
                ph = entrada_float("Valor de pH estimado (0 a 14): ")

            # Dados da cultura
            tipo_cultura = entrada_opcao("Digite a cultura (soja ou milho): ", ["soja", "milho"])
            area_ha = calcular_area()
            germinacao = entrada_float("Poder germinativo das sementes (%): ")
            peso_mil_graos = entrada_float("Peso por mil grãos (g): ")

            produtividade_op = entrada_yn("Calcular produtividade esperada? (Y/N): ")
            if produtividade_op == 'y':
                if tipo_cultura == 'soja':
                    qtd_vagens = entrada_float("Quantas vagens em 10 plantas? ")
                    qtd_graos = entrada_float("Quantos grãos nas vagens? ")
                    produtividade_calc = calcular_produtividade(
                        tipo_cultura, qtd_vagens, qtd_graos, germinacao, peso_mil_graos
                    )
                else:
                    peso_graos = entrada_float("Peso médio dos grãos coletados (g): ")
                    produtividade_calc = calcular_produtividade(
                        tipo_cultura, peso_graos=peso_graos
                    )
            else:
                produtividade_calc = None

            espacamento = 0.4 if tipo_cultura == 'soja' else 0.5
            densidade = calculo_densidade(tipo_cultura, espacamento)
            taxa = calcular_semeadura(densidade, germinacao)
            peso_ha = calcular_peso_area(tipo_cultura, peso_mil_graos, germinacao)

            # Verifica responsável
            responsaveis = listar_responsaveis(cursor)
            if not responsaveis:
                print("Nenhum responsável cadastrado. Cadastre antes de continuar.")
                return
            cd_responsavel = responsaveis[0]['cd_responsavel']

            # Insere cultura
            inserir_cultura(cursor, {
                'nm_cultura': tipo_cultura,
                'tp_cultura': tipo_cultura
            })
            cd_cultura = cursor.lastrowid

            # Insere área de plantio
            inserir_area_plantio(cursor, {
                'vl_area_ha': area_ha,
                'vl_espacamento': espacamento,
                'vl_densidade': densidade,
                'vl_taxa_semeadura': taxa,
                'vl_peso_ha': peso_ha,
                'cd_cultura': cd_cultura,
                'cd_responsavel': cd_responsavel,
                'ds_produtividade': str(produtividade_calc) if produtividade_calc else None
            })
            cd_area = cursor.lastrowid

            # Registrar sensores
            if 'umidade' in locals():
                for tp, val in [
                    ('umidade', umidade),
                    ('temperatura', temperatura_solo),
                    ('fosforo', fosforo),
                    ('potassio', potassio),
                    ('nitrogenio', nitrogenio),
                    ('umidade_solo', umidade_solo),
                    ('ph', ph)
                ]:
                    cd_sensor = inserir_sensor(cursor, tp, 'Simulado', cd_area)
                    inserir_leitura(cursor, cd_sensor, datetime.now(), val)

            # Adubação
            if entrada_yn("Deseja registrar adubação? (Y/N): ") == 'y':
                if tipo_cultura == 'soja':
                    p = entrada_float("P (fósforo) resina (mg/dm³): ")
                    k = entrada_float("K (potássio) trocável (cmol/dm³): ")
                    prod_est = entrada_float("Estimativa de produção (ton/ha): ")
                    p2o5, k2o = calcular_adubo_soja(prod_est, p, k)
                    inserir_adubacao(cursor, cd_area, p2o5, k2o, None)
                else:
                    prod_est = entrada_float_intervalo(
                        "Estimativa de produção (ton/ha): ", 5, 15
                    )
                    destino = entrada_opcao(
                        "Finalidade do milho (grao ou silagem): ", ["grao", "silagem"]
                    )
                    n, p, k = calcular_adubo_milho(prod_est, destino)
                    inserir_adubacao(cursor, cd_area, p, k, n)

            # Fungicida
            if entrada_yn("Deseja registrar aplicação de fungicida? (Y/N): ") == 'y':
                nome = input("Nome do produto: ")
                velocidade = entrada_float("Velocidade do trator (m/min): ")
                tanque = entrada_float("Capacidade do tanque (L): ")
                vazao = entrada_float("Vazão do pulverizador (L/min): ")
                num_pulverizadores = entrada_float("Qtd de bicos/pulverizadores: ")
                espacadores = entrada_float("Espaçamento entre bicos (cm): ")
                qtd_lha = entrada_float("Recomendação do fabricante (L/ha): ")

                dosagem, taxa_aplic = calcular_pulverizadores(
                    tanque, qtd_lha, vazao, velocidade,
                    num_pulverizadores, espacadores
                )
                fungicida_ha, total_fungicida = calcular_volume_fungicida(
                    area_ha, tanque, dosagem, taxa_aplic
                )
                inserir_fungicida(cursor, cd_area, total_fungicida, nome)

            db.conn.commit()
            print("✅ Todos os dados foram salvos com sucesso!\n")

        except Exception:
            print("❌ Ocorreu um erro durante a operação:")
            traceback.print_exc()
            db.conn.rollback()


def listar_dados():
    """
    Exibe no console dados de culturas, aplicações e leituras.
    """
    with SQLiteDB() as db:
        cursor = db.cursor
        try:
            dados = listar_culturas_com_area(cursor)
            if not dados:
                print("Nenhuma cultura cadastrada.")
                return

            print("Culturas cadastradas:")
            for i, d in enumerate(dados):
                print(f"[{i}] Cultura: {d['nm_cultura'].capitalize()}, Área: {d['vl_area_ha']:.2f} ha")

            indice = entrada_opcao("Selecione o índice para visualizar os detalhes: ",
                                  [str(i) for i in range(len(dados))]
            )
            selecionado = dados[int(indice)]

            print(f"--- Detalhes da Cultura '{selecionado['nm_cultura'].capitalize()}' ---")
            print(f"Tipo de Cultura: {selecionado['tp_cultura']}")
            print(f"Área Total: {selecionado['vl_area_ha']:.2f} ha")
            print(f"Espaçamento: {selecionado['vl_espacamento']*100:.1f} cm")
            print(f"Densidade: {selecionado['vl_densidade']:.2f} sementes por metro")
            print(f"Taxa de Semeadura: {selecionado['vl_taxa_semeadura']:.2f} sementes por metro")
            print(f"Peso por Hectare: {selecionado['vl_peso_ha']/1000:.2f} Kg/ha")
            prod = selecionado['ds_produtividade']
            print(f"Produtividade Estimada: {prod + ' sc/ha' if prod else 'Não informada'}")

            cd_area = selecionado['cd_area']

            print("🔹 Aplicações registradas:")
            for a in listar_adubacoes(cursor):
                if a['cd_area'] == cd_area:
                    print(
                        f"  [Adubação] Data: {a['dt_aplicacao']} | Total: {a['vl_quantidade']} kg "
                        f"(P: {a['vl_fosforo']} kg, K: {a['vl_potassio']} kg, N: {a['vl_nitrogenio'] or 0} kg)"
                    )

            print("🔹 Leituras de Sensores:")
            sensores = listar_sensores(cursor)
            sensor_map = {s['cd_sensor']: s['tp_sensor'] for s in sensores if s['cd_area'] == cd_area}
            leituras = listar_leituras(cursor)
            if leituras:
                for l in leituras:
                    tp_id = l['cd_sensor']
                    if tp_id in sensor_map:
                        tipo = sensor_map[tp_id].lower()
                        unidade = {
                            'umidade': '%',
                            'temperatura': '°C',
                            'umidade_solo': 'm³/m³',
                            'fosforo': 'Fósforo',
                            'potassio': 'Potássio',
                            'nitrogenio': 'Nitrogênio',
                            'ph': 'pH'
                        }.get(tipo, '')
                        print(
                            f"  [{sensor_map[tp_id].capitalize()}] {l['dt_leitura']} | Valor: {l['vl_valor']} {unidade}"
                        )
            else:
                print("  Nenhuma leitura registrada.")

        except Exception:
            print("❌ Erro ao listar os dados:")
            traceback.print_exc()


def atualizar_dados():
    """
    Atualiza a área de plantio e, opcionalmente, adubação, fungicida ou leituras.
    """
    with SQLiteDB() as db:
        cursor = db.cursor
        try:
            dados = listar_culturas_com_area(cursor)
            if not dados:
                print("Nenhuma cultura cadastrada.")
                return
            print("Culturas cadastradas:")
            for i, d in enumerate(dados):
                print(f"[{i}] Cultura: {d['nm_cultura'].capitalize()}, Área: {d['vl_area_ha']} ha")
            idx = entrada_opcao(
                "Selecione o índice da cultura para atualizar: ",
                [str(i) for i in range(len(dados))]
            )
            sel = dados[int(idx)]
            cd_area = sel['cd_area']
            cd_cultura = sel['cd_cultura']
            if entrada_yn("Deseja recalcular a área? (Y/N): ").lower()=='y':
                nova_area = calcular_area()
            else:
                nova_area = sel['vl_area_ha']
            germinacao = entrada_float("Novo poder germinativo das sementes (%): ")
            peso_mil_graos = entrada_float("Novo peso por mil grãos (g): ")
            if entrada_yn("Calcular nova produtividade? (Y/N): ").lower()=='y':
                if sel['tp_cultura']=='soja':
                    qtd_vagens = entrada_float("Quantas vagens em 10 plantas? ")
                    qtd_graos = entrada_float("Quantos grãos nas vagens? ")
                    produtividade = calcular_produtividade(
                        sel['tp_cultura'], qtd_vagens, qtd_graos,
                        germinacao, peso_mil_graos
                    )
                else:
                    peso_graos = entrada_float("Peso médio dos grãos coletados (g): ")
                    produtividade = calcular_produtividade(
                        sel['tp_cultura'], peso_graos=peso_graos
                    )
            else:
                produtividade = sel['ds_produtividade'] if sel['ds_produtividade'] is not None else None

            espac = 0.4 if sel['tp_cultura']=='soja' else 0.5
            dens = calculo_densidade(sel['tp_cultura'], espac)
            taxa = calcular_semeadura(dens, germinacao)
            peso_ha = calcular_peso_area(sel['tp_cultura'], peso_mil_graos, germinacao)
            cursor.execute(
                '''
                UPDATE Area_Plantio
                SET vl_area_ha = ?, vl_espacamento = ?, vl_densidade = ?,
                    vl_taxa_semeadura = ?, vl_peso_ha = ?, ds_produtividade = ?
                WHERE cd_area = ?
                ''',
                (nova_area, espac, dens, taxa, peso_ha, str(produtividade) if produtividade else None, cd_area)
            )
            if entrada_yn("Deseja atualizar a adubação? (Y/N): ").lower()=='y':
                fos, pot, nit = (
                    entrada_float("Novo P (kg/ha): "),
                    entrada_float("Novo K (kg/ha): "),
                    entrada_float("Novo N (kg/ha): ")
                )
                adubs = listar_adubacoes(cursor)
                for a in adubs:
                    if a['cd_area']==cd_area:
                        atualizar_adubacao(cursor, a['cd_aplicacao'], fos, pot, nit)
            if entrada_yn("Registrar novas leituras simuladas? (Y/N): ").lower()=='y':
                _, umid, _, _ = obter_dados_climaticos()
                temperatura_solo = entrada_float("Valor de temperatura do solo estimado (°C): ")
                umidade_solo = entrada_float("Valor de umidade do solo estimado (m³/m³): ")
                fosf = entrada_float("Valor do Fósforo: ")
                pota = entrada_float("Valor do Potássio: ")
                nitr = entrada_float("Valor do Nitrogênio: ")
                phv = entrada_float("Valor de pH (0-14): ")
                for tp, val in [
                    ('umidade', umid),
                    ('temperatura', temperatura_solo),
                    ('fosforo', fosf),
                    ('potassio', pota),
                    ('nitrogenio', nitr),
                    ('umidade_solo', umidade_solo),
                    ('ph', phv)
                ]:
                    cd_s = inserir_sensor(cursor, tp, 'Simulado', cd_area)
                    inserir_leitura(cursor, cd_s, datetime.now(), val)
            db.conn.commit()
            print("✅ Atualização concluída com sucesso.")
        except Exception:
            db.conn.rollback()
            traceback.print_exc()


def deletar_dados():
    """
    Deleta cultura e registros associados.
    """
    with SQLiteDB() as db:
        cursor = db.cursor
        try:
            dados = listar_culturas_com_area(cursor)
            if not dados:
                print("Nenhuma cultura cadastrada.")
                return
            print("Culturas cadastradas:")
            for i, d in enumerate(dados):
                print(f"[{i}] Cultura: {d['nm_cultura'].capitalize()}, Área: {d['vl_area_ha']} ha")
            id_cultura = int(entrada_float("Selecione o ID da cultura a deletar: "))
            cursor.execute("DELETE FROM Aplicacao WHERE cd_area = ?", (id_cultura,))
            sensores = listar_sensores(cursor)
            for s in sensores:
                if s['cd_area']==id_cultura:
                    cursor.execute("DELETE FROM Leitura_Sensor WHERE cd_sensor = ?", (s['cd_sensor'],))
                    deletar_sensor(cursor, s['cd_sensor'])
            deletar_area_plantio(cursor, id_cultura)
            deletar_cultura(cursor, id_cultura)
            db.conn.commit()
            print("✅ Cultura e registros associados deletados.")
        except Exception:
            db.conn.rollback()
            traceback.print_exc()
