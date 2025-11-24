from datetime import datetime
from typing import Dict
import os

from fastapi import FastAPI
from pydantic import BaseModel

from fase2_database.data.conexao import SQLiteDB
from fase2_database.data.crud_sensor import inserir_sensor, listar_sensores
from fase2_database.data.crud_leitura import inserir_leitura

app = FastAPI(
    title="FarmTech IoT API",
    description="API para receber dados de sensores IoT e gerenciar alertas agrícolas",
    version="1.0.0"
)


class LeituraPayload(BaseModel):
    cd_area: int
    fosforo: float | None = None
    potassio: float | None = None
    umidade: float | None = None
    ph: float | None = None
    irrigacao: float | None = None


def carregar_mapa_sensores(cursor, cd_area: int) -> Dict[tuple, int]:
    mapa = {}
    sensores = listar_sensores(cursor)
    for s in sensores:
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


def get_or_create_sensor(cursor, mapa, tp_sensor, cd_area, nm_modelo="ESP32_API"):
    chave = (tp_sensor, cd_area)
    if chave in mapa:
        return mapa[chave]
    cd_sensor = inserir_sensor(cursor, tp_sensor, nm_modelo, cd_area)
    mapa[chave] = cd_sensor
    return cd_sensor


@app.get("/")
def root():
    """Endpoint raiz - informações da API"""
    return {
        "service": "FarmTech IoT API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "health_check": "/health-check",
            "docs": "/docs",
            "iot_data": "/api/leituras/esp32"
        }
    }


@app.get("/health")
def health():
    """Health check endpoint - verificação de saúde da API"""
    try:
        # Testar conexão com banco de dados
        with SQLiteDB() as db:
            db.cursor.execute("SELECT 1")

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "service": "FarmTech IoT API"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": "disconnected",
            "error": str(e)
        }


@app.get("/health-check")
def health_check():
    """Health check endpoint alternativo"""
    return health()


@app.post("/api/leituras/esp32")
def receber_leitura(payload: LeituraPayload):
    """Recebe leituras de sensores do ESP32"""
    with SQLiteDB() as db:
        cursor = db.cursor
        mapa = carregar_mapa_sensores(cursor, payload.cd_area)

        dados = {
            "fosforo": payload.fosforo,
            "potassio": payload.potassio,
            "umidade": payload.umidade,
            "ph": payload.ph,
            "irrigacao": payload.irrigacao,
        }

        for tp, valor in dados.items():
            if valor is None:
                continue
            cd_sensor = get_or_create_sensor(cursor, mapa, tp, payload.cd_area)
            inserir_leitura(cursor, cd_sensor, datetime.now(), valor)

    return {
        "status": "ok",
        "cd_area": payload.cd_area,
        "timestamp": datetime.now().isoformat()
    }

