#!/bin/bash
# test-api.sh - Testa a API localmente

set -e

API_URL=${1:-http://localhost:8000}

echo "Testando API FarmTech"
echo "URL: ${API_URL}"
echo ""

# 1. Root endpoint
echo "1. Root Endpoint"
curl -s ${API_URL}/ | jq '.' || curl -s ${API_URL}/
echo ""

# 2. Health check
echo "2. Health Check (/health)"
curl -s ${API_URL}/health | jq '.' || curl -s ${API_URL}/health
echo ""

# 3. Health check alternativo
echo "3. Health Check (/health-check)"
curl -s ${API_URL}/health-check | jq '.' || curl -s ${API_URL}/health-check
echo ""

# 4. Enviar leitura de teste
echo "4. Enviando Leitura de Teste"
curl -s -X POST ${API_URL}/api/leituras/esp32 \
    -H "Content-Type: application/json" \
    -d '{
        "cd_area": 1,
        "fosforo": 15.5,
        "potassio": 120.0,
        "umidade": 35.0,
        "ph": 5.0,
        "irrigacao": 0.0
    }' | jq '.' || curl -s -X POST ${API_URL}/api/leituras/esp32 \
    -H "Content-Type: application/json" \
    -d '{"cd_area":1,"fosforo":15.5,"potassio":120.0,"umidade":35.0,"ph":5.0,"irrigacao":0.0}'
echo ""

echo "Testes concluidos!"
echo ""
echo "Documentacao: ${API_URL}/docs"
echo ""
