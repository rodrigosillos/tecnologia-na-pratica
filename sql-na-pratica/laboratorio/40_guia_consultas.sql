-- SQL na Pratica | Guia rapido | PostgreSQL 18
-- Base original. Execute uma instrucao por vez e confira as respostas.
-- O ultimo bloco usa EXPLAIN ANALYZE: executa um SELECT, sem alterar dados.

-- preparacao
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;
SELECT current_database() AS banco,
       current_user AS usuario;
SELECT COUNT(*) AS lancamentos
FROM lancamentos;

-- filtro
SELECT id, valor
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY valor DESC, id
LIMIT 3;

-- sem_liquidacao
SELECT id, valor
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
  AND data_liquidacao IS NULL
ORDER BY id;

-- pendencias_corte
SELECT id, valor
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
  AND (data_liquidacao IS NULL
       OR data_liquidacao >= DATE '2026-06-01')
ORDER BY id;

-- classificacao
SELECT id,
       CASE
         WHEN data_liquidacao < DATE '2026-06-01'
           THEN 'Liquidada no corte'
         ELSE 'Pendente no corte'
       END AS situacao
FROM lancamentos
WHERE id IN (2, 4, 10)
ORDER BY id;

-- resumo
SELECT u.id AS usuario,
       COUNT(l.id) AS despesas,
       COALESCE(SUM(l.valor), 0) AS total
FROM usuarios AS u
LEFT JOIN contas AS c ON c.usuario_id = u.id
LEFT JOIN lancamentos AS l
  ON l.conta_id = c.id
 AND l.tipo = 'despesa'
 AND l.data_competencia >= DATE '2026-05-01'
 AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id
ORDER BY u.id;

-- grupos
SELECT categoria_id, SUM(valor) AS total
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
GROUP BY categoria_id
HAVING SUM(valor) > 100.00
ORDER BY total DESC, categoria_id;

-- ausencia
SELECT u.id, u.nome
FROM usuarios AS u
WHERE NOT EXISTS (
    SELECT 1
    FROM contas AS c
    JOIN lancamentos AS l ON l.conta_id = c.id
    WHERE c.usuario_id = u.id
      AND l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
)
ORDER BY u.id;

-- cte
WITH gastos AS (
    SELECT c.usuario_id, SUM(l.valor) AS total
    FROM contas AS c
    JOIN lancamentos AS l ON l.conta_id = c.id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
    GROUP BY c.usuario_id
)
SELECT usuario_id, total
FROM gastos
WHERE total > 400.00
ORDER BY usuario_id;

-- acumulado
SELECT l.id, l.valor,
       SUM(l.valor) OVER (
           PARTITION BY c.usuario_id
           ORDER BY l.data_competencia, l.id
           ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
       ) AS acumulado
FROM contas AS c
JOIN lancamentos AS l ON l.conta_id = c.id
WHERE c.usuario_id = 1
  AND l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
ORDER BY l.data_competencia, l.id;

-- plano
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, valor
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY id;
