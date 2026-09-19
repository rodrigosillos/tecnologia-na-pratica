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


-- BLOCO 01: orcamento_previa
-- Esperado: id 1 e 300.00.
SELECT id, valor_limite
FROM orcamentos
WHERE usuario_id = 1
  AND categoria_id = 2
  AND mes_referencia = DATE '2026-05-01'
  AND valor_limite = 300.00;

-- BLOCO 02: orcamento_alterar
-- Esperado: id 1, antes 300.00, depois 330.00.
BEGIN;
UPDATE orcamentos
SET valor_limite = valor_limite * 1.10
WHERE usuario_id = 1
  AND categoria_id = 2
  AND mes_referencia = DATE '2026-05-01'
  AND valor_limite = 300.00
RETURNING id,
          old.valor_limite AS antes,
          new.valor_limite AS depois;

-- BLOCO 03: orcamento_conferir
-- Esperado: IDs 1/2/4, limites 330.00/150.00/250.00. So Ana/maio mudou.
SELECT id, usuario_id, valor_limite
FROM orcamentos
WHERE categoria_id = 2
ORDER BY id;

-- BLOCO 04: orcamento_desfazer
-- Encerra exercicio 1. Limite inicial 300.00 restaurado.
ROLLBACK;

-- BLOCO 05: zero_primeira
-- EXERCICIO 2: tentativa incompleta intencional. Esperado: id 4, 110.00.
BEGIN;
UPDATE lancamentos
SET valor = 110.00
WHERE id = 4
  AND conta_id = 1
  AND valor = 120.00
  AND data_liquidacao IS NULL
RETURNING id, valor;

-- BLOCO 06: zero_segunda
-- Esperado: ZERO linhas e NENHUM erro. Nao execute COMMIT.
UPDATE lancamentos
SET data_liquidacao = DATE '2026-05-18'
WHERE id = 4
  AND conta_id = 1
  AND valor = 120.00
  AND data_liquidacao IS NULL
RETURNING id, valor, data_liquidacao;

-- BLOCO 07: zero_diagnostico
-- Esperado: id 4, 110.00, NULL. Operacao de negocio incompleta.
SELECT id, valor, data_liquidacao
FROM lancamentos
WHERE id = 4;

-- BLOCO 08: zero_desfazer
-- Desfaca a tentativa antes da solucao.
ROLLBACK;

-- BLOCO 09: zero_solucao
-- Solucao: esperado id 4, 110.00, 2026-05-18. Uma linha.
BEGIN;
UPDATE lancamentos
SET valor = 110.00,
    data_liquidacao = DATE '2026-05-18'
WHERE id = 4
  AND conta_id = 1
  AND valor = 120.00
  AND data_liquidacao IS NULL
RETURNING id, valor, data_liquidacao;

-- BLOCO 10: zero_final
-- Encerra exercicio 2. Esperado: id 4, 120.00, NULL.
ROLLBACK;
SELECT id, valor, data_liquidacao
FROM lancamentos
WHERE id = 4;

