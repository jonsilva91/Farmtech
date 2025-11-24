#!/bin/bash
# deploy-ecr.sh - Push da imagem para AWS ECR

set -e

echo "☁️  Deploy para AWS ECR..."

# Variáveis (ajustar conforme sua conta AWS)
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-""}
ECR_REPOSITORY="farmtech-api"
IMAGE_TAG=${1:-latest}

# Verificar se AWS_ACCOUNT_ID foi fornecido
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "AWS_ACCOUNT_ID não definido. Tentando obter automaticamente..."
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
fi

ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FULL_IMAGE_NAME="${ECR_URI}/${ECR_REPOSITORY}"

echo "Configuração:"
echo "   Região: ${AWS_REGION}"
echo "   Account: ${AWS_ACCOUNT_ID}"
echo "   Repositório: ${ECR_REPOSITORY}"
echo "   Tag: ${IMAGE_TAG}"
echo ""

# 1. Login no ECR
echo "Autenticando no ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_URI}

# 2. Criar repositório se não existir
echo "Verificando repositório ECR..."
if ! aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${AWS_REGION} 2>/dev/null; then
    echo "Criando repositório ${ECR_REPOSITORY}..."
    aws ecr create-repository \
        --repository-name ${ECR_REPOSITORY} \
        --region ${AWS_REGION} \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
fi

# 3. Tag da imagem local
echo "Criando tag para ECR..."
docker tag farmtech-api:latest ${FULL_IMAGE_NAME}:${IMAGE_TAG}
docker tag farmtech-api:latest ${FULL_IMAGE_NAME}:latest

# 4. Push para ECR
echo "Enviando imagem para ECR..."
docker push ${FULL_IMAGE_NAME}:${IMAGE_TAG}
docker push ${FULL_IMAGE_NAME}:latest

echo ""
echo "Deploy concluído com sucesso!"
echo "Imagem disponível em:"
echo "   ${FULL_IMAGE_NAME}:${IMAGE_TAG}"
echo "   ${FULL_IMAGE_NAME}:latest"
echo ""
echo "Próximos passos:"
echo "   1. Deploy no ECS/Fargate: ./scripts/deploy-ecs.sh"
echo "   2. Ou Lambda: atualizar função com a nova imagem"
