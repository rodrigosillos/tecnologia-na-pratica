-- Conecte-se a python_na_pratica; consultas somente de leitura.
SELECT current_database(), current_user, version();
SELECT id, data, descricao, categoria, valor
FROM tnp_cap06.despesas ORDER BY id;
SELECT categoria, count(*) AS quantidade, sum(valor) AS total
FROM tnp_cap06.despesas GROUP BY categoria ORDER BY categoria;
SELECT count(*) AS quantidade, COALESCE(sum(valor), 0.00) AS total
FROM tnp_cap06.despesas;
