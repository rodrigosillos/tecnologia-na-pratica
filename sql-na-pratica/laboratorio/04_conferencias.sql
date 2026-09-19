-- Conferencias do estado inicial. Execute antes de experimentar alteracoes.
SET search_path TO sql_pratica, public;
SELECT 'usuarios' AS tabela, COUNT(*) AS linhas FROM usuarios
UNION ALL SELECT 'contas', COUNT(*) FROM contas
UNION ALL SELECT 'categorias', COUNT(*) FROM categorias
UNION ALL SELECT 'lancamentos', COUNT(*) FROM lancamentos
UNION ALL SELECT 'orcamentos', COUNT(*) FROM orcamentos
ORDER BY tabela;
-- Esperado: categorias 7, contas 4, lancamentos 12, orcamentos 5, usuarios 3.

SELECT SUM(valor) AS total_despesas_recorte
FROM lancamentos
WHERE conta_id = 1 AND tipo = 'despesa' AND valor >= 100;
-- Esperado: 480.00. Soma auxiliar, nao ensinada neste capitulo.

SELECT COUNT(*) AS contas_sem_movimento
FROM contas AS c
WHERE NOT EXISTS (SELECT 1 FROM lancamentos AS l WHERE l.conta_id = c.id);
-- Esperado: 1. Verificacao do conjunto para capitulos futuros.
