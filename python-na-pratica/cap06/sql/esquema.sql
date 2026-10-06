CREATE SCHEMA IF NOT EXISTS {esquema};
CREATE TABLE IF NOT EXISTS {esquema}.metadados (
    chave INTEGER PRIMARY KEY CHECK (chave = 1),
    versao INTEGER NOT NULL CHECK (versao = 1)
);
INSERT INTO {esquema}.metadados (chave, versao) VALUES (1, 1)
ON CONFLICT (chave) DO NOTHING;
CREATE TABLE IF NOT EXISTS {esquema}.despesas (
    id VARCHAR(9) PRIMARY KEY CHECK (id ~ '^D[0-9]{{3,8}}$'),
    data DATE NOT NULL,
    descricao TEXT NOT NULL CHECK (length(descricao) BETWEEN 1 AND 120 AND descricao = btrim(descricao)),
    categoria TEXT NOT NULL CHECK (length(categoria) BETWEEN 1 AND 30 AND categoria = btrim(categoria)),
    valor NUMERIC(9, 2) NOT NULL CHECK (valor > 0 AND valor <> 'NaN'::numeric)
);
