CREATE SCHEMA IF NOT EXISTS {esquema};
CREATE TABLE IF NOT EXISTS {esquema}.metadados (
    chave INTEGER PRIMARY KEY CHECK (chave = 1),
    versao INTEGER NOT NULL CHECK (versao = 1)
);
INSERT INTO {esquema}.metadados VALUES (1, 1) ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS {esquema}.despesas (
    id VARCHAR(9) PRIMARY KEY CHECK (id ~ '^D[0-9]{{3,8}}$'),
    data DATE NOT NULL,
    descricao TEXT NOT NULL CHECK (length(descricao) BETWEEN 1 AND 120 AND descricao = btrim(descricao)),
    categoria TEXT NOT NULL CHECK (length(categoria) BETWEEN 1 AND 30 AND categoria = btrim(categoria)),
    valor NUMERIC(9, 2) NOT NULL CHECK (valor > 0 AND valor <> 'NaN'::numeric)
);
CREATE TABLE IF NOT EXISTS {esquema}.execucoes (
    id VARCHAR(40) PRIMARY KEY CHECK (id ~ '^[a-z0-9][a-z0-9_-]{{0,39}}$'),
    entrada_sha256 CHAR(64) NOT NULL CHECK (entrada_sha256 ~ '^[a-f0-9]{{64}}$'),
    novas INTEGER NOT NULL CHECK (novas >= 0),
    existentes INTEGER NOT NULL CHECK (existentes >= 0),
    retrato JSONB NOT NULL,
    proveniencia JSONB NOT NULL,
    confirmada_em TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
