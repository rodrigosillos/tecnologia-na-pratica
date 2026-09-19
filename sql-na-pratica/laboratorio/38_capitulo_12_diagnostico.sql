-- SQL na Pratica | Capitulo 12 | PostgreSQL 18
-- Dados ficticios. Execute UMA instrucao por vez no banco de estudos.
-- Use a mesma aba e conexao, com autocommit ativado.
-- Execute o arquivo 36 antes de iniciar as tarefas.

-- Etapa 1: t2_diagnostico
-- ERRO DE LOGICA INTENCIONAL: NULL sozinho nao representa a data de corte.
SELECT id, valor
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01'
  AND data_liquidacao IS NULL
ORDER BY id;
