-- SQL na Pratica | Capitulo 4 | Base inicial carregada.
-- Execute cada consulta separadamente para observar o resultado.
SET search_path TO sql_pratica;
SET DateStyle TO 'ISO, YMD';

-- ATENCAO: consultas identificadas como incorretas executam sem erro,
-- mas respondem a uma pergunta diferente. Nao sao modelos de solucao.

-- consulta: precedencia_incorreta
SELECT id, conta_id, tipo, valor
FROM lancamentos
WHERE conta_id = 1
   OR conta_id = 2
  AND tipo = 'despesa'
  AND valor >= 180
ORDER BY id;

-- consulta: precedencia_corrigida
SELECT id, conta_id, tipo, valor
FROM lancamentos
WHERE (conta_id = 1 OR conta_id = 2)
  AND tipo = 'despesa'
  AND valor >= 180
ORDER BY id;

-- consulta: exercicio_2_incorreto
SELECT id, descricao, valor
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia BETWEEN DATE '2026-05-01'
                          AND DATE '2026-06-01'
  AND data_liquidacao = NULL
ORDER BY id;

-- consulta: exercicio_2_correcao_parcial
-- Ainda incorreta: inclui o primeiro dia de junho.
SELECT id, descricao, valor
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia BETWEEN DATE '2026-05-01'
                          AND DATE '2026-06-01'
  AND data_liquidacao IS NULL
ORDER BY id;
