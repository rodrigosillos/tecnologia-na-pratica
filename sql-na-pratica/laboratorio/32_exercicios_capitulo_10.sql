-- SQL na Pratica - Capitulo 10. Banco de estudos, dados ficticios.
-- MESMA ABA E CONEXAO em todo o percurso. Autocommit ligado.
-- Encerre qualquer transacao pendente antes de comecar.
-- Execute UMA INSTRUCAO por vez, ate o ponto e virgula, na ordem.
-- Ordem: 30 (carga), 31 (planos), 32 (exercicios), 33 (limpeza).
-- A tabela e temporaria: fechar a conexao a remove.
-- Os planos podem variar; quantidades e totais devem coincidir.
-- Todos os EXPLAIN ANALYZE deste pacote medem apenas SELECTs.

-- BLOCO 01: ex1_plano
-- Exercicio 1: consulta correta, mas compare Index Cond e Filter. Requer indice criado no arquivo 31.
EXPLAIN (ANALYZE, BUFFERS, TIMING OFF)
SELECT id, data_competencia, valor
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND EXTRACT(YEAR FROM data_competencia) = 2026
  AND EXTRACT(MONTH FROM data_competencia) = 5
ORDER BY data_competencia, id;

-- BLOCO 02: ex1_conferencia
-- Esperado: 31 e 3379.00. As expressoes nao mudam a resposta nesta carga.
SELECT COUNT(*) AS quantidade,
       SUM(valor) AS total
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND EXTRACT(YEAR FROM data_competencia) = 2026
  AND EXTRACT(MONTH FROM data_competencia) = 5;

-- BLOCO 03: ex1_solucao
-- Intervalo direto: compare com EXTRACT sem alterar o resultado esperado.
EXPLAIN (ANALYZE, BUFFERS, TIMING OFF)
SELECT id, data_competencia, valor
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY data_competencia, id;

-- BLOCO 04: ex2_erro
-- ERRO DE LOGICA INTENCIONAL: BETWEEN inclui 1 de junho. Retorna 32 e 3500.00.
SELECT COUNT(*) AS quantidade,
       SUM(valor) AS total
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND data_competencia BETWEEN
      DATE '2026-05-01' AND DATE '2026-06-01';

-- BLOCO 05: ex2_solucao
-- Limite superior exclusivo: esperado 31 e 3379.00.
SELECT COUNT(*) AS quantidade,
       SUM(valor) AS total
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01';

-- BLOCO 06: ex2_plano
-- Aggregate retorna uma linha, leitura subjacente retorna 31. Sao granularidades diferentes.
EXPLAIN (ANALYZE, BUFFERS, TIMING OFF)
SELECT COUNT(*) AS quantidade,
       SUM(valor) AS total
FROM pg_temp.despesas_teste
WHERE conta_id = 42
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01';

