-- init-db.sql
-- Script de inicialização do banco PostgreSQL para FarmTech

-- Ativar extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Schema principal
CREATE SCHEMA IF NOT EXISTS farmtech;

SET search_path TO farmtech, public;

-- Tabela: Cultura
CREATE TABLE IF NOT EXISTS Cultura (
    cd_cultura SERIAL PRIMARY KEY,
    nm_cultura VARCHAR(100) NOT NULL UNIQUE,
    ds_cultura TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Responsavel
CREATE TABLE IF NOT EXISTS Responsavel (
    cd_responsavel SERIAL PRIMARY KEY,
    nm_responsavel VARCHAR(150) NOT NULL,
    nr_cpf VARCHAR(14) UNIQUE,
    nr_telefone VARCHAR(20),
    ds_email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Area_Plantio
CREATE TABLE IF NOT EXISTS Area_Plantio (
    cd_area SERIAL PRIMARY KEY,
    nm_area VARCHAR(100),
    vl_area_ha DECIMAL(10, 2) NOT NULL CHECK (vl_area_ha > 0),
    cd_cultura INT REFERENCES Cultura(cd_cultura) ON DELETE SET NULL,
    cd_responsavel INT REFERENCES Responsavel(cd_responsavel) ON DELETE SET NULL,
    dt_plantio DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Sensor
CREATE TABLE IF NOT EXISTS Sensor (
    cd_sensor SERIAL PRIMARY KEY,
    tp_sensor VARCHAR(50) NOT NULL,
    nm_modelo VARCHAR(100),
    cd_area INT REFERENCES Area_Plantio(cd_area) ON DELETE CASCADE,
    dt_instalacao DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Leitura_Sensor
CREATE TABLE IF NOT EXISTS Leitura_Sensor (
    cd_leitura SERIAL PRIMARY KEY,
    cd_sensor INT NOT NULL REFERENCES Sensor(cd_sensor) ON DELETE CASCADE,
    dt_leitura TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    vl_valor DECIMAL(10, 4) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Aplicacao (adubação e fungicidas)
CREATE TABLE IF NOT EXISTS Aplicacao (
    cd_aplicacao SERIAL PRIMARY KEY,
    cd_area INT REFERENCES Area_Plantio(cd_area) ON DELETE CASCADE,
    tp_aplicacao VARCHAR(20) CHECK (tp_aplicacao IN ('adubacao', 'fungicida')),
    nm_produto VARCHAR(150),
    vl_quantidade DECIMAL(10, 2),
    ds_unidade VARCHAR(20),
    dt_aplicacao DATE NOT NULL,
    ds_observacao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: Clima
CREATE TABLE IF NOT EXISTS Clima (
    cd_clima SERIAL PRIMARY KEY,
    cd_area INT REFERENCES Area_Plantio(cd_area) ON DELETE CASCADE,
    dt_medicao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    vl_temperatura DECIMAL(5, 2),
    vl_umidade DECIMAL(5, 2),
    vl_precipitacao DECIMAL(6, 2),
    vl_vento DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_leitura_sensor ON Leitura_Sensor(cd_sensor, dt_leitura DESC);
CREATE INDEX IF NOT EXISTS idx_leitura_data ON Leitura_Sensor(dt_leitura DESC);
CREATE INDEX IF NOT EXISTS idx_area_cultura ON Area_Plantio(cd_cultura);
CREATE INDEX IF NOT EXISTS idx_sensor_area ON Sensor(cd_area);
CREATE INDEX IF NOT EXISTS idx_aplicacao_area ON Aplicacao(cd_area, dt_aplicacao DESC);

-- Dados iniciais (exemplo)
INSERT INTO Cultura (nm_cultura, ds_cultura) VALUES
    ('Soja', 'Glycine max - Principal cultura oleaginosa'),
    ('Milho', 'Zea mays - Cultura de grãos'),
    ('Trigo', 'Triticum - Cultura de inverno')
ON CONFLICT (nm_cultura) DO NOTHING;

INSERT INTO Responsavel (nm_responsavel, nr_cpf, nr_telefone, ds_email) VALUES
    ('Administrador Sistema', '000.000.000-00', '(11) 99999-9999', 'admin@farmtech.com')
ON CONFLICT (nr_cpf) DO NOTHING;

-- Grants
GRANT ALL PRIVILEGES ON SCHEMA farmtech TO farmtech_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA farmtech TO farmtech_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA farmtech TO farmtech_user;

COMMIT;

-- Mensagem de sucesso
DO $$
BEGIN
    RAISE NOTICE '✅ Banco de dados FarmTech inicializado com sucesso!';
END $$;
