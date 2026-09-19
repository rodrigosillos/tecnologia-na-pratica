-- Capitulo 3. Base inicial carregada; execute uma consulta de cada vez.
SET search_path TO sql_pratica;
-- A. Participantes
SELECT id, nome FROM usuarios ORDER BY id;
-- B. Contas
SELECT id, usuario_id, nome FROM contas ORDER BY id;
-- C. Caminho do lancamento 7: conta 2, participante 1, Ana
SELECT id, conta_id, descricao, valor FROM lancamentos WHERE id = 7;
-- D. Conta sem movimento: zero linhas
SELECT id, descricao, valor FROM lancamentos WHERE conta_id = 4 ORDER BY id;
-- E. Escala numerica: 12.35
SELECT CAST(12.345 AS NUMERIC(12,2)) AS valor;
-- F. Competencia em maio, liquidacao em junho
SELECT id, data_competencia, data_liquidacao FROM lancamentos WHERE id = 10;
-- G. Liquidacao pendente: IDs 4 e 11
SELECT id, descricao FROM lancamentos WHERE data_liquidacao IS NULL ORDER BY id;
-- H. Categorias e tipos
SELECT id, nome, tipo FROM categorias WHERE id <= 2 ORDER BY id;
-- I. Limites de Ana para Mercado
SELECT mes_referencia, valor_limite FROM orcamentos
WHERE usuario_id = 1 AND categoria_id = 2 ORDER BY mes_referencia;
