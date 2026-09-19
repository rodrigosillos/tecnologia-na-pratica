-- SQL na Pratica | Capitulo 6 | Base ficticia do livro
-- Execute uma consulta por vez. Os dados nao sao alterados.
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: resumo
SELECT COUNT(*) AS quantidade,
       SUM(valor) AS total,
       ROUND(AVG(valor), 2) AS media,
       MIN(valor) AS menor,
       MAX(valor) AS maior
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01';

-- consulta: contagem_liquidacao
SELECT COUNT(*) AS despesas,
       COUNT(data_liquidacao) AS com_liquidacao,
       COUNT(*) - COUNT(data_liquidacao)
           AS sem_liquidacao
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01';

-- consulta: sem_despesas
SELECT COUNT(*) AS quantidade,
       SUM(valor) AS total,
       AVG(valor) AS media
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-07-01'
  AND data_competencia < DATE '2026-08-01';

-- consulta: por_categoria
SELECT cat.id,
       cat.nome AS categoria,
       COUNT(*) AS quantidade,
       SUM(l.valor) AS total
FROM lancamentos AS l
JOIN categorias AS cat
    ON cat.id = l.categoria_id
   AND cat.tipo = l.tipo
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
GROUP BY cat.id, cat.nome
ORDER BY total DESC, cat.id;

-- consulta: por_usuario
SELECT u.id,
       u.nome AS usuario,
       COUNT(*) AS quantidade,
       ROUND(AVG(l.valor), 2) AS media
FROM lancamentos AS l
JOIN contas AS c ON c.id = l.conta_id
JOIN usuarios AS u ON u.id = c.usuario_id
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id, u.nome
ORDER BY u.id;

-- consulta: categorias_having
SELECT cat.id,
       cat.nome AS categoria,
       COUNT(*) AS quantidade,
       SUM(l.valor) AS total
FROM lancamentos AS l
JOIN categorias AS cat
    ON cat.id = l.categoria_id
   AND cat.tipo = l.tipo
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
GROUP BY cat.id, cat.nome
HAVING SUM(l.valor) >= 200
ORDER BY total DESC, cat.id;

-- consulta: contas_contagem
SELECT c.id AS conta,
       COUNT(*) AS linhas,
       COUNT(l.id) AS despesas,
       SUM(l.valor) AS total
FROM contas AS c
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
   AND l.tipo = 'despesa'
   AND l.data_competencia >= DATE '2026-05-01'
   AND l.data_competencia < DATE '2026-06-01'
GROUP BY c.id
ORDER BY c.id;

-- consulta: contas_zero
SELECT c.id AS conta,
       COUNT(*) AS linhas,
       COUNT(l.id) AS despesas,
       COALESCE(SUM(l.valor), 0) AS total
FROM contas AS c
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
   AND l.tipo = 'despesa'
   AND l.data_competencia >= DATE '2026-05-01'
   AND l.data_competencia < DATE '2026-06-01'
GROUP BY c.id
ORDER BY c.id;

-- consulta: pendencias
SELECT u.id,
       u.nome AS usuario,
       COALESCE(SUM(l.valor), 0) AS total,
       COALESCE(
           SUM(l.valor) FILTER (
               WHERE l.data_liquidacao IS NULL
           ), 0
       ) AS pendente
FROM usuarios AS u
LEFT JOIN contas AS c ON c.usuario_id = u.id
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
   AND l.tipo = 'despesa'
   AND l.data_competencia >= DATE '2026-05-01'
   AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id, u.nome
ORDER BY u.id;

-- consulta: orcamentos
SELECT u.nome AS usuario,
       cat.nome AS categoria,
       o.valor_limite AS limite,
       COALESCE(SUM(l.valor), 0) AS total
FROM orcamentos AS o
JOIN usuarios AS u ON u.id = o.usuario_id
JOIN categorias AS cat
    ON cat.id = o.categoria_id
   AND cat.tipo = o.tipo
LEFT JOIN contas AS c ON c.usuario_id = u.id
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
   AND l.categoria_id = o.categoria_id
   AND l.tipo = o.tipo
   AND l.data_competencia >= DATE '2026-05-01'
   AND l.data_competencia < DATE '2026-06-01'
WHERE o.mes_referencia = DATE '2026-05-01'
GROUP BY o.id, u.id, u.nome,
         cat.id, cat.nome, o.valor_limite
ORDER BY o.id;

-- consulta: orcamentos_excedidos
SELECT u.nome AS usuario,
       cat.nome AS categoria,
       o.valor_limite AS limite,
       COALESCE(SUM(l.valor), 0) AS total
FROM orcamentos AS o
JOIN usuarios AS u ON u.id = o.usuario_id
JOIN categorias AS cat
    ON cat.id = o.categoria_id
   AND cat.tipo = o.tipo
LEFT JOIN contas AS c ON c.usuario_id = u.id
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
   AND l.categoria_id = o.categoria_id
   AND l.tipo = o.tipo
   AND l.data_competencia >= DATE '2026-05-01'
   AND l.data_competencia < DATE '2026-06-01'
WHERE o.mes_referencia = DATE '2026-05-01'
GROUP BY o.id, u.id, u.nome,
         cat.id, cat.nome, o.valor_limite
HAVING COALESCE(SUM(l.valor), 0)
       > o.valor_limite
ORDER BY o.id;
