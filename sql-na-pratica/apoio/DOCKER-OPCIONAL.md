# Alternativa com Docker Compose

Use somente se já conhece Docker e possui Docker com Compose instalado. Este caminho substitui a instalação nativa do servidor; o pgAdmin continuará no computador. Não é requisito para ler o livro.

1. Na pasta deste arquivo, crie um arquivo `.env` com `SQL_PRATICA_ADMIN_PASSWORD=SUA_SENHA_LOCAL`. Troque o marcador por uma senha própria antes de executar; não compartilhe esse arquivo nem o coloque em repositório público. Se sua senha contiver caracteres especiais, siga as regras de citação do formato `.env` do Docker Compose.
2. Execute `docker compose up -d` nessa pasta.
3. Confira `docker compose ps` e `docker compose logs postgres`. Aguarde o servidor ficar pronto para aceitar conexões.
4. No pgAdmin instalado no computador, registre a conexão administrativa usando host `127.0.0.1`, porta **5433**, banco `postgres`, usuário `postgres` e a senha do arquivo `.env`.
5. Continue a preparação do capítulo 2: crie `estudante_sql` e o banco `sql_na_pratica` pelo pgAdmin, depois registre a conexão de estudos usando a mesma porta 5433. Execute os scripts como `estudante_sql`.

A porta 5433 do computador aponta para 5432 dentro do contêiner; a publicação é restrita ao endereço de loopback. Se 5433 já estiver ocupada, escolha outra porta livre no lado esquerdo da configuração e use-a na conexão.

O volume preserva os dados. Para parar o serviço, use `docker compose stop`; para retomá-lo, `docker compose start`. Alterar a senha no `.env` depois da inicialização não redefine a senha do banco já criado. Não use `docker compose down -v` para solucionar um problema de conexão: essa opção remove o volume e seus dados.

O arquivo fixa a imagem em `postgres:18.6`. A imagem oficial da linha 18 utiliza `/var/lib/postgresql` como destino do volume, com os dados em um subdiretório específico da versão. Antes do fechamento do livro, a versão corretiva e a disponibilidade da imagem deverão ser conferidas novamente.

Este roteiro e o Compose foram revisados na documentação e o YAML foi conferido estruturalmente; o contêiner não foi executado neste ambiente. Não substituem a validação prática de instalação e conexão.

Fontes oficiais consultadas em 17/09/2026:

- Imagem oficial: https://hub.docker.com/_/postgres
- Variáveis no Compose: https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
