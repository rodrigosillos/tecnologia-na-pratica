-- SQL na Pratica - Capitulo 9. Dados ficticios, banco de estudos.
-- Execute UM BLOCO POR VEZ, na MESMA ABA E CONEXAO do Query Tool.
-- Dentro do bloco, selecione UMA INSTRUCAO por vez, na ordem.
-- Uma instrucao termina no ponto e virgula. Confira sua saida.
-- Nao execute este arquivo inteiro nem todos os scripts em um laco.
-- Use Auto commit ligado e Auto rollback on error desligado.
-- Antes de comecar, finalize qualquer transacao anterior.
-- Em caso de divergencia, pare; se estiver em transacao, ROLLBACK.
-- Os ensaios terminam em ROLLBACK; somente o arquivo 27 confirma
-- a criacao e a remocao do usuario de teste. Veja as pausas nele.
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;


-- BLOCO 01: preparar_savepoint
-- Esperado: UPDATE de uma linha, id 4, 120.00, 2026-05-18; savepoint criado.
BEGIN;
UPDATE lancamentos
SET data_liquidacao = DATE '2026-05-18'
WHERE id = 4
  AND conta_id = 1
  AND valor = 120.00
  AND data_liquidacao IS NULL
RETURNING id, valor, data_liquidacao;
SAVEPOINT antes_valor;

-- BLOCO 02: erro_check
-- ERRO INTENCIONAL 23514. Execute isoladamente. Nao corrija o valor ainda.
UPDATE lancamentos
SET valor = 0
WHERE id = 4;

-- BLOCO 03: erro_transacao
-- ERRO INTENCIONAL 25P02. A transacao continua em estado de erro.
SELECT id, valor
FROM lancamentos
WHERE id = 4;

-- BLOCO 04: recuperar_savepoint
-- Recuperacao: execute isoladamente na mesma conexao. Esperado: id 4, 120.00, 2026-05-18.
ROLLBACK TO SAVEPOINT antes_valor;
SELECT id, valor, data_liquidacao
FROM lancamentos
WHERE id = 4;

-- BLOCO 05: encerrar_savepoint
-- ROLLBACK completo. Esperado: id 4, 120.00, NULL.
RELEASE SAVEPOINT antes_valor;
ROLLBACK;
SELECT id, valor, data_liquidacao
FROM lancamentos
WHERE id = 4;

