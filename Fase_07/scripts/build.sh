#!/bin/bash
# build.sh - Build da imagem Docker da API FarmTech

set -e

echo "Iniciando build da imagem Docker..."

# Variáveis
IMAGE_NAME="farmtech-api"
VERSION=${1:-latest}
DOCKERFILE="Dockerfile"

# Navegar para o diretório raiz do projeto
cd "$(dirname "$0")/.."

echo "Construindo imagem: ${IMAGE_NAME}:${VERSION}"

# Build da imagem
docker build \
  -t ${IMAGE_NAME}:${VERSION} \
  -t ${IMAGE_NAME}:latest \
  -f ${DOCKERFILE} \
  .

echo "Build concluído com sucesso!"
echo "Imagem criada: ${IMAGE_NAME}:${VERSION}"

# Mostrar tamanho da imagem
echo ""
echo "Informações da imagem:"
docker images ${IMAGE_NAME}:${VERSION}

echo ""
echo "Para executar localmente:"
echo "   docker run -p 8000:8000 ${IMAGE_NAME}:${VERSION}"
echo ""
echo "Ou usar docker-compose:"
echo "   docker-compose up"
