import time
from datetime import datetime

import serial  # pip install pyserial

from fase2_database.data.conexao import SQLiteDB
from fase2_database.data.crud_sensor import inserir_sensor, listar_sensores
from fase2_database.data.crud_leitura import inserir_leitura


# ======== CONFIGURAÇÕES ========

SERIAL_PORT = "COM6"  
BAUD_RATE = 115200
CD_AREA = 8            # área de plantio que esse ESP32 monitora
NM_MODELO_SENSOR = "Umidade"  


# ======== PARSE DA LINHA DO ESP32 ========

def parse_linha_esp32(linha: str):
    """
    Espera algo como:
    'Fosforo: 1 | Potassio: 0 | Umidade: 43.2% | pH: 6.8 | Irrigacao: ATIVA'
    Retorna dict com valores numéricos.
    """
    linha = linha.strip()
    if not linha:
        return None

    dados = {}
    try:
        partes = [p.strip() for p in linha.split("|")]

        for p in partes:
            if p.startswith("Fosforo:"):
                dados["fosforo"] = int(p.split(":")[1].strip())
            elif p.startswith("Potassio:"):
                dados["potassio"] = int(p.split(":")[1].strip())
            elif p.startswith("Umidade:"):
                valor = p.split(":")[1].strip().replace("%", "")
                dados["umidade"] = float(valor)
            elif p.startswith("pH:") or p.startswith("pH "):
                valor = p.split(":")[1].strip()
                dados["ph"] = float(valor)
            elif p.startswith("Irrigacao:"):
                status = p.split(":")[1].strip().upper()
                dados["irrigacao"] = 1.0 if status == "ATIVA" else 0.0

        return dados if dados else None
    except Exception as e:
        print(f"[ERRO PARSE] Linha: {linha} | Erro: {e}")
        return None


# ======== MAPA DE SENSORES (USANDO SEU CRUD) ========

def carregar_mapa_sensores(cursor, cd_area):
    """
    Usa listar_sensores(cursor) pra montar um mapa:
    (tp_sensor, cd_area) -> cd_sensor
    """
    mapa = {}
    sensores = listar_sensores(cursor)

    for s in sensores:
        # sqlite3.Row ou tupla
        try:
            cd_sensor = s["cd_sensor"]
            tp_sensor = s["tp_sensor"]
            area = s["cd_area"]
        except (TypeError, KeyError):
            cd_sensor = s[0]
            tp_sensor = s[1]
            area = s[3]

        if area == cd_area:
            mapa[(tp_sensor, cd_area)] = cd_sensor

    return mapa


def get_or_create_sensor(cursor, mapa, tp_sensor, cd_area, nm_modelo=NM_MODELO_SENSOR):
    """
    Se já existir sensor (tp_sensor, cd_area) no mapa, retorna o cd_sensor.
    Senão, usa inserir_sensor do  CRUD e atualiza o mapa.
    """
    chave = (tp_sensor, cd_area)
    if chave in mapa:
        return mapa[chave]

    cd_sensor = inserir_sensor(cursor, tp_sensor, nm_modelo, cd_area)
    mapa[chave] = cd_sensor
    return cd_sensor


# ======== GRAVAÇÃO NO BANCO (USANDO crud_leitura) ========

def gravar_leituras_no_banco(dados: dict, cd_area: int):
    """
    dados: dict com chaves como 'umidade', 'ph', 'fosforo', 'potassio', 'irrigacao'
    """
    with SQLiteDB() as db:
        cursor = db.cursor

        # Mapa de sensores para essa área
        mapa_sensores = carregar_mapa_sensores(cursor, cd_area)

        for tp, valor in dados.items():
            if valor is None:
                continue

            cd_sensor = get_or_create_sensor(cursor, mapa_sensores, tp, cd_area)
            inserir_leitura(cursor, cd_sensor, datetime.now(), valor)
        # commit é feito pelo __exit__ do SQLiteDB


# ======== LOOP PRINCIPAL ========

def loop_esp32():
    print(f"Conectando ao ESP32 em {SERIAL_PORT} @ {BAUD_RATE}...")
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print("Conectado. Lendo dados... (Ctrl+C para sair)")
        time.sleep(2)  # tempo pra estabilizar depois do reset

        while True:
            try:
                raw = ser.readline()
                if not raw:
                    continue

                linha = raw.decode("utf-8", errors="ignore")
                print(f"[SERIAL] {linha.strip()}")

                dados = parse_linha_esp32(linha)
                if dados:
                    gravar_leituras_no_banco(dados, CD_AREA)
                    print(f"[OK] Gravado no banco: {dados}")

            except KeyboardInterrupt:
                print("Interrompido pelo usuário.")
                break
            except Exception as e:
                print(f"[ERRO LOOP] {e}")
                time.sleep(1)


if __name__ == "__main__":
    loop_esp32()
