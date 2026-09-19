-- SQL na Pratica | Capitulo 4 | Base inicial carregada.
-- Execute cada consulta separadamente para observar o resultado.
SET search_path TO sql_pratica;
SET DateStyle TO 'ISO, YMD';

-- consulta: exercicio_1_solucao
SELECT id, descricao, valor,
       CASE
           WHEN data_liquidacao IS NULL
               THEN 'pendente'
           ELSE 'liquidado'
       END AS situacao
FROM lancamentos
WHERE conta_id IN (1, 2)
  AND tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY valor DESC, id ASC;

-- consulta: exercicio_2_solucao
SELECT id, descricao, valor
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
  AND data_liquidacao IS NULL
ORDER BY id;

