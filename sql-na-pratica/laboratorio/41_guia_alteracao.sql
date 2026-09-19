-- SQL na Pratica | Guia rapido | Ensaio de alteracao
-- Use somente o banco de estudos com a base original.
-- Autocommit ativado. Mesma aba e conexao. Uma instrucao por vez.
-- Encerre a transacao anterior antes de comecar.
-- Prepare a sessao com o arquivo 40, sem repetir carga ou estrutura.
-- PREVIA: deve retornar exatamente ID 4, conta 1, 120.00, data nula.
-- Se divergir, pare e investigue. Nao altere as guardas para forcar.
SELECT id, conta_id, valor, data_liquidacao
FROM lancamentos
WHERE id = 4
  AND conta_id = 1
  AND tipo = 'despesa'
  AND valor = 120.00
  AND data_liquidacao IS NULL;

-- Execute BEGIN e depois UPDATE separadamente.
-- RETURNING: uma linha, ID 4, antes 120.00, depois 125.00.
-- Se retornar zero ou ocorrer erro, use ROLLBACK e investigue.
BEGIN;
UPDATE lancamentos
SET valor = 125.00
WHERE id = 4
  AND conta_id = 1
  AND tipo = 'despesa'
  AND valor = 120.00
  AND data_liquidacao IS NULL
RETURNING id, old.valor AS antes,
          new.valor AS depois;

-- Desfaca e confira: ID 4, valor 120.00, data nula.
-- Nao troque ROLLBACK por COMMIT. Nao rode o arquivo inteiro.
ROLLBACK;
SELECT id, valor, data_liquidacao
FROM lancamentos
WHERE id = 4;
