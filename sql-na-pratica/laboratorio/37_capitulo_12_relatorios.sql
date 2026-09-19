-- SQL na Pratica | Capitulo 12 | PostgreSQL 18
-- Dados ficticios. Execute UMA instrucao por vez no banco de estudos.
-- Use a mesma aba e conexao, com autocommit ativado.
-- Execute o arquivo 36 antes de iniciar as tarefas.

-- Etapa 1: t1_fechamento
SELECT u.id AS usuario,
       COALESCE(SUM(l.valor), 0) AS total,
       COALESCE(SUM(l.valor) FILTER (
           WHERE l.data_liquidacao < DATE '2026-06-01'
       ), 0) AS liquidado,
       COALESCE(SUM(l.valor) FILTER (
           WHERE l.data_liquidacao IS NULL
              OR l.data_liquidacao >= DATE '2026-06-01'
       ), 0) AS pendente
FROM usuarios AS u
LEFT JOIN contas AS c ON c.usuario_id = u.id
LEFT JOIN lancamentos AS l
  ON l.conta_id = c.id
 AND l.tipo = 'despesa'
 AND l.data_competencia >= DATE '2026-05-01'
 AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id
ORDER BY u.id;

-- Etapa 2: t2_pendencias
SELECT l.id, c.usuario_id AS usuario,
       l.valor, l.data_liquidacao
FROM lancamentos AS l
JOIN contas AS c ON c.id = l.conta_id
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
  AND (l.data_liquidacao IS NULL
       OR l.data_liquidacao >= DATE '2026-06-01')
ORDER BY c.usuario_id, l.id;

-- Etapa 3: t3_orcamentos
WITH gastos AS (
    SELECT c.usuario_id, l.categoria_id,
           SUM(l.valor) AS total
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
    GROUP BY c.usuario_id, l.categoria_id
)
SELECT o.id AS orcamento,
       o.valor_limite AS limite,
       COALESCE(g.total, 0) AS realizado,
       o.valor_limite - COALESCE(g.total, 0) AS saldo
FROM orcamentos AS o
LEFT JOIN gastos AS g
  ON g.usuario_id = o.usuario_id
 AND g.categoria_id = o.categoria_id
WHERE o.mes_referencia = DATE '2026-05-01'
ORDER BY o.id;

-- Etapa 4: t3_sem_orcamento
SELECT l.id, l.valor
FROM lancamentos AS l
JOIN contas AS c ON c.id = l.conta_id
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
  AND NOT EXISTS (
      SELECT 1
      FROM orcamentos AS o
      WHERE o.usuario_id = c.usuario_id
        AND o.categoria_id = l.categoria_id
        AND o.mes_referencia = DATE '2026-05-01'
  )
ORDER BY l.id;

-- Etapa 5: t4_ranking
WITH gastos AS (
    SELECT c.usuario_id, l.categoria_id,
           SUM(l.valor) AS total
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
    GROUP BY c.usuario_id, l.categoria_id
), classificacao AS (
    SELECT usuario_id, categoria_id, total,
           DENSE_RANK() OVER (
               PARTITION BY usuario_id
               ORDER BY total DESC
           ) AS faixa,
           SUM(total) OVER (
               PARTITION BY usuario_id
           ) AS total_usuario
    FROM gastos
)
SELECT usuario_id AS usuario,
       categoria_id AS categoria, total, faixa,
       ROUND(100.0 * total / total_usuario, 2)
           AS percentual
FROM classificacao
WHERE faixa <= 2
ORDER BY usuario_id, faixa, categoria_id;

-- Etapa 6: t5_comparacao
WITH meses(mes) AS (
    VALUES (DATE '2026-05-01'), (DATE '2026-06-01')
), serie AS (
    SELECT u.id AS usuario, m.mes,
           COALESCE(SUM(l.valor), 0) AS total
    FROM usuarios AS u
    CROSS JOIN meses AS m
    LEFT JOIN contas AS c ON c.usuario_id = u.id
    LEFT JOIN lancamentos AS l
      ON l.conta_id = c.id
     AND l.tipo = 'despesa'
     AND l.data_competencia >= m.mes
     AND l.data_competencia < m.mes + INTERVAL '1 month'
    GROUP BY u.id, m.mes
), comparacao AS (
    SELECT usuario, mes, total,
           LAG(total) OVER (
               PARTITION BY usuario ORDER BY mes
           ) AS anterior
    FROM serie
)
SELECT usuario, anterior AS maio, total AS junho,
       total - anterior AS diferenca
FROM comparacao
WHERE mes = DATE '2026-06-01'
ORDER BY usuario;
