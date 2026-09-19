-- Execute depois de 01_estrutura.sql e 02_dados.sql.
-- Execute um bloco por vez para conferir cada saida.

-- Carga: 12 lancamentos.
SELECT COUNT(*) AS quantidade
FROM sql_pratica.lancamentos;

-- Esta configuracao vale para a sessao atual.
SET search_path TO sql_pratica;
SHOW search_path;

-- Consulta do capitulo 1: IDs 2, 4 e 6.
SELECT id, descricao, valor
FROM lancamentos
WHERE conta_id = 1
  AND tipo = 'despesa'
  AND valor >= 100
ORDER BY id;
