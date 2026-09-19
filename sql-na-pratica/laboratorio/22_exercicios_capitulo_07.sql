-- SQL na Prática | Capítulo 7 | Base fictícia inicial
-- Execute uma instrução por vez no banco de estudos.

SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: exercicio_1_solucao
WITH despesas_maio AS (
    SELECT l.id, c.usuario_id,
           l.categoria_id, l.valor
    FROM lancamentos AS l
    JOIN contas AS c ON c.id = l.conta_id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
)
SELECT d.id, d.usuario_id,
       d.categoria_id, d.valor
FROM despesas_maio AS d
WHERE NOT EXISTS (
    SELECT 1
    FROM orcamentos AS o
    WHERE o.usuario_id = d.usuario_id
      AND o.categoria_id = d.categoria_id
      AND o.mes_referencia = DATE '2026-05-01'
)
ORDER BY d.id;

-- consulta: exercicio_2_solucao
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
