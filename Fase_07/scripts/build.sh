#!/bin/bash
# build.sh - Build da imagem Docker da API FarmTech

set -e

echo "Iniciando build da imagem Docker..."

docker build -t farmtech/rocket .

echo "Tagging e enviando a imagem para o Amazon ECR..."

docker tag farmtech/rocket:latest 058057616525.dkr.ecr.us-east-1.amazonaws.com/farmtech/rocket:latest

echo "Fazendo push da imagem para o ECR..."

docker push 058057616525.dkr.ecr.us-east-1.amazonaws.com/farmtech/rocket:latest

echo "Build e push concluídos com sucesso!"