-- SQL na Pratica | Capitulo 6 | Base ficticia do livro
-- Execute uma consulta por vez. Os dados nao sao alterados.
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: exercicio_1_solucao
SELECT u.id,
       u.nome AS usuario,
       cat.nome AS categoria,
       SUM(l.valor) AS total
FROM lancamentos AS l
JOIN contas AS c ON c.id = l.conta_id
JOIN usuarios AS u ON u.id = c.usuario_id
JOIN categorias AS cat
    ON cat.id = l.categoria_id
   AND cat.tipo = l.tipo
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id, u.nome, cat.id, cat.nome
HAVING SUM(l.valor) >= 100
ORDER BY u.id, cat.id;

-- consulta: exercicio_2_solucao
SELECT u.id,
       u.nome AS usuario,
       COUNT(l.id) FILTER (
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
