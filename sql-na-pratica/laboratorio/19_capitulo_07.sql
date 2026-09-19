-- SQL na Prática | Capítulo 7 | Base fictícia inicial
-- Execute uma instrução por vez no banco de estudos.

SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: acima_media
SELECT l.id, l.descricao, l.valor
FROM lancamentos AS l
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
  AND l.valor > (
      SELECT AVG(m.valor)
      FROM lancamentos AS m
      WHERE m.tipo = 'despesa'
        AND m.data_competencia >= DATE '2026-05-01'
        AND m.data_competencia < DATE '2026-06-01'
  )
ORDER BY l.id;

-- consulta: resumo_derivado
SELECT u.id, u.nome, r.total
FROM (
    SELECT c.usuario_id,
           SUM(l.valor) AS total
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
    GROUP BY c.usuario_id
) AS r
JOIN usuarios AS u ON u.id = r.usuario_id
WHERE r.total > 400
ORDER BY u.id;

-- consulta: usuarios_com_pendencia
SELECT u.id, u.nome
FROM usuarios AS u
WHERE EXISTS (
    SELECT 1
    FROM contas AS c
    JOIN lancamentos AS l ON l.conta_id = c.id
    WHERE c.usuario_id = u.id
      AND l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
      AND l.data_liquidacao IS NULL
)
ORDER BY u.id;

-- consulta: usuarios_sem_despesas
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

-- consulta: not_in_null
SELECT 99 NOT IN (1, NULL) AS ausente;

-- consulta: ctes_usuarios
WITH despesas_maio AS (
    SELECT c.usuario_id, l.valor
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
), totais_usuario AS (
    SELECT usuario_id, SUM(valor) AS total
    FROM despesas_maio
    GROUP BY usuario_id
)
SELECT u.id, u.nome,
       COALESCE(t.total, 0) AS total
FROM usuarios AS u
LEFT JOIN totais_usuario AS t
    ON t.usuario_id = u.id
ORDER BY u.id;

-- consulta: cte_orcamentos
WITH gastos_maio AS (
    SELECT c.usuario_id, l.categoria_id,
           SUM(l.valor) AS total
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
    GROUP BY c.usuario_id, l.categoria_id
)
SELECT u.nome AS usuario,
       cat.nome AS categoria,
       o.valor_limite AS limite,
       COALESCE(g.total, 0) AS total
FROM orcamentos AS o
JOIN usuarios AS u ON u.id = o.usuario_id
JOIN categorias AS cat
    ON cat.id = o.categoria_id
   AND cat.tipo = o.tipo
LEFT JOIN gastos_maio AS g
    ON g.usuario_id = o.usuario_id
   AND g.categoria_id = o.categoria_id
WHERE o.mes_referencia = DATE '2026-05-01'
ORDER BY o.id;

-- consulta: orcamentos_excedidos
WITH gastos_maio AS (
    SELECT c.usuario_id, l.categoria_id,
           SUM(l.valor) AS total
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
    GROUP BY c.usuario_id, l.categoria_id
)
SELECT u.nome AS usuario,
       cat.nome AS categoria,
       o.valor_limite AS limite,
       COALESCE(g.total, 0) AS total
FROM orcamentos AS o
JOIN usuarios AS u ON u.id = o.usuario_id
JOIN categorias AS cat
    ON cat.id = o.categoria_id
   AND cat.tipo = o.tipo
LEFT JOIN gastos_maio AS g
    ON g.usuario_id = o.usuario_id
   AND g.categoria_id = o.categoria_id
WHERE o.mes_referencia = DATE '2026-05-01'
  AND COALESCE(g.total, 0) > o.valor_limite
ORDER BY o.id;
