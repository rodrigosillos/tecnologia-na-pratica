-- SQL na Pratica | Capitulo 5 | Use a base inicial carregada.
-- Execute cada consulta separadamente para observar o resultado.
-- ATENCAO: consultas intencionalmente incorretas para as perguntas
-- do capitulo. Executam sem erro, mas produzem respostas inadequadas.
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: ausencia_incorreta
SELECT c.id AS conta,
       l.id AS lancamento
FROM contas AS c
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
WHERE l.data_liquidacao IS NULL
ORDER BY c.id, l.id;

-- consulta: filtro_where_incorreto
SELECT c.id AS conta,
       l.id AS lancamento,
       l.valor
FROM contas AS c
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
ORDER BY c.id, l.id;

-- consulta: orcamento_incompleto
SELECT l.id AS lancamento,
       o.id AS orcamento,
       o.valor_limite AS limite
FROM lancamentos AS l
INNER JOIN orcamentos AS o
    ON o.categoria_id = l.categoria_id
WHERE l.id = 2
ORDER BY o.id;

-- consulta: exercicio_2_incorreto
SELECT l.id,
       l.valor,
       o.usuario_id AS titular,
       o.valor_limite AS limite
FROM lancamentos AS l
INNER JOIN contas AS c
    ON c.id = l.conta_id
LEFT JOIN orcamentos AS o
    ON o.categoria_id = l.categoria_id
   AND o.mes_referencia = DATE '2026-05-01'
WHERE l.id IN (2, 9)
  AND l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
ORDER BY l.id, o.usuario_id;

