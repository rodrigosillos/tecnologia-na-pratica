-- SQL na Pratica | Capitulo 12 | PostgreSQL 18
-- Dados ficticios. Execute UMA instrucao por vez no banco de estudos.
-- Use a mesma aba e conexao, com autocommit ativado.

-- Etapa 1: preparacao
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;
SELECT current_database() AS banco,
       current_user AS usuario;
SELECT COUNT(*) AS lancamentos
FROM lancamentos;
