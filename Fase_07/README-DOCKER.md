# 🐳 Docker - FarmTech API

Documentação completa para dockerização e deploy da API FastAPI do projeto FarmTech Fase_07.

---

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Estrutura de Arquivos](#estrutura-de-arquivos)
- [Quick Start](#quick-start)
- [Build Manual](#build-manual)
- [Execução Local](#execução-local)
- [Docker Compose](#docker-compose)
- [Deploy na AWS](#deploy-na-aws)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Pré-requisitos

### Ferramentas Necessárias:

- **Docker** >= 24.0
- **Docker Compose** >= 2.20
- **AWS CLI** >= 2.0 (para deploy)
- **jq** (para testes - opcional)

### Instalação:

```bash
# Verificar versões
docker --version
docker-compose --version
aws --version

# Instalar Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Instalar AWS CLI
pip install awscli --upgrade
```

---

## 📁 Estrutura de Arquivos

```
Fase_07/
├── Dockerfile                  # Imagem multi-stage otimizada
├── docker-compose.yml          # Ambiente local completo
├── .dockerignore              # Arquivos excluídos do build
├── .env.example               # Template de variáveis de ambiente
├── requirements-api.txt       # Dependências mínimas da API
├── scripts/
│   ├── build.sh              # Script de build
│   ├── run-local.sh          # Execução local rápida
│   ├── deploy-ecr.sh         # Push para AWS ECR
│   └── test-api.sh           # Testes automatizados
└── docker/
    └── init-db.sql           # Inicialização do PostgreSQL
```

---

## 🚀 Quick Start

### 1️⃣ Configurar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar com suas credenciais AWS
nano .env
```

Mínimo necessário no `.env`:
```bash
AWS_SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:farmtech-alerts
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=abc123...
```

### 2️⃣ Build e Execução (Modo Rápido)

```bash
# Build da imagem
./scripts/build.sh

# Executar localmente
./scripts/run-local.sh

# Testar
./scripts/test-api.sh
```

### 3️⃣ Acessar a API

- **Swagger UI:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Endpoint IoT:** http://localhost:8000/api/leituras/esp32

---

## 🔨 Build Manual

### Build Simples:

```bash
docker build -t farmtech-api:latest .
```

### Build com Tag Específica:

```bash
docker build -t farmtech-api:v1.0.0 .
```

### Build Multi-Plataforma (ARM + x86):

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t farmtech-api:latest \
  --push .
```

### Verificar Imagem:

```bash
docker images farmtech-api
docker inspect farmtech-api:latest
```

### Informações da Imagem:

```bash
# Tamanho
docker images farmtech-api:latest --format "{{.Size}}"

# Camadas
docker history farmtech-api:latest
```

---

## 💻 Execução Local

### Método 1: Docker Run (Simples)

```bash
docker run -d \
  --name farmtech-api \
  -p 8000:8000 \
  --env-file .env \
  farmtech-api:latest
```

### Método 2: Com Volume (Persistir DB SQLite)

```bash
docker run -d \
  --name farmtech-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/src/fase2_database/config:/app/fase2_database/config \
  farmtech-api:latest
```

### Método 3: Modo Interativo (Debug)

```bash
docker run -it --rm \
  -p 8000:8000 \
  --env-file .env \
  farmtech-api:latest \
  /bin/bash
```

### Gerenciar Container:

```bash
# Ver logs
docker logs -f farmtech-api

# Ver logs das últimas 100 linhas
docker logs --tail 100 farmtech-api

# Parar
docker stop farmtech-api

# Reiniciar
docker restart farmtech-api

# Remover
docker rm -f farmtech-api
```

---

## 🐳 Docker Compose

### Ambiente Completo (API + PostgreSQL + pgAdmin)

```bash
# Subir todos os serviços
docker-compose up -d

# Subir apenas API e banco
docker-compose up -d api db

# Com reconstrução
docker-compose up -d --build

# Ver logs
docker-compose logs -f api

# Parar tudo
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados!)
docker-compose down -v
```

### Serviços Disponíveis:

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **API** | http://localhost:8000 | - |
| **PostgreSQL** | localhost:5432 | user: `farmtech_user` / pass: `farmtech_password` |
| **pgAdmin** | http://localhost:5050 | email: `admin@farmtech.com` / pass: `admin123` |

### Conectar ao Banco via pgAdmin:

1. Acesse http://localhost:5050
2. Login com credenciais acima
3. Add Server:
   - **Name:** FarmTech Local
   - **Host:** `db` (nome do serviço no docker-compose)
   - **Port:** `5432`
   - **Database:** `farmtech`
   - **Username:** `farmtech_user`
   - **Password:** `farmtech_password`

---

## ☁️ Deploy na AWS

### 1️⃣ Deploy no ECR (Container Registry)

```bash
# Configurar AWS CLI
aws configure

# Build local
./scripts/build.sh

# Push para ECR
./scripts/deploy-ecr.sh
```

O script faz automaticamente:
- ✅ Autenticação no ECR
- ✅ Cria repositório se não existir
- ✅ Tag da imagem
- ✅ Push da imagem

### 2️⃣ Deploy no ECS Fargate

#### Opção A: Via Console AWS

1. **Criar Cluster ECS:**
   - Nome: `farmtech-cluster`
   - Tipo: Fargate

2. **Criar Task Definition:**
   - Nome: `farmtech-api-task`
   - Container:
     - Imagem: `123456789012.dkr.ecr.us-east-1.amazonaws.com/farmtech-api:latest`
     - CPU: 256
     - Memória: 512 MB
     - Porta: 8000
   - Environment Variables: Adicionar do .env

3. **Criar Service:**
   - Cluster: `farmtech-cluster`
   - Task: `farmtech-api-task`
   - Tipo: Fargate
   - Desired tasks: 1
   - Load Balancer: Opcional (recomendado)

#### Opção B: Via CLI

```bash
# Registrar Task Definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Criar Service
aws ecs create-service \
  --cluster farmtech-cluster \
  --service-name farmtech-api-service \
  --task-definition farmtech-api-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### 3️⃣ Deploy no Lambda (Alternativa Serverless)

```bash
# Criar função Lambda com imagem de container
aws lambda create-function \
  --function-name farmtech-api \
  --package-type Image \
  --code ImageUri=123456789012.dkr.ecr.us-east-1.amazonaws.com/farmtech-api:latest \
  --role arn:aws:iam::123456789012:role/lambda-execution-role \
  --timeout 30 \
  --memory-size 512

# Atualizar função
aws lambda update-function-code \
  --function-name farmtech-api \
  --image-uri 123456789012.dkr.ecr.us-east-1.amazonaws.com/farmtech-api:latest
```

**Nota:** Para Lambda, ajustar o Dockerfile para usar `mangum` como handler.

---

## 🧪 Testes

### Script Automatizado:

```bash
./scripts/test-api.sh http://localhost:8000
```

### Testes Manuais:

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# Enviar leitura de teste
curl -X POST http://localhost:8000/api/leituras/esp32 \
  -H "Content-Type: application/json" \
  -d '{
    "cd_area": 1,
    "fosforo": 15.5,
    "potassio": 120.0,
    "umidade": 35.0,
    "ph": 5.0,
    "irrigacao": 0.0
  }'

# Ver documentação interativa
open http://localhost:8000/docs
```

### Testes de Carga (ApacheBench):

```bash
# Instalar ab
sudo apt-get install apache2-utils

# 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:8000/health
```

---

## 🔍 Troubleshooting

### Problema: Build falha com erro de dependências

**Solução:**
```bash
# Limpar cache do Docker
docker builder prune -a

# Build sem cache
docker build --no-cache -t farmtech-api:latest .
```

### Problema: Container não inicia

**Diagnóstico:**
```bash
# Ver logs detalhados
docker logs farmtech-api

# Executar em modo interativo
docker run -it --rm farmtech-api:latest /bin/bash

# Verificar dentro do container
ls -la /app
python -c "from fase3_iot.api_leituras import app; print('OK')"
```

### Problema: Erro de conexão com banco

**Solução:**
```bash
# Verificar se container do DB está rodando
docker-compose ps

# Ver logs do PostgreSQL
docker-compose logs db

# Testar conexão manual
docker-compose exec db psql -U farmtech_user -d farmtech
```

### Problema: AWS SNS não envia alertas

**Diagnóstico:**
```bash
# Verificar variáveis de ambiente no container
docker exec farmtech-api env | grep AWS

# Testar credenciais AWS
docker exec farmtech-api aws sns list-topics --region us-east-1

# Ver logs de alerta
docker logs farmtech-api | grep -i alerta
```

### Problema: Permissões no volume

**Solução:**
```bash
# Ajustar permissões
sudo chown -R 1000:1000 src/fase2_database/config

# Ou criar volume com permissões corretas
docker volume create farmtech-db
```

---

## 📊 Monitoramento

### Uso de Recursos:

```bash
# Stats em tempo real
docker stats farmtech-api

# Uso de disco
docker system df

# Informações detalhadas
docker inspect farmtech-api
```

### Health Check Manual:

```bash
# Verificar saúde do container
docker inspect --format='{{.State.Health.Status}}' farmtech-api

# Ver histórico de health checks
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' farmtech-api
```

---

## 🧹 Limpeza

```bash
# Parar e remover container
docker rm -f farmtech-api

# Remover imagem
docker rmi farmtech-api:latest

# Limpar tudo relacionado ao projeto
docker-compose down -v
docker rmi farmtech-api:latest

# Limpeza geral do Docker
docker system prune -a --volumes
```

---

## 📚 Referências

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [AWS ECS Fargate](https://docs.aws.amazon.com/AmazonECS/latest/userguide/what-is-fargate.html)

---

## 🆘 Suporte

Para issues e dúvidas:
- **GitHub Issues:** https://github.com/jonsilva91/FarmTech/issues
- **Email:** admin@farmtech.com

---

**FarmTech - Equipe Rocket** 🚀
