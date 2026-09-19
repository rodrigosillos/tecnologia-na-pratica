-- SQL na Pratica | Capitulo 11 | PostgreSQL 18
-- Dados ficticios; use apenas o banco de estudos.
-- Execute UMA instrucao por vez e confira o resultado.
-- Mantenha a mesma aba e conexao, com autocommit ativado.

-- Etapa 1: preparacao
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;
SELECT current_database() AS banco,
       current_user AS usuario;
SELECT COUNT(*) AS lancamentos_originais
FROM lancamentos;

-- Etapa 2: candidata_incompleta
-- ERRO DE LOGICA INTENCIONAL: consulta candidata para diagnostico.
SELECT u.id, u.nome,
       COALESCE(SUM(l.valor), 0) AS total
FROM usuarios AS u
LEFT JOIN contas AS c ON c.usuario_id = u.id
LEFT JOIN lancamentos AS l ON l.conta_id = c.id
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id, u.nome
ORDER BY u.id;

-- Etapa 3: rastreamento
SELECT u.id AS usuario_id,
       l.id AS lancamento_id, l.valor
FROM usuarios AS u
JOIN contas AS c ON c.usuario_id = u.id
JOIN lancamentos AS l ON l.conta_id = c.id
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
ORDER BY u.id, l.id;

-- Etapa 4: consulta_revisada
SELECT u.id, u.nome,
       COALESCE(SUM(l.valor), 0) AS total
FROM usuarios AS u
LEFT JOIN contas AS c ON c.usuario_id = u.id
LEFT JOIN lancamentos AS l
  ON l.conta_id = c.id
 AND l.tipo = 'despesa'
 AND l.data_competencia >= DATE '2026-05-01'
 AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id, u.nome
ORDER BY u.id;

-- Etapa 5: conferencia_independente
SELECT COUNT(*) AS quantidade,
       SUM(valor) AS total
FROM lancamentos
WHERE tipo = 'despesa'
  AND data_competencia >= DATE '2026-05-01'
  AND data_competencia < DATE '2026-06-01';

