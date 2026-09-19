-- SQL na Pratica | Capitulo 5 | Use a base inicial carregada.
-- Execute cada consulta separadamente para observar o resultado.
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: exercicio_1_solucao
SELECT c.id AS conta,
       u.nome AS usuario
FROM contas AS c
INNER JOIN usuarios AS u
    ON u.id = c.usuario_id
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
   AND l.data_competencia >= DATE '2026-05-01'
   AND l.data_competencia < DATE '2026-06-01'
WHERE l.id IS NULL
ORDER BY c.id;

-- consulta: exercicio_2_solucao
SELECT l.id,
       l.valor,
       o.usuario_id AS titular,
       o.valor_limite AS limite
FROM lancamentos AS l
INNER JOIN contas AS c
    ON c.id = l.conta_id
LEFT JOIN orcamentos AS o
    ON o.categoria_id = l.categoria_id
   AND o.usuario_id = c.usuario_id
   AND o.mes_referencia = DATE '2026-05-01'
WHERE l.id IN (2, 9)
  AND l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
ORDER BY l.id, o.usuario_id;

