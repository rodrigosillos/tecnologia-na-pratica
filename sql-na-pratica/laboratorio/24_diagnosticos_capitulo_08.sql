-- SQL na Prática | Capítulo 8 | Base fictícia inicial
-- Execute uma instrução completa por vez no banco de estudos.
-- Apenas consultas; não depende da view do capítulo 7.
-- Erros de lógica intencionais para diagnóstico.
-- As instruções executam, mas não atendem às perguntas do livro.

SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: ranking_id_incorreto
SELECT id, valor,
       ROW_NUMBER() OVER (
           ORDER BY valor DESC, id
       ) AS ordem,
       RANK() OVER (
           ORDER BY valor DESC, id
       ) AS posicao,
       DENSE_RANK() OVER (
           ORDER BY valor DESC, id
       ) AS faixa
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY valor DESC, id;

-- consulta: limite_global_incorreto
WITH classificadas AS (
    SELECT l.id, c.usuario_id AS usuario, l.valor,
           ROW_NUMBER() OVER (
               PARTITION BY c.usuario_id
               ORDER BY l.valor DESC, l.id
           ) AS ordem
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
)
SELECT id, usuario, valor, ordem
FROM classificadas
ORDER BY usuario, ordem
LIMIT 2;

-- consulta: junho_antes_lag
WITH mensais AS (
    SELECT c.usuario_id AS usuario,
           CAST(DATE_TRUNC('month', l.data_competencia)
                AS DATE) AS mes,
           SUM(l.valor) AS total
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-06-01'
      AND l.data_competencia < DATE '2026-07-01'
    GROUP BY c.usuario_id,
             CAST(DATE_TRUNC('month', l.data_competencia)
                  AS DATE)
), comparacao AS (
    SELECT usuario, mes, total,
           LAG(total) OVER (
               PARTITION BY usuario ORDER BY mes
           ) AS anterior
    FROM mensais
)
SELECT usuario, mes, total, anterior,
       total - anterior AS diferenca
FROM comparacao
ORDER BY usuario, mes;

-- consulta: exercicio_2_incorreto
SELECT l.id, c.usuario_id AS usuario, l.valor,
       SUM(l.valor) OVER (
           PARTITION BY c.usuario_id
       ) AS total_mes
FROM lancamentos AS l
JOIN contas AS c ON c.id = l.conta_id
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
  AND l.valor >= 100
ORDER BY c.usuario_id, l.id;
