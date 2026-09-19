# Preparação do laboratório no pgAdmin

Este roteiro acompanha o capítulo 2 de **SQL na Prática**, de Rodrigo Sillos. O objetivo é criar um ambiente de estudos separado, carregar dados fictícios e conferir a primeira consulta. Todos os valores da amostra representam reais.

## 1. Instale e abra as ferramentas

Use **PostgreSQL 18** e **pgAdmin 4**. Siga o caminho do seu sistema operacional no capítulo 2. O servidor guarda os dados; o pgAdmin é o cliente usado para enviar consultas. Fechar o pgAdmin não necessariamente encerra o servidor.

- [Downloads oficiais do PostgreSQL](https://www.postgresql.org/download/)
- [Downloads oficiais do pgAdmin](https://www.pgadmin.org/download/)

Anote a porta escolhida na instalação. A porta padrão do PostgreSQL é **5432**. A alternativa Docker deste pacote usa **5433** no computador. Se você já possui outro servidor, preserve-o e confira a porta antes de conectar.

## 2. Prepare o usuário de estudos

Abra a conexão administrativa local no pgAdmin. Se necessário, use **Servers > Register > Server**. Na aba **General**, escolha um nome identificável. Na aba **Connection**, informe o host local, a porta da sua instalação, o banco `postgres`, o usuário administrativo `postgres` e a senha definida na instalação.

Crie o usuário pelo menu **Login/Group Roles > Create > Login/Group Role**:

| Campo | Valor |
| --- | --- |
| Name | `estudante_sql` |
| Password | Uma senha local escolhida por você |
| Can login? | Yes |
| Superuser? | No |
| Create roles? | No |
| Create databases? | No |

Mantenha os demais privilégios administrativos desativados. Se a role já existir, confira sua configuração; não apague usuários ou bancos anteriores para repetir o roteiro.

## 3. Crie o banco e uma conexão própria

Na conexão administrativa, abra **Databases > Create > Database**. Informe:

| Campo | Valor |
| --- | --- |
| Database | `sql_na_pratica` |
| Owner | `estudante_sql` |
| Encoding | `UTF8` |

Registre outra conexão em **Servers > Register > Server**, agora com estes dados:

| Campo | Valor |
| --- | --- |
| Nome visual | SQL na Prática |
| Host name/address | `127.0.0.1` |
| Port | A porta anotada na instalação |
| Maintenance database | `sql_na_pratica` |
| Username | `estudante_sql` |
| Password | A senha do usuário de estudos |

Use essa conexão nas atividades. Se `sql_na_pratica` já contiver um laboratório que você deseja preservar, crie outro banco vazio, por exemplo `sql_na_pratica_estudo`, com o mesmo proprietário. Nesse caso, substitua o nome do banco nas conferências. O schema continuará se chamando `sql_pratica`.

## 4. Confira a sessão

Selecione seu banco e abra **Tools > Query Tool**. Extraia todo o ZIP antes de abrir os arquivos da pasta `laboratorio`.

Abra `00_verificar_conexao.sql`. Selecione e execute **uma instrução completa por vez**, até o ponto e vírgula. Use **Execute script** para executar a seleção. Na documentação consultada, o atalho é F5. O comando **Execute query** também pode executar a consulta sob o cursor: por isso, neste roteiro, selecione explicitamente o trecho desejado.

Confira:

| Verificação | Resultado esperado |
| --- | --- |
| `current_database()` | `sql_na_pratica`, ou o outro banco de estudos criado por você |
| `current_user` | `estudante_sql` |
| `server_version` | Uma versão da linha 18 |
| `server_encoding` | `UTF8` |

No menu de execução, mantenha **Auto commit ativado**. Para as experiências de erro controlado dos capítulos 3 e 9, mantenha também **Auto rollback on error desativado**. Assim você poderá observar o erro e recuperar a transação explicitamente. Os comandos `BEGIN`, `COMMIT` e `ROLLBACK` dos arquivos continuam necessários.

## 5. Crie as tabelas e carregue os dados

1. Abra `01_estrutura.sql`, retire qualquer seleção parcial e execute **o arquivo inteiro**. Ele abre e confirma sua própria transação.
2. Confira a área **Messages**. Se houve erro, pare e trate o primeiro erro antes de continuar.
3. Abra `02_dados.sql` e execute **o arquivo inteiro, uma única vez**.
4. Abra `04_conferencias.sql` e execute cada instrução separadamente.

As contagens devem ser:

| Tabela | Linhas |
| --- | ---: |
| categorias | 7 |
| contas | 4 |
| lancamentos | 12 |
| orcamentos | 5 |
| usuarios | 3 |

As outras conferências retornam **480.00** para o recorte inicial e **1** conta sem movimento. Expandir a árvore ou usar Refresh apenas atualiza a visualização; não carrega os dados.

## 6. Execute a primeira consulta

```sql
SET search_path TO sql_pratica;

SELECT id, descricao, valor
FROM lancamentos
WHERE conta_id = 1
  AND tipo = 'despesa'
  AND valor >= 100
ORDER BY id;
```

Execute o `SET` primeiro; depois selecione e execute o `SELECT` completo. O resultado é:

| id | descricao | valor |
| ---: | --- | ---: |
| 2 | Mercado | 180.00 |
| 4 | Internet | 120.00 |
| 6 | Mercado | 180.00 |

Os dois lançamentos de Mercado são registros diferentes. A consulta seleciona despesas registradas, sem restringir mês ou pagamento. Um resultado visualmente plausível ainda precisa ser confrontado com a pergunta.

## Como continuar

Consulte o **MAPA-DO-LABORATORIO.md** para localizar os arquivos do capítulo. O **ROTEIRO-DE-EXECUCAO.md** detalha as pausas, conexões e resultados. Os arquivos **RESPOSTAS** e **RESULTADOS-ESPERADOS.md** ajudam a conferir sua solução.

Uma nova aba do Query Tool pode usar outra conexão. Refaça a preparação da sessão quando necessário. Nos capítulos de transações e de tabela temporária, mantenha a mesma aba e conexão durante a experiência.

## Referências de interface

Instruções conferidas na documentação do pgAdmin 4 9.18 em 19/09/2026. Menus podem variar com o idioma e a versão. Esta conferência documental não equivale a uma execução do aplicativo.

- [Registro de servidor](https://www.pgadmin.org/docs/pgadmin4/9.18/server_dialog.html)
- [Criação de role](https://www.pgadmin.org/docs/pgadmin4/9.18/role_dialog.html)
- [Criação de banco](https://www.pgadmin.org/docs/pgadmin4/9.18/database_dialog.html)
- [Execução e opções de transação](https://www.pgadmin.org/docs/pgadmin4/9.18/query_tool_toolbar.html)
