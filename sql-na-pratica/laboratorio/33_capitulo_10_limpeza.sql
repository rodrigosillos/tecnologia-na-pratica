-- SQL na Pratica - Capitulo 10. Banco de estudos, dados ficticios.
-- MESMA ABA E CONEXAO em todo o percurso. Autocommit ligado.
-- Encerre qualquer transacao pendente antes de comecar.
-- Execute UMA INSTRUCAO por vez, ate o ponto e virgula, na ordem.
-- Ordem: 30 (carga), 31 (planos), 32 (exercicios), 33 (limpeza).
-- A tabela e temporaria: fechar a conexao a remove.
-- Os planos podem variar; quantidades e totais devem coincidir.
-- Todos os EXPLAIN ANALYZE deste pacote medem apenas SELECTs.

-- BLOCO 01: limpeza
-- Execute SOMENTE apos concluir as comparacoes e os exercicios. Remove tabela temporaria e indice.
DROP TABLE pg_temp.despesas_teste;

-- BLOCO 02: conferencia_final
-- Esperado: 12 lancamentos originais; nenhuma linha das cinco tabelas foi alterada.
SELECT COUNT(*) AS lancamentos_originais
FROM sql_pratica.lancamentos;

