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


-- BLOCO 01: prever_commit
-- EXIGIDO: zero linhas. Se o id existir, pare e investigue; nao apague dados desconhecidos.
SELECT id, nome
FROM usuarios
WHERE id = 900001;

-- BLOCO 02: inserir_commit
-- Esperado: id 900001 e Teste do capitulo 9. Confira antes do bloco seguinte.
BEGIN;
INSERT INTO usuarios (id, nome)
VALUES (900001, 'Teste do capitulo 9')
RETURNING id, nome;

-- BLOCO 03: confirmar_insercao
-- EXECUTE SOMENTE depois de conferir a linha inserida. Em caso de divergencia, ROLLBACK.
COMMIT;

-- BLOCO 04: conferir_commit
-- Esperado: id 900001 e Teste do capitulo 9, agora confirmado.
SELECT id, nome
FROM usuarios
WHERE id = 900001;

-- BLOCO 05: limpar_commit
-- Esperado: EXATAMENTE o usuario criado, id 900001 e nome combinado. Confira antes de COMMIT.
BEGIN;
DELETE FROM usuarios
WHERE id = 900001
  AND nome = 'Teste do capitulo 9'
RETURNING id, nome;

-- BLOCO 06: confirmar_limpeza
-- SO CONFIRME se DELETE retornou a linha esperada. SELECT final: zero linhas.
COMMIT;
SELECT id, nome
FROM usuarios
WHERE id = 900001;

