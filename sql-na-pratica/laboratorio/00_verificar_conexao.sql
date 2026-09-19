-- Execute no Query Tool conectado ao seu banco de estudos.
-- Selecione uma instrucao de cada vez para observar sua saida.
SELECT current_database() AS banco,
       current_user AS usuario;
-- Esperado no percurso principal: sql_na_pratica | estudante_sql.
-- Se voce escolheu outro nome de banco, espere esse outro nome.

SHOW server_version;
SHOW server_encoding;
-- Linha 18; UTF8. O arquivo nao cria nem altera objetos.
