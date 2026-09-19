-- SQL na Prática | Capítulo 8 | Base fictícia inicial
-- Execute uma instrução completa por vez no banco de estudos.
-- Apenas consultas; não depende da view do capítulo 7.

SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: exercicio_1_solucao
WITH classificadas AS (
    SELECT id, valor,
           DENSE_RANK() OVER (
               ORDER BY valor DESC
           ) AS faixa
    FROM lancamentos
    WHERE tipo = 'despesa'
      AND data_competencia >= DATE '2026-05-01'
      AND data_competencia < DATE '2026-06-01'
)
SELECT id, valor, faixa
FROM classificadas
WHERE faixa <= 3
ORDER BY valor DESC, id;

-- consulta: exercicio_2_solucao
WITH despesas AS (
    SELECT l.id, c.usuario_id AS usuario, l.valor,
           SUM(l.valor) OVER (
               PARTITION BY c.usuario_id
           ) AS total_mes
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
)
SELECT id, usuario, valor, total_mes
FROM despesas
WHERE valor >= 100
ORDER BY usuario, id;
