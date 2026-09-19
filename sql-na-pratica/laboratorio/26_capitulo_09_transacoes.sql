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

-- BLOCO 01: preparacao
-- Conferir banco de estudos, usuario e 12 lancamentos. Pare se a base divergir.
SET search_path TO sql_pratica, public;
SET datestyle TO ISO, YMD;
SELECT current_database() AS banco,
       current_user AS usuario;
SELECT COUNT(*) AS quantidade
FROM lancamentos;

-- BLOCO 02: inserir
-- Esperado: 1 linha inserida, conta 2 e valor 18.50. ID gerado pode variar.
BEGIN;
INSERT INTO lancamentos (
    conta_id, categoria_id, tipo, descricao,
    valor, data_competencia, data_liquidacao
)
VALUES (
    2, 3, 'despesa', 'Transporte de teste',
    18.50, DATE '2026-05-25', NULL
)
RETURNING id, conta_id, valor;

-- BLOCO 03: contar_insercao
-- Esperado: 13. Ainda nao houve COMMIT.
SELECT COUNT(*) AS quantidade
FROM lancamentos;

-- BLOCO 04: desfazer_insercao
-- Esperado: 12. A sequencia pode ter avancado.
ROLLBACK;
SELECT COUNT(*) AS quantidade
FROM lancamentos;

-- BLOCO 05: prever_update
-- Esperado: id 4, 120.00, NULL. Pare se nao encontrar essa linha.
SELECT id, valor, data_liquidacao
FROM lancamentos
WHERE id = 4
  AND conta_id = 1
  AND tipo = 'despesa'
  AND valor = 120.00
  AND data_liquidacao IS NULL;

-- BLOCO 06: atualizar
-- Esperado: uma linha, id 4, antes NULL e depois 2026-05-18.
BEGIN;
UPDATE lancamentos
SET data_liquidacao = DATE '2026-05-18'
WHERE id = 4
  AND conta_id = 1
  AND tipo = 'despesa'
  AND valor = 120.00
  AND data_liquidacao IS NULL
RETURNING id,
          old.data_liquidacao AS antes,
          new.data_liquidacao AS depois;

-- BLOCO 07: desfazer_update
-- Esperado: id 4, 120.00, NULL.
ROLLBACK;
SELECT id, valor, data_liquidacao
FROM lancamentos
WHERE id = 4;

-- BLOCO 08: prever_delete
-- Esperado: id 7, conta 2, 30.00. Pare se divergir.
SELECT id, conta_id, valor
FROM lancamentos
WHERE id = 7
  AND conta_id = 2
  AND tipo = 'despesa'
  AND valor = 30.00;

-- BLOCO 09: excluir
-- Esperado: uma linha, id 7 e 30.00.
BEGIN;
DELETE FROM lancamentos
WHERE id = 7
  AND conta_id = 2
  AND tipo = 'despesa'
  AND valor = 30.00
RETURNING id, valor;

-- BLOCO 10: contar_exclusao
-- Esperado: 11.
SELECT COUNT(*) AS quantidade
FROM lancamentos;

-- BLOCO 11: desfazer_exclusao
-- Esperado: id 7, conta 2, 30.00. A tabela volta a 12 lancamentos.
ROLLBACK;
SELECT id, conta_id, valor
FROM lancamentos
WHERE id = 7;

