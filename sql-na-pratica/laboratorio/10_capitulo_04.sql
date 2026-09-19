-- SQL na Pratica | Capitulo 4 | Base inicial carregada.
-- Execute cada consulta separadamente para observar o resultado.
SET search_path TO sql_pratica;
SET DateStyle TO 'ISO, YMD';

-- consulta: todas_despesas
SELECT id, descricao, valor
FROM lancamentos
WHERE tipo = 'despesa'
ORDER BY id;

-- consulta: ana_maio
SELECT id, descricao, valor
FROM lancamentos
WHERE conta_id IN (1, 2)
  AND tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY id;

-- consulta: precedencia_corrigida
SELECT id, conta_id, tipo, valor
FROM lancamentos
WHERE (conta_id = 1 OR conta_id = 2)
  AND tipo = 'despesa'
  AND valor >= 180
ORDER BY id;

-- consulta: faixa_valores
SELECT id, valor
FROM lancamentos
WHERE conta_id IN (1, 2)
  AND tipo = 'despesa'
  AND valor BETWEEN 100 AND 180
ORDER BY id;

-- consulta: tres_maiores_ana_maio
SELECT id, descricao, valor
FROM lancamentos
WHERE conta_id IN (1, 2)
  AND tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
ORDER BY valor DESC, id ASC
LIMIT 3;

-- consulta: quatro_maiores_base
SELECT id, valor
FROM lancamentos
WHERE tipo = 'despesa'
ORDER BY valor DESC, id ASC
LIMIT 4;

-- consulta: busca_texto
SELECT id, descricao
FROM lancamentos
WHERE descricao LIKE 'Mer%'
ORDER BY id;

-- consulta: categorias_distintas
SELECT DISTINCT categoria_id
FROM lancamentos
WHERE conta_id IN (1, 2)
  AND tipo = 'despesa'
ORDER BY categoria_id;

-- consulta: calculo_percentual
SELECT id, valor,
       valor * 0.10 AS dez_por_cento
FROM lancamentos
WHERE id IN (2, 4)
ORDER BY id;

-- consulta: dias_desde_competencia
SELECT id,
       DATE '2026-06-10' - data_competencia
           AS dias_desde_competencia
FROM lancamentos
WHERE data_liquidacao IS NULL
ORDER BY id;

-- consulta: data_diferente
SELECT id, data_liquidacao
FROM lancamentos
WHERE id IN (2, 4, 10)
  AND data_liquidacao <> DATE '2026-05-10'
ORDER BY id;

-- consulta: data_diferente_ou_ausente
SELECT id, data_liquidacao
FROM lancamentos
WHERE id IN (2, 4, 10)
  AND (
      data_liquidacao <> DATE '2026-05-10'
      OR data_liquidacao IS NULL
  )
ORDER BY id;

-- consulta: ordenacao_nulos
SELECT id, data_liquidacao
FROM lancamentos
WHERE id IN (2, 4, 10, 11)
ORDER BY data_liquidacao ASC NULLS LAST, id ASC;

-- consulta: classificacao
SELECT id,
       CASE
           WHEN data_liquidacao IS NULL
               THEN 'pendente'
           ELSE 'liquidado'
       END AS situacao
FROM lancamentos
WHERE id IN (4, 10, 11)
ORDER BY id;

-- consulta: apresentacao_liquidacao
SELECT id,
       COALESCE(
           CAST(data_liquidacao AS TEXT),
           'Pendente'
       ) AS liquidacao_exibida
FROM lancamentos
WHERE id IN (4, 10, 11)
ORDER BY id;

