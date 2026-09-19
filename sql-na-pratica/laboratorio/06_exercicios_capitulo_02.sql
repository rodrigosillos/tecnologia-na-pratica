-- Solucoes dos exercicios do capitulo 2.
-- 1: O nome completo funciona sem preparar o search_path.
RESET search_path;
SHOW search_path;
SELECT COUNT(*) AS quantidade
FROM sql_pratica.lancamentos;
-- Esperado: 12.

-- Outra solucao para o exercicio 1.
SET search_path TO sql_pratica;
SELECT COUNT(*) AS quantidade
FROM lancamentos;
-- Esperado: 12.

-- 2: Antes de executar em outra sessao, conferir banco e usuario.
SELECT current_database() AS banco,
       current_user AS usuario;
SET search_path TO sql_pratica;
SELECT id, descricao, valor
FROM lancamentos
WHERE conta_id = 1
  AND tipo = 'despesa'
  AND valor >= 180
ORDER BY id;
-- Esperado: IDs 2 e 6, ambos 180.00.
