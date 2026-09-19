-- NAO EXECUTE ESTE ARQUIVO INTEIRO.
-- No Query Tool: selecione cada bloco e execute separadamente, na mesma aba.
-- No menu de execucao: Auto commit ligado e Auto rollback on error desligado.
-- Uma transacao pendente de outro trabalho deve ser resolvida antes.
-- Bloco 1: cria uma tabela temporaria e uma linha fora do schema do projeto.
BEGIN;
CREATE TEMP TABLE teste_chave_cap03 (id INTEGER PRIMARY KEY);
INSERT INTO teste_chave_cap03 (id) VALUES (1);

-- Bloco 2: ERRO INTENCIONAL. Esperado SQLSTATE 23505 (chave repetida).
INSERT INTO teste_chave_cap03 (id) VALUES (1);

-- Bloco 3: executar separado APOS o erro para recuperar a sessao.
-- Desfaz inclusive a criacao da tabela temporaria.
ROLLBACK;
