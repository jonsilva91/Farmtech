# Quick Start - FarmTech Docker

## Configuração Inicial

```bash
# 1. Copiar template de variáveis
cp .env.example .env

# 2. Editar credenciais AWS (opcional para testes locais)
nano .env
```

## Executar

```bash
# Modo padrão: API + PostgreSQL + Dashboard
./scripts/run-local.sh
```

## Acessar

- **Dashboard Streamlit:** http://localhost:8501
- **API Swagger:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **PostgreSQL:** localhost:5432
- **pgAdmin:** http://localhost:5050 (opcional)

## Gerenciar

```bash
# Ver logs
./scripts/logs.sh          # API
./scripts/logs.sh db       # PostgreSQL

# Status
./scripts/status.sh

# Parar
./scripts/stop.sh          # Parar containers
./scripts/stop.sh down     # Remover containers
./scripts/stop.sh clean    # Remover tudo (APAGA DADOS)
```

## Build e Deploy

```bash
# Build local
./scripts/build.sh

# Testar
./scripts/test-api.sh

# Deploy AWS ECR
./scripts/deploy-ecr.sh
```

## Comandos Docker Compose Diretos

```bash
docker-compose up -d              # Iniciar
docker-compose down               # Parar
docker-compose ps                 # Status
docker-compose logs -f api        # Logs
docker-compose restart api        # Restart
docker-compose exec api bash      # Shell
```

## Estrutura de Scripts

```
scripts/
├── run-local.sh    # Iniciar serviços
├── stop.sh         # Parar serviços
├── logs.sh         # Ver logs
├── status.sh       # Ver status
├── build.sh        # Build imagem
├── test-api.sh     # Testar API
└── deploy-ecr.sh   # Deploy AWS
```

## Troubleshooting

```bash
# Limpar tudo e recomeçar
docker-compose down -v
docker system prune -f
./scripts/run-local.sh rebuild

# Ver logs de erro
docker-compose logs api

# Verificar saúde do container
docker-compose ps
docker inspect farmtech-api
```
