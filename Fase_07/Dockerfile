# ============================================
# Stage 1: Builder - Instala dependências
# ============================================
FROM python:3.12-slim as builder

# Variáveis de ambiente para otimização
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Instala dependências do sistema necessárias para build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas requirements para cache eficiente
COPY requirements-api.txt .

# Instala dependências Python em um diretório isolado
RUN pip install --user --no-warn-script-location -r requirements-api.txt


# ============================================
# Stage 2: Runtime - Imagem final leve
# ============================================
FROM python:3.12-slim

# Metadados
LABEL maintainer="FarmTech - Equipe Rocket"
LABEL description="FastAPI IoT API - FarmTech Fase 07"
LABEL version="1.0.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

# Diretório de trabalho
WORKDIR $APP_HOME

# Copia dependências do builder para /usr/local (disponível globalmente)
COPY --from=builder /root/.local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /root/.local/bin /usr/local/bin

# Copia código da aplicação
COPY src/fase2_database ./fase2_database
COPY src/fase3_iot ./fase3_iot
COPY src/aws_alerts.py .

# Cria diretório para o banco SQLite
RUN mkdir -p fase2_database/config

# Cria usuário não-root para segurança
RUN groupadd -r farmtech && useradd -r -g farmtech farmtech && \
    chown -R farmtech:farmtech $APP_HOME

# Troca para usuário não-root
USER farmtech

# Expõe porta da API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Comando padrão - inicia FastAPI com Uvicorn
CMD ["uvicorn", "fase3_iot.api_leituras:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
