-- SQL na Pratica - Capitulo 10. Banco de estudos, dados ficticios.
-- MESMA ABA E CONEXAO em todo o percurso. Autocommit ligado.
-- Encerre qualquer transacao pendente antes de comecar.
-- Execute UMA INSTRUCAO por vez, ate o ponto e virgula, na ordem.
-- Ordem: 30 (carga), 31 (planos), 32 (exercicios), 33 (limpeza).
-- A tabela e temporaria: fechar a conexao a remove.
-- Os planos podem variar; quantidades e totais devem coincidir.
-- Todos os EXPLAIN ANALYZE deste pacote medem apenas SELECTs.

-- BLOCO 01: consulta
-- Esperado: 31 linhas, IDs 8321 a 8351, datas de maio de 2026.
SELECT id, data_competencia, valor
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY data_competencia, id;

-- BLOCO 02: conferencia_alvo
-- Esperado: quantidade 31, total 3379.00.
SELECT COUNT(*) AS quantidade,
       SUM(valor) AS total
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01';

-- BLOCO 03: plano_estimado
-- EXPLAIN sem ANALYZE mostra apenas estimativas para este SELECT.
EXPLAIN
SELECT id, data_competencia, valor
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY data_competencia, id;

-- BLOCO 04: plano_antes
-- Consulta executada SEM indice. Salve o plano antes de criar o indice. Repita algumas vezes se comparar tempos.
EXPLAIN (ANALYZE, BUFFERS, TIMING OFF)
SELECT id, data_competencia, valor
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY data_competencia, id;

-- BLOCO 05: criar_indice
-- Execute uma vez. A carga deve estar preparada e ainda sem este indice.
CREATE INDEX idx_despesas_conta_data
ON pg_temp.despesas_teste
USING btree (conta_id, data_competencia);

-- BLOCO 06: plano_depois
-- Mesma consulta agora COM indice. Observe Index Cond, linhas e buffers. Nao force o tipo de plano.
EXPLAIN (ANALYZE, BUFFERS, TIMING OFF)
SELECT id, data_competencia, valor
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY data_competencia, id;

-- BLOCO 07: conferencia_depois
-- O resultado deve continuar 31 e 3379.00.
SELECT COUNT(*) AS quantidade,
       SUM(valor) AS total
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01';

-- BLOCO 08: plano_amplo
-- Total geral. Esperado: Aggregate recebe 100000 valores e devolve uma linha.
EXPLAIN (ANALYZE, BUFFERS, TIMING OFF)
SELECT SUM(valor) AS total
FROM pg_temp.despesas_teste;

