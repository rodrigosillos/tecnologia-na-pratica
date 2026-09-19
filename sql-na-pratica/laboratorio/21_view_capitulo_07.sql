-- SQL na Prática | Capítulo 7 | Base fictícia inicial
-- Execute uma instrução por vez no banco de estudos.
-- Execute criar_view uma única vez, como proprietário do schema.
-- Nas próximas consultas, execute apenas consultar_view.
-- Repetir CREATE VIEW produz erro 42P07; não apague a base.
-- A criação guarda a definição; não modifica os lançamentos.

SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;

-- consulta: criar_view
CREATE VIEW sql_pratica.v_despesas AS
SELECT l.id AS lancamento_id,
       c.usuario_id,
       l.categoria_id,
       l.descricao,
       l.valor,
       l.data_competencia,
       l.data_liquidacao
FROM sql_pratica.lancamentos AS l
JOIN sql_pratica.contas AS c
    ON c.id = l.conta_id
WHERE l.tipo = 'despesa';

-- consulta: consultar_view
SELECT usuario_id, SUM(valor) AS total
FROM sql_pratica.v_despesas
WHERE data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
GROUP BY usuario_id
ORDER BY usuario_id;
