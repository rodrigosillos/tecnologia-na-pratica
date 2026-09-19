-- SQL na Pratica - Capitulo 10. Banco de estudos, dados ficticios.
-- MESMA ABA E CONEXAO em todo o percurso. Autocommit ligado.
-- Encerre qualquer transacao pendente antes de comecar.
-- Execute UMA INSTRUCAO por vez, ate o ponto e virgula, na ordem.
-- Ordem: 30 (carga), 31 (planos), 32 (exercicios), 33 (limpeza).
-- A tabela e temporaria: fechar a conexao a remove.
-- Os planos podem variar; quantidades e totais devem coincidir.
-- Todos os EXPLAIN ANALYZE deste pacote medem apenas SELECTs.

-- BLOCO 01: preparacao
-- Confira banco de estudos, usuario estudante_sql e 12 lancamentos originais.
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;
SELECT current_database() AS banco,
       current_user AS usuario;
SELECT COUNT(*) AS lancamentos_originais
FROM sql_pratica.lancamentos;

-- BLOCO 02: carga
-- Recria SOMENTE a tabela temporaria despesas_teste e remove seu indice anterior. Nao repita no meio da comparacao.
DROP TABLE IF EXISTS pg_temp.despesas_teste;
CREATE TEMP TABLE despesas_teste AS
SELECT (c.conta - 1) * 200 + d.dia + 1 AS id,
       c.conta AS conta_id,
       DATE '2026-01-01' + d.dia
           AS data_competencia,
       (10 + (c.conta % 50) * 2 + d.dia % 31)
           ::NUMERIC(12,2) AS valor,
       'Despesa de laboratorio ' || c.conta
           || '/' || d.dia AS descricao
FROM generate_series(1, 500) AS c(conta)
CROSS JOIN generate_series(0, 199) AS d(dia);

-- BLOCO 03: conferencia_carga
-- Esperado: 100000 linhas e 500 contas sinteticas.
SELECT COUNT(*) AS linhas,
       COUNT(DISTINCT conta_id) AS contas
FROM pg_temp.despesas_teste;

-- BLOCO 04: estatisticas
-- Coleta estatisticas da tabela temporaria. Nao cria indice.
ANALYZE pg_temp.despesas_teste;

