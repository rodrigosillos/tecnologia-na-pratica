-- SQL na Pratica | Capitulo 5 | Use a base inicial carregada.
-- Execute cada consulta separadamente para observar o resultado.
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: lancamento_conta
SELECT l.id AS lancamento,
       c.id AS conta,
       c.nome
FROM lancamentos AS l
INNER JOIN contas AS c
    ON c.id = l.conta_id
WHERE l.id IN (2, 7)
ORDER BY l.id;

-- consulta: despesas_maio
SELECT l.id,
       u.nome AS usuario,
       cat.nome AS categoria,
       l.valor
FROM lancamentos AS l
INNER JOIN contas AS c
    ON c.id = l.conta_id
INNER JOIN usuarios AS u
    ON u.id = c.usuario_id
INNER JOIN categorias AS cat
    ON cat.id = l.categoria_id
   AND cat.tipo = l.tipo
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
ORDER BY l.id;

-- consulta: contas_inner
SELECT c.id AS conta,
       c.nome,
       l.id AS lancamento
FROM contas AS c
INNER JOIN lancamentos AS l
    ON l.conta_id = c.id
WHERE c.id IN (2, 4)
ORDER BY c.id, l.id;

-- consulta: contas_left
SELECT c.id AS conta,
       c.nome,
       l.id AS lancamento
FROM contas AS c
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
WHERE c.id IN (2, 4)
ORDER BY c.id, l.id;

-- consulta: sem_movimento
SELECT c.id AS conta,
       u.nome AS usuario
FROM contas AS c
INNER JOIN usuarios AS u
    ON u.id = c.usuario_id
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
WHERE l.id IS NULL
ORDER BY c.id;

-- consulta: filtro_on
SELECT c.id AS conta,
       l.id AS lancamento,
       l.valor
FROM contas AS c
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
   AND l.tipo = 'despesa'
   AND l.data_competencia >= DATE '2026-05-01'
   AND l.data_competencia < DATE '2026-06-01'
ORDER BY c.id, l.id;

-- consulta: orcamento_completo
SELECT l.id,
       l.valor,
       o.id AS orcamento,
       o.valor_limite AS limite
FROM lancamentos AS l
INNER JOIN contas AS c
    ON c.id = l.conta_id
LEFT JOIN orcamentos AS o
    ON o.usuario_id = c.usuario_id
   AND o.categoria_id = l.categoria_id
   AND o.mes_referencia = DATE '2026-05-01'
WHERE c.usuario_id = 1
  AND l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
ORDER BY l.id;

-- consulta: grade_cross
SELECT u.id AS usuario,
       cat.id AS categoria
FROM usuarios AS u
CROSS JOIN categorias AS cat
WHERE cat.tipo = 'despesa'
ORDER BY u.id, cat.id;

-- consulta: pares_self
SELECT a.usuario_id AS usuario,
       a.id AS conta_a,
       b.id AS conta_b
FROM contas AS a
INNER JOIN contas AS b
    ON b.usuario_id = a.usuario_id
   AND a.id < b.id
ORDER BY a.usuario_id, a.id, b.id;

