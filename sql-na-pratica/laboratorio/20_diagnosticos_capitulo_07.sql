-- SQL na Prática | Capítulo 7 | Base fictícia inicial
-- Execute uma instrução por vez no banco de estudos.
-- Diagnósticos: sem_correlacao e exercicio_2_incorreto têm erros
-- de lógica intencionais; não provocam erro de sintaxe.

SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: sem_correlacao
SELECT u.id, u.nome
FROM usuarios AS u
WHERE EXISTS (
    SELECT 1
    FROM contas AS c
    JOIN lancamentos AS l ON l.conta_id = c.id
    WHERE l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
      AND l.data_liquidacao IS NULL
)
ORDER BY u.id;

-- consulta: not_in_correspondencia
SELECT 1 NOT IN (1, NULL) AS ausente;

-- consulta: exercicio_2_incorreto
SELECT u.id, u.nome
FROM usuarios AS u
WHERE EXISTS (
    SELECT COUNT(*)
    FROM contas AS c
    JOIN lancamentos AS l ON l.conta_id = c.id
    WHERE c.usuario_id = u.id
      AND l.tipo = 'despesa'
      AND l.data_competencia >= DATE '2026-05-01'
      AND l.data_competencia < DATE '2026-06-01'
      AND l.data_liquidacao IS NULL
)
ORDER BY u.id;
