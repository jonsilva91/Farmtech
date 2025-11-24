#!/bin/bash
# run-local.sh - Executa API + PostgreSQL + Dashboard localmente

set -e

cd "$(dirname "$0")/.."

# Verificar docker compose
if ! docker compose version &> /dev/null; then
    echo "Erro: docker compose não encontrado"
    exit 1
fi

# Criar .env se não existir
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Arquivo .env criado. Configure as credenciais AWS antes de continuar."
        exit 0
    fi
fi

echo "Iniciando API + PostgreSQL + Dashboard..."
echo ""
echo "Serviços disponíveis:"
echo "  Dashboard:  http://localhost:8501"
echo "  API:        http://localhost:8000/docs"
echo "  Health:     http://localhost:8000/health"
echo "  PostgreSQL: localhost:5432"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""
echo "========================================="
echo ""

docker compose up api db dashboard
