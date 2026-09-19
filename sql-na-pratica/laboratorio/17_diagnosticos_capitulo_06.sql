-- SQL na Pratica | Capitulo 6 | Base ficticia do livro
-- Execute uma consulta por vez. Os dados nao sao alterados.
-- DIAGNOSTICOS: SQL valido com resultados inadequados para a pergunta do livro.
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: where_incorreto
SELECT cat.id,
       cat.nome AS categoria,
       COUNT(*) AS quantidade,
       SUM(l.valor) AS total
FROM lancamentos AS l
JOIN categorias AS cat
    ON cat.id = l.categoria_id
   AND cat.tipo = l.tipo
WHERE l.tipo = 'despesa'
  AND l.valor >= 200
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
GROUP BY cat.id, cat.nome
ORDER BY total DESC, cat.id;

-- consulta: distinct_incorreto
SELECT SUM(valor) AS total,
       SUM(DISTINCT valor) AS total_distinto
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01';

-- consulta: exercicio_2_incorreto
SELECT u.id,
       u.nome AS usuario,
       COUNT(*) FILTER (
           WHERE l.data_liquidacao IS NULL
       ) AS pendencias
FROM usuarios AS u
LEFT JOIN contas AS c ON c.usuario_id = u.id
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
   AND l.tipo = 'despesa'
   AND l.data_competencia >= DATE '2026-05-01'
   AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id, u.nome
ORDER BY u.id;
