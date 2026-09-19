# Capítulo 2 — Respostas comentadas

## Exercício 1

Se `sql_pratica.lancamentos` funciona e `lancamentos` não, confira `SHOW search_path;`. Uma nova sessão não herda o `SET` que você executou em outra conexão.

Duas formas de continuar:

```sql
SELECT COUNT(*) FROM sql_pratica.lancamentos;
```

Ou prepare a sessão e depois consulte:

```sql
SET search_path TO sql_pratica;
SELECT COUNT(*) FROM lancamentos;
```

Nenhuma das duas alternativas recria a tabela. Se nem o nome completo funcionar, reveja o banco, a carga e as permissões.

## Exercício 2

Execute `laboratorio/06_exercicios_capitulo_02.sql` uma instrução por vez. Com o limite de 180.00, a resposta deve conter **IDs 2 e 6**, ambos de 180.00.

Salvar e reabrir o arquivo preserva o texto da consulta, mas não a conexão ou as configurações da sessão. Antes de executar de novo, confira banco e usuário com o arquivo 00. Execute o `SET search_path` se usar nomes de tabelas sem o schema. Se selecionar somente o SELECT, um SET fora da seleção não será executado.
