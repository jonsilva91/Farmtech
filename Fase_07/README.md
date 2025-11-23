# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
  <a href="https://www.fiap.com.br/">
    <img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" border="0" width="40%" height="40%">
  </a>
</p>

<br>

# FarmTech — Fase 07

## Equipe Rocket

## 👨‍🎓 Integrantes

- <a href="https://www.linkedin.com/in/jonas-silva-0a659892/">Jonas Luis da Silva</a>
- <a href="https://www.linkedin.com/in/renan-francisco-de-paula-b3320915b/overlay/about-this-profile/">Renan Francisco de Paula</a>
- <a href="https://www.linkedin.com/in/jo%C3%A3o-vitor-severo-oliveira-87904134b/">João Vitor Severo Oliveira</a>
- <a href="https://www.linkedin.com/in/isagomesferreira/">Isabelle Gomes Ferreira</a>
- <a href="https://www.linkedin.com/in/edson-henrique-felix-batista-a00191123/">Edson Henrique Felix Batista</a>

## 👩‍🏫 Professores

**Tutor:** <a href="https://www.linkedin.com/company/inova-fusca">Lucas Gomes Moreira</a>  
**Coordenador:** <a href="https://www.linkedin.com/company/inova-fusca">André Godoi Chiovato</a>

---

--

> **Importante:** este README da raiz do projeto FarmTech funciona como **guia de navegação** da Fase 07.

---

## 🔗 Links principais

- **Repositório:** `https://github.com/jonsilva91/FarmTech`
- **Vídeo geral da Fase 07 (integração do sistema):** _[inserir link do vídeo não listado aqui]_

---

## 📁 Estrutura geral de pastas

```bash
FarmTech/
├── Fase_01/                  # Protótipo inicial: cálculos agronômicos e CLI
├── Fase_02/                  # Modelagem de dados, MER/DER e scripts SQL
├── Fase_03/                  # Integração IoT + banco (ESP32 + SQLite)
├── Fase_04/                  # Dashboard inicial (Streamlit) + ML local
├── Fase_05/                  # ML + Cloud (AWS) — VER README ESPECÍFICO
├── Fase_06/                  # Visão Computacional (YOLO) — VER README ESPECÍFICO
├── Fase_07/
   └── src/
       ├── Home.py           # Dashboard integrado (Streamlit)
       ├── pages/            # Páginas por fase (02, 04, 06...)
       ├── fase2_database/   # Conexão e CRUDs (SQLite)
       ├── fase3_iot/        # API FastAPI + scripts série para ESP32
       ├── model/            # Modelos de ML (solo + fertilizante)
       ├── clima_api.py      # Integração com API meteorológica
       ├── fase06_visao      # (visão computacional)
       ├── aws_alert.py      # (Alertas AWS)
       └── assets/
          └── logo-fiap.png
```

> Observação: as pastas `Fase_05` e `Fase_06` possuem **READMEs próprios**, notebooks e arquivos pesados
> (datasets, imagens YOLO etc.). Aqui só deixamos o link e o contexto para navegação.

---

# 🧭 Visão geral por fase

## 📐 Fase 01 — Cálculos Agronômicos e Base de Dados Inicial

**Objetivo:** construir a base lógica agronômica do sistema, permitindo:

- Cálculo de **área de plantio** em diferentes formatos de talhão (retângulo, círculo, triângulo, trapézio e fórmula personalizada), sempre convertendo para **hectares (ha)**.
- Cálculo de **adubação para soja e milho** (N, P₂O₅, K₂O) com base em produtividade esperada e parâmetros de solo.
- Cálculos de **densidade de plantas**, **taxa de semeadura**, **peso de grãos por hectare** e **produtividade estimada**.

Na Fase 07, essa lógica de negócio foi consolidada em funções puras no módulo:

- `Fase_07/src/calculos.py`

Essas funções deixam de ser apenas CLI e passam a ser **reutilizáveis tanto pelo Streamlit quanto por APIs ou outros serviços**, garantindo a continuidade do raciocínio da Fase 01 dentro do sistema integrado.

---

## 🗃️ Fase 02 — Banco de Dados Estruturado (MER, DER e CRUD)

**Objetivo:** sair de estruturas soltas (JSON/variáveis) e consolidar um **banco relacional** para o ecossistema FarmTech.

Principais entregas:

- Modelagem conceitual e lógica (**MER/DER**) com tabelas como:
  - `Cultura`
  - `Area_Plantio`
  - `Responsavel`
  - `Sensor`
  - `Leitura_Sensor`
  - `Aplicacao` (adubação e fungicidas)
  - `Clima`
- Scripts de criação de tabela (SQLite) e **CRUDs em Python**:
  - `fase2_database/data/conexao.py` → classe `SQLiteDB` (context manager para abrir/fechar conexões).
  - `fase2_database/data/crud_cultura.py` → cadastro de culturas e vínculo com áreas.
  - `fase2_database/data/crud_responsavel.py` → manutenção de responsáveis.
  - `fase2_database/data/crud_sensor.py` → cadastro de sensores por área.
  - `fase2_database/data/crud_leitura.py` → leituras de sensores.
  - `fase2_database/data/crud_adubacao.py` e `crud_fungicida.py` → registro de aplicações via tabela `Aplicacao`.

Na Fase 07, este banco é **reutilizado diretamente** pelo dashboard, sem refazer lógica:

- Toda a leitura e escrita (Streamlit, API, ESP32) passa pela mesma base SQLite.

---

## 🌱 Fase 03 — IoT e Automação Inteligente (ESP32 + Banco)

**Objetivo:** conectar o mundo físico ao digital: sensores em campo, ESP32 e banco de dados.

Entregas principais:

- Firmware em C++/Arduino rodando no **ESP32** (via PlatformIO) com:
  - Leitura de **DHT22** (temperatura e umidade do ar).
  - Simulação de NPK (nitrogênio, fósforo, potássio) no LCD I2C.
  - LEDs de alerta (umidade baixa / temperatura alta).
  - Interface serial para escolha de plot (NPK ou Temp/Umidade).
- CRUD de leituras:
  - `fase2_database/data/crud_leitura.py` → gravação na tabela `Leitura_Sensor`.
- Script de integração serial (Fase anterior):
  - `fase3_iot/esp32_serial.py` → lia a saída serial e persistia no banco.

### 🔁 Evolução na Fase 07 — ESP32 → FastAPI → Banco

Na Fase 07, o fluxo foi modernizado:

1. O ESP32 continua lendo/simulando sensores, mas agora envia os dados via **HTTP (JSON)**:

   - Usa `WiFi.h` + `HTTPClient.h`.
   - Envia para o endpoint: `POST /api/leituras/esp32`.
   - Payload inclui: `cd_area`, `fosforo`, `potassio`, `umidade`, `ph`, `irrigacao`.

2. No backend Python, foi criada uma **API com FastAPI**:

   - Módulo: `fase3_iot/api_leituras.py`
   - Endpoint principal: `POST /api/leituras/esp32`
   - Converte o JSON em leituras na tabela `Leitura_Sensor` e registra o estado da área.

3. O dashboard Streamlit lê diretamente essas leituras do banco (mesma base da Fase 02), unificando o ecossistema.

> Resultado: a Fase 03 deixa de ser "script isolado" e passa a ser um **serviço IoT web-ready**, integrado aos modelos de ML e à interface da Fase 04/07.

---

## 📊 Fase 04 — Dashboard Interativo + ML Local

**Objetivo:** criar uma **camada de visualização e inteligência** em cima dos dados de sensores e do solo.

Componentes principais (agora consolidados em `Fase_07/src`):

- **Dashboard Streamlit**

  - `Home.py` → página principal da Fase 07, que incorpora e expande a lógica original da Fase 04.
  - `pages/01_Fase 02 - Cadastro Cultura Área.py` → cadastro de culturas, áreas e responsáveis (usando CRUDs da Fase 02).
  - `pages/02_Fase 04 - Regressao de Umidade.py` → visualização de leituras e regressão de umidade/volume (solo).
  - `pages/03_Fase 04 - Classificacao Fertilizantes.py` → sugestão de fertilizante com base em NPK e condições.
  - `pages/04_Fase 06 - Visao Computacional.py` → integração com o resultado do YOLO (Fase 06).

- **Modelos de ML para solo (regressão)**

  - Pasta: `Fase_07/src/model/`
  - Arquivos: `soil_model_30cm.pkl`, `soil_model_60cm.pkl`, ..., `soil_model_150cm.pkl`.
  - Carregados via `joblib` com cache em `load_models()`.
  - Entrada: umidade e temperatura (do solo ou do ar, dependendo da disponibilidade).
  - Saída: conteúdo volumétrico de água (CVA) previsto em m³/m³.

- **Modelo de recomendação de fertilizante**
  - Arquivo: `xgb_fertilizer_recommendation.pkl`.
  - Estrutura: dicionário com `model`, `scaler`, `le_crop`, `le_fert`, `features`.
  - Página de Streamlit monta o vetor de entrada com:
    - Temperatura
    - Umidade do solo
    - Nitrogênio (N)
    - Fósforo (P)
    - Potássio (K)
  - O modelo retorna uma recomendação de fertilizante, exibida como métrica na interface.

> Na Fase 07, todo esse conteúdo é reorganizado em um **dashboard único**, que conversa com banco, API IoT e visão computacional.

---

## ☁️ Fase 05 — ML + Cloud (AWS)

> **Observação:** esta fase possui um README **próprio** dentro da pasta `Fase_05/`, seguindo o padrão oficial FIAP.

Resumo (para navegação):

- **Entrega 1 (ML):**

  - EDA do dataset `crop_yield.csv`.
  - Clusterização de padrões de produtividade.
  - Desenvolvimento e comparação de 5 modelos de regressão para prever rendimento (t/ha).
  - Notebook principal com todas as análises.

- **Entrega 2 (Cloud – AWS):**
  - Estimativa de custos para hospedar API + ML na AWS.
  - Comparação de regiões (`us-east-1` × `sa-east-1`).
  - Justificativa de escolha de região (latência, compliance, custo).
  - Prints do AWS Pricing Calculator.

👉 **Para detalhes completos:** ver `Fase_05/README.md` e o notebook listado lá.

_(Espaço reservado para acrescentar mais links específicos da Fase 05, se necessário pelo enunciado da Fase 07.)_

---

## 🖼️ Fase 06 — Visão Computacional (YOLO)

> **Observação:** assim como a Fase 05, a Fase 06 tem um README próprio dentro de `Fase_06/`.

Resumo (para navegação):

- Implementação de um pipeline de **visão computacional** com YOLO:

  - Dataset exemplo (gatos/cachorros) + adaptação conceitual para pragas/doenças em lavoura.
  - Organização de `dataset/train` e `dataset/test` com imagens e labels YOLO.
  - Notebooks como `darknet_yolo.ipynb` / `cats_dogs_cnn.ipynb` / `yolo_model.ipynb`.

- Resultado integrado ao sistema na Fase 07:
  - Página `pages/04_Fase 06 - Visao Computacional.py` faz a ponte entre o modelo de detecção e o dashboard.
  - Espaço para exibir imagens, detecções e possíveis alertas de saúde da plantação.

👉 **Para detalhes completos:** ver `Fase_06/README.md` e os notebooks de YOLO.

_(Espaço reservado para descrever, se necessário, a integração futura com AWS Rekognition – opção de "Ir Além".)_

---

## 🌾 Fase 07 — Consolidação do Sistema (Dashboard + API + IoT)

**Objetivo:** integrar todas as fases anteriores em um **único sistema de gestão agrícola**, pronto para ser adaptado a outros setores.

### 🔧 Principais componentes

- **Dashboard principal (Home)**

  - Arquivo: `Fase_07/src/Home.py`
  - Funções:
    - Selecionar cultura e área de plantio.
    - Visualizar leituras de sensores (pH, NPK, umidade, temperatura) por área.
    - Exibir métricas climáticas em tempo real (API de clima).
    - Mostrar previsão de conteúdo de água no solo (modelos de solo).
    - Indicar status de irrigação com base na decisão da função `decidir_irriga()`.
    - Integrar com recomendação de fertilizante e visão computacional via páginas.

- **Páginas de navegação (sidebar)**

  - `01_Fase 02 - Cadastro Cultura Área.py` → interface gráfica para os CRUDs de Cultura/Área/Responsável (Fase 02).
  - `02_Fase 04 - Regressao de Umidade.py` → gráficos e modelos de solo (Fase 04).
  - `03_Fase 04 - Classificacao Fertilizantes.py` → recomendação de fertilizantes (Fase 04 + dados de sensores).
  - `04_Fase 06 - Visao Computacional.py` → integrações com a Fase 06.

- **Banco de dados (reuso Fase 02/03)**

  - `fase2_database/data/conexao.py` → `SQLiteDB` com caminho centralizado para o `.db`.
  - CRUDs de cultura, responsáveis, sensores, leituras, aplicações e clima reaproveitados.

- **API IoT (FastAPI)**

  - `fase3_iot/api_leituras.py`:
    - Endpoint `POST /api/leituras/esp32` recebendo JSON do ESP32.
    - Converte o JSON em registros na tabela `Leitura_Sensor` (e tabelas auxiliares, se necessário).
    - Pode evoluir para gerar **alertas de irrigação ou adubação** com base em thresholds.

- **Firmware ESP32**

  - Código em C++/Arduino, responsável por:
    - Ler DHT22 (quando disponível) ou simular temperatura/umidade.
    - Simular valores de NPK.
    - Exibir dados no LCD I2C.
    - Definir `cd_area` no código para associar o dispositivo a uma área do banco.
    - Enviar leituras periódicas via HTTP para o endpoint FastAPI.

- **Modelos de ML**
  - Solo: regressão para previsão de CVA em várias profundidades (30–150 cm).
  - Fertilizante: classificação via XGBoost (ou similar) com scaler + encoders.

### ☁️ Espaço reservado — Serviço de Alerta na AWS (Fase 07, Entrega 2)

Conforme o enunciado da Fase 07, há uma segunda parte de entrega envolvendo **mensageria na AWS** (e-mail ou SMS para funcionários da fazenda, com alertas de sensor ou visão computacional).

> **Espaço reservado:**
>
> - Descrever aqui, depois de implementado:
>   - Arquitetura escolhida (SNS, SQS, Lambda, etc.).
>   - Critérios para disparo de alerta (ex.: umidade abaixo de X, praga detectada, etc.).
>   - Prints do console da AWS e fluxo fim a fim.
>   - Link do vídeo demonstrando a mensageria.

---

# ▶️ Como executar a Fase 07 (ambiente local)

## 1️⃣ Clonar o repositório

```bash
git clone https://github.com/jonsilva91/FarmTech.git
cd FarmTech/Fase_07/src
```

## 2️⃣ Criar e ativar ambiente virtual

```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# ou Windows (CMD)
.\.venv\Scripts\activate

# ou Linux/Mac
# source .venv/bin/activate
```

## 3️⃣ Instalar dependências

Se existir `requirements.txt` na pasta `src/`:

```bash
pip install -U pip
pip install -r requirements.txt
```

Caso contrário, instale os principais pacotes manualmente:

```bash
pip install streamlit fastapi uvicorn[standard] pandas numpy matplotlib joblib scikit-learn requests
```

## 4️⃣ Iniciar a API (FastAPI)

Em um terminal (dentro de `Fase_07/src`):

```bash
uvicorn fase3_iot.api_leituras:app --reload --host 0.0.0.0 --port 8000
```

- Documentação interativa (Swagger): `http://127.0.0.1:8000/docs`
- Endpoint principal usado pelo ESP32: `POST /api/leituras/esp32`

## 5️⃣ Iniciar o dashboard (Streamlit)

Em outro terminal, também em `Fase_07/src`:

```bash
streamlit run Home.py
```

- Acesse em: `http://localhost:8501`
- Use a sidebar para navegar entre:
  - **Home (Fase 07)**
  - **Fase 02 - Cadastro Cultura Área**
  - **Fase 04 - Regressão de Umidade**
  - **Fase 04 - Classificação Fertilizantes**
  - **Fase 06 - Visão Computacional**

## 6️⃣ Conectar o ESP32 (opcional / demo físico)

1. Compilar e enviar o firmware para o ESP32 (via PlatformIO ou Arduino IDE), ajustando:
   - SSID e senha do Wi-Fi.
   - IP da máquina que roda o FastAPI na constante `API_URL`.
   - `CD_AREA` correspondente à área cadastrada no banco.
2. Com o FastAPI rodando, o ESP32 enviará leituras periódicas.
3. No Streamlit, selecione a área associada ao dispositivo e acompanhe as leituras em tempo quase real.

---

# 🗃 Histórico de versões (resumo)

- **0.7.0 — Fase 07 (2025)**

  - Integração completa das Fases 01–06 em um único dashboard (Streamlit).
  - Criação da API FastAPI para receber leituras de ESP32 via HTTP.
  - Reorganização dos módulos de cálculo (`calculos.py`) para uso em UI e serviços.
  - Integração dos modelos de solo e fertilizante na interface.

- **0.6.0 — Fase 06**

  - Implementação do pipeline de visão computacional com YOLO.
  - Organização de datasets, labels e notebooks de treinamento e testes.

- **0.5.0 — Fase 05**

  - Modelagem de regressão adicional para produtividade agrícola.
  - Estimativa de custos em AWS (EC2 + S3) e justificativa de região.

- **0.4.0 — Fase 04**

  - Primeira versão do dashboard com Streamlit.
  - Integração inicial de modelos de ML locais para irrigação e fertilização.

- **0.3.0 — Fase 03**

  - Integração de ESP32 com sensores.
  - CRUD de leituras e leitura via serial.

- **0.2.0 — Fase 02**

  - Banco relacional em SQLite com MER/DER e CRUDs.

- **0.1.0 — Fase 01**
  - Cálculos agronômicos iniciais (área, adubação, densidade, produtividade).

---

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1">

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/">
<a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por
<a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sob
<a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.
</p>
