-- SQL na Prática | Capítulo 8 | Base fictícia inicial
-- Execute uma instrução completa por vez no banco de estudos.
-- Apenas consultas; não depende da view do capítulo 7.

SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: total_usuario
SELECT l.id, c.usuario_id AS usuario, l.valor,
       SUM(l.valor) OVER (
           PARTITION BY c.usuario_id
       ) AS total_mes
FROM lancamentos AS l
JOIN contas AS c ON c.id = l.conta_id
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
ORDER BY c.usuario_id, l.id;

-- consulta: percentuais
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
SELECT id, usuario,
       ROUND(100.0 * valor / total_mes, 2)
           AS percentual
FROM despesas
ORDER BY usuario, id;

-- consulta: total_geral
SELECT l.id, c.usuario_id AS usuario, l.valor,
       SUM(l.valor) OVER (
           
       ) AS total_mes
FROM lancamentos AS l
JOIN contas AS c ON c.id = l.conta_id
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
ORDER BY c.usuario_id, l.id;

-- consulta: classificacao
SELECT id, valor,
       ROW_NUMBER() OVER (
           ORDER BY valor DESC, id
       ) AS ordem,
       RANK() OVER (
           ORDER BY valor DESC
       ) AS posicao,
       DENSE_RANK() OVER (
           ORDER BY valor DESC
       ) AS faixa
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY valor DESC, id;

-- consulta: duas_por_usuario
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
WHERE ordem <= 2
ORDER BY usuario, ordem;

-- consulta: acumulado
SELECT l.id, c.usuario_id AS usuario,
       l.data_competencia AS dia, l.valor,
       SUM(l.valor) OVER (
           PARTITION BY c.usuario_id
           ORDER BY l.data_competencia, l.id
           ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
       ) AS acumulado
FROM lancamentos AS l
JOIN contas AS c ON c.id = l.conta_id
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
ORDER BY c.usuario_id, l.data_competencia, l.id;

-- consulta: molduras
SELECT id, valor,
       SUM(valor) OVER (
           ORDER BY valor
       ) AS padrao,
       SUM(valor) OVER (
           ORDER BY valor, id
           ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
       ) AS por_linha
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY valor, id;

-- consulta: comparacao_mensal
WITH mensais AS (
    SELECT c.usuario_id AS usuario,
           CAST(DATE_TRUNC('month', l.data_competencia)
                AS DATE) AS mes,
           SUM(l.valor) AS total
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
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

-- consulta: junho_externo
WITH mensais AS (
    SELECT c.usuario_id AS usuario,
           CAST(DATE_TRUNC('month', l.data_competencia)
                AS DATE) AS mes,
           SUM(l.valor) AS total
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
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
WHERE mes = DATE '2026-06-01'
ORDER BY usuario, mes;
