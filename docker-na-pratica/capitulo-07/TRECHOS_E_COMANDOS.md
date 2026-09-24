# Capítulo 7 — trechos e comandos para consulta

> NÃO EXECUTE ESTE ARQUIVO INTEIRO. Ele contém comandos, trechos parciais, modelos, saídas e falhas deliberadas. Use somente a etapa indicada no livro, com suas pré-condições e verificações.

Fonte: manuscrito consolidado R02. O texto de cada bloco foi preservado, inclusive quebras reais. A numeração abaixo localiza os blocos neste arquivo; não é uma sequência automática de execução.

Marcadores como `ID_OBTIDO` não são valores reais. Comandos de remoção, alterações e falhas controladas exigem a identificação prévia dos recursos. Os parágrafos de contexto são lembretes; não substituem a seção completa do livro.

## Trecho 001 — Retome o estado sem perder as anotações

**Contexto do livro:**

> Preserve esse volume, a pasta de bind mount e a cópia de recuperação do capítulo anterior. O ZIP desta entrega contém os arquivos do programa, não uma cópia dos seus dados reais. Extraia-o em uma pasta nova; não sobrescreva sua pasta de backup ou seus arquivos editados.

> Nesta etapa, execute os comandos a partir da pasta laboratorio do ZIP, um nível acima de catalogo-estudos. A estrutura relevante é:

```text
laboratorio/
    catalogo-estudos/    aplicação 1.4, sem alteração
        .env.cap06
        Dockerfile
        app.js
        ...
    entrada/            novo componente Nginx
        Dockerfile
        nginx.conf
        .dockerignore
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 002 — Retome o estado sem perder as anotações

**Contexto do livro:**

> Continuamos com containers Linux, Docker Engine local e o mesmo contexto dos capítulos anteriores. A rede bridge desta prática conecta containers no mesmo daemon; criar uma rede com o mesmo nome em outro computador não une os dois ambientes. [1]

> Consulte antes de modificar:

```text
docker version
docker ps -a --filter name=catalogo
docker image ls tnp-catalogo
docker volume inspect tnp-catalogo-dados
docker inspect --format "{{json .Mounts}}" catalogo-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 003 — Retome o estado sem perder as anotações

**Contexto do livro:**

> Reservaremos a rede tnp-catalogo-rede, o alias catalogo, o container catalogo-entrada e a imagem tnp-entrada:1.0. O exercício final utilizará tnp-rede-revisao e catalogo-revisao. Confirme nomes completos antes de qualquer criação. Filtros podem encontrar correspondências parciais; não remova objetos desconhecidos.

> Se apenas a imagem tnp-catalogo:1.4 estiver ausente, reconstrua-a da pasta fornecida, sem alterar a aplicação. Esse é um caminho de recuperação, não um build obrigatório para quem preservou a imagem:

```text
docker build -t tnp-catalogo:1.4 ./catalogo-estudos
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 004 — Uma rede não é uma pasta compartilhada

**Contexto do livro:**

> No capítulo anterior, uma montagem ligava um caminho do container a um armazenamento. Uma rede cria outra relação: permite que processos enviem mensagens entre ambientes de execução.

> Uma consulta HTTP às anotações seguirá este percurso:

```text
Processo cliente
    -> conexão HTTP com o catálogo
    -> processo Node.js lê o arquivo no volume
    -> resposta JSON volta ao cliente
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 005 — Bridge: o driver e a rede que já existia

**Contexto do livro:**

> Consulte as redes conhecidas pelo Engine:

```text
docker network ls
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 006 — Bridge: o driver e a rede que já existia

**Contexto do livro:**

> Até aqui, os containers criados sem --network utilizaram a configuração padrão. Agora criaremos uma bridge própria do projeto. Ela oferece resolução automática de nomes e aliases entre containers conectados. Na bridge padrão, não devemos presumir essa mesma descoberta automática por nome. Não usaremos o mecanismo legado --link nem manteremos IPs manualmente em arquivos de hosts. [1]

> Verifique primeiro se o nome está livre:

```text
docker network inspect tnp-catalogo-rede
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 007 — Bridge: o driver e a rede que já existia

**Contexto do livro:**

> Na primeira execução, a mensagem de rede inexistente é esperada. Ela não equivale a uma falha de acesso ao Engine. Se houver uma rede com esse nome, examine origem, driver e participantes antes de reutilizá-la.

> Crie somente a rede nova do laboratório:

```text
docker network create --driver bridge --label tnp.capitulo=07 tnp-catalogo-rede
docker network inspect tnp-catalogo-rede
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 008 — Conecte o catálogo sem reconstruí-lo

**Contexto do livro:**

> Confirme que o container principal é o do capítulo anterior. Inicie-o e teste seu próprio servidor:

```text
docker start catalogo-web
docker exec catalogo-web node diagnostico.js
docker exec catalogo-web node anotar.js --listar
docker inspect --format "{{.Id}}" catalogo-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 009 — Conecte o catálogo sem reconstruí-lo

**Contexto do livro:**

> Espere a sonda retornar HTTP 200 antes de continuar. Se houver uma corrida logo após o início, consulte os logs e repita somente a verificação; não repita run. Anote o ID e reconheça o conteúdo das anotações.

> Queremos acrescentar acesso pela rede do projeto, mantendo a instância e o volume. Conecte:

```text
docker network connect --alias catalogo tnp-catalogo-rede catalogo-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 010 — Conecte o catálogo sem reconstruí-lo

**Contexto do livro:**

> catalogo-web continua sendo o nome do container. catalogo é um alias de rede escolhido para os clientes. Um alias tem escopo na rede em que foi configurado; não é um domínio público nem uma renomeação global do container. Evite atribuir esse mesmo alias a vários destinos neste exercício: isso tornaria ambígua a intenção de consultar uma única aplicação. [7]

> Verifique o resultado:

```text
docker inspect --format "{{.Id}}" catalogo-web
docker inspect --format "{{json .NetworkSettings.Networks}}" catalogo-web
docker network inspect tnp-catalogo-rede
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 011 — Primeiro encontre o nome; depois teste o serviço

**Contexto do livro:**

> Usaremos a imagem do catálogo também como ferramenta temporária. Ela já contém Node.js e diagnostico.js; não precisamos instalar utilitários dentro do servidor nem construir outra imagem apenas para fazer uma consulta.

> A primeira tarefa consulta a resolução do alias, sem iniciar o catálogo:

```text
docker run --rm --pull=never --network tnp-catalogo-rede tnp-catalogo:1.4 node -e "require('node:dns').promises.lookup('catalogo').then(console.log).catch(e=>{console.error(e.code);process.exitCode=1})"
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 012 — Primeiro encontre o nome; depois teste o serviço

**Contexto do livro:**

> Esperamos um endereço correspondente ao catálogo na rede do projeto. Não copie esse IP para a configuração da aplicação. O objetivo é comprovar uma associação naquele momento; o endereço pode mudar quando endpoints forem recriados.

> Agora teste o protocolo e uma resposta concreta:

```text
docker run --rm --pull=never --network tnp-catalogo-rede tnp-catalogo:1.4 node diagnostico.js http://catalogo:3000/health
docker run --rm --pull=never --network tnp-catalogo-rede tnp-catalogo:1.4 node diagnostico.js http://catalogo:3000/api/anotacoes
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 013 — O loopback de quem?

**Contexto do livro:**

> Mantenha o servidor funcionando. Antes de executar, preveja o resultado desta tarefa:

```text
docker run --rm --pull=never --network tnp-catalogo-rede tnp-catalogo:1.4 node diagnostico.js http://127.0.0.1:3000/health
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 014 — A porta do host não é a porta do serviço

**Contexto do livro:**

> Agora mantenha o alias, mas use deliberadamente a porta errada:

```text
docker run --rm --pull=never --network tnp-catalogo-rede tnp-catalogo:1.4 node diagnostico.js http://catalogo:8084/health
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 015 — A consulta partiu da rede certa?

**Contexto do livro:**

> Por fim, execute sem selecionar a rede do projeto:

```text
docker run --rm --pull=never tnp-catalogo:1.4 node diagnostico.js http://catalogo:3000/health
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 016 — Desconectar é alterar acesso, não apagar a aplicação

**Contexto do livro:**

> Vamos remover temporariamente apenas a ligação que acabamos de acrescentar. Este é um laboratório local, sem outros usuários dependendo da aplicação. Não aplique desconexões experimentais a serviços compartilhados.

```text
docker network disconnect tnp-catalogo-rede catalogo-web
docker network inspect tnp-catalogo-rede
docker inspect --format "{{json .NetworkSettings.Networks}}" catalogo-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 017 — Desconectar é alterar acesso, não apagar a aplicação

**Contexto do livro:**

> Repita a sonda pela rede do projeto:

```text
docker run --rm --pull=never --network tnp-catalogo-rede tnp-catalogo:1.4 node diagnostico.js http://catalogo:3000/health
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 018 — Desconectar é alterar acesso, não apagar a aplicação

**Contexto do livro:**

> Ela não deverá alcançar o catálogo por esse alias. Entretanto, a instância continua existindo. Consulte seu estado, sua sonda interna e suas anotações:

```text
docker ps --filter name=catalogo-web
docker exec catalogo-web node diagnostico.js
docker exec catalogo-web node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 019 — Desconectar é alterar acesso, não apagar a aplicação

**Contexto do livro:**

> O objeto, o programa e os dados não foram removidos. Alteramos um endpoint de rede. Na fase atual, ainda existe a ligação anterior à bridge padrão e a publicação original, que também pode ser conferida no navegador. [10]

> A correção deve reconstruir a relação perdida, não todos os recursos:

```text
docker network connect --alias catalogo tnp-catalogo-rede catalogo-web
docker run --rm --pull=never --network tnp-catalogo-rede tnp-catalogo:1.4 node diagnostico.js http://catalogo:3000/api/anotacoes
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 020 — Uma única entrada para o navegador

**Contexto do livro:**

> O Nginx funcionará como proxy reverso: recebe a requisição do navegador, encaminha-a ao catálogo e devolve a resposta. O navegador não precisa resolver o alias catalogo; quem usa esse nome é o processo Nginx dentro da rede Docker. [11]

> O estado desejado é:

```text
Navegador no host
    -> 127.0.0.1:8084
    -> catalogo-entrada, Nginx na porta 8080
    -> catalogo:3000 na rede tnp-catalogo-rede
    -> catalogo-web, Node.js
    -> /app/dados no volume tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 021 — Construa a entrada com configuração explícita

**Contexto do livro:**

> O diretório entrada contém os únicos arquivos novos de execução deste capítulo. Não altere app.js, armazenamento.js, anotar.js, diagnostico.js, os temas ou a Edição 3 da página.

> O Dockerfile da entrada é:

```text
FROM nginx:alpine
COPY nginx.conf /etc/nginx/nginx.conf
USER nginx
EXPOSE 8080
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 022 — Construa a entrada com configuração explícita

**Contexto do livro:**

> O processo utiliza nginx, não root. O listener será 8080, o PID ficará em /tmp e os diretórios temporários necessários serão graváveis nesse local. Esses ajustes permitem uma execução sem elevar o servidor a root apenas para acessar uma porta privilegiada ou um diretório de sistema. [14]

> O arquivo completo entrada/nginx.conf é:

```text
worker_processes 1;
error_log /dev/stderr warn;
pid /tmp/nginx.pid;

events {
    worker_connections 128;
}

http {
    access_log /dev/stdout;
    client_body_temp_path /tmp/client_temp;
    proxy_temp_path /tmp/proxy_temp;
    fastcgi_temp_path /tmp/fastcgi_temp;
    uwsgi_temp_path /tmp/uwsgi_temp;
    scgi_temp_path /tmp/scgi_temp;

    server {
        listen 8080;
        server_name _;

        location / {
            proxy_pass http://catalogo:3000;
            proxy_connect_timeout 3s;
            proxy_read_timeout 5s;
            proxy_set_header Host $host;
        }
    }
}
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 023 — Construa a entrada com configuração explícita

**Contexto do livro:**

> O número de workers e o limite de conexões foram escolhidos para um laboratório pequeno; não representam dimensionamento recomendado para produção. O acesso vai para stdout e os erros para stderr, permitindo observação por docker logs. As diretivas de processo, PID e log fazem parte da configuração do Nginx. [16]

> O .dockerignore da entrada restringe os arquivos do contexto:

```text
*
!Dockerfile
!nginx.conf
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 024 — Construa a entrada com configuração explícita

**Contexto do livro:**

> Antes do build, confira se tnp-entrada:1.0 não identifica outro trabalho. Construa a partir da pasta laboratorio:

```text
docker build -t tnp-entrada:1.0 ./entrada
docker image inspect --format "{{.Id}}" tnp-entrada:1.0
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 025 — Valide no ambiente em que o nome existe

**Contexto do livro:**

> Mantenha o catálogo conectado e respondendo. Antes de colocar a entrada em execução contínua, valide sua configuração na mesma rede:

```text
docker run --rm --pull=never --network tnp-catalogo-rede tnp-entrada:1.0 -t
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 026 — Mude a publicação preservando o volume

**Contexto do livro:**

> Agora precisamos liberar 8084 no host e retirar a publicação direta do catálogo. Essa alteração exige recriar o container, como aprendemos anteriormente. A diferença é que agora existem dados a preservar.

> Confira a montagem e consulte as anotações uma última vez:

```text
docker inspect --format "{{json .Mounts}}" catalogo-web
docker exec catalogo-web node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 027 — Mude a publicação preservando o volume

**Contexto do livro:**

> Só prossiga se tnp-catalogo-dados estiver montado em /app/dados e contiver os dados esperados. Se encontrar gravações importantes somente na camada do container, proteja-as antes da substituição. Use o procedimento de cópia do capítulo 6 quando precisar atualizar seu backup, escolhendo outro destino em vez de sobrescrever uma cópia útil.

> Não execute gravações durante esta troca. Pare e remova apenas a instância confirmada, sem remover o volume:

```text
docker stop catalogo-web
docker rm catalogo-web
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 028 — Mude a publicação preservando o volume

**Contexto do livro:**

> Recrie o catálogo já na rede definitiva, com o mesmo ambiente e armazenamento, sem -p:

```text
docker run --pull=never -d --name catalogo-web --network tnp-catalogo-rede --network-alias catalogo --env-file catalogo-estudos/.env.cap06 --mount type=volume,src=tnp-catalogo-dados,dst=/app/dados tnp-catalogo:1.4
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 029 — Mude a publicação preservando o volume

**Contexto do livro:**

> Confira o novo ID, as redes, a montagem e a ausência de publicação:

```text
docker inspect --format "{{.Id}}" catalogo-web
docker inspect --format "{{json .NetworkSettings.Networks}}" catalogo-web
docker inspect --format "{{json .Mounts}}" catalogo-web
docker port catalogo-web
docker exec catalogo-web node diagnostico.js
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 030 — Mude a publicação preservando o volume

**Contexto do livro:**

> docker port não deverá listar uma associação ao host. Ainda assim, outro container conectado pode consultar catalogo:3000. Repita a prova dos dados:

```text
docker run --rm --pull=never --network tnp-catalogo-rede tnp-catalogo:1.4 node diagnostico.js http://catalogo:3000/api/anotacoes
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 031 — Inicie a entrada e verifique os dois trechos

**Contexto do livro:**

> Com o catálogo respondendo, crie o proxy:

```text
docker run --pull=never -d --name catalogo-entrada --network tnp-catalogo-rede -p 127.0.0.1:8084:8080 tnp-entrada:1.0
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 032 — Inicie a entrada e verifique os dois trechos

**Contexto do livro:**

> Se houver uma recusa de publicação, investigue quem usa o endereço e se a tentativa deixou um container criado. Não remova serviços desconhecidos. O fato de termos liberado o mapeamento antigo não impede outro programa de ocupar a porta.

> Observe:

```text
docker ps --filter name=catalogo
docker port catalogo-entrada
docker inspect --format "{{.Config.User}}" catalogo-entrada
docker network inspect tnp-catalogo-rede
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 033 — Inicie a entrada e verifique os dois trechos

**Contexto do livro:**

> Abra http://127.0.0.1:8084/. Confira Edição 3, os três temas e todas as rotas: /health, /api/config, /api/temas e /api/anotacoes. A marca da página não mudou porque o catálogo não foi reconstruído.

> Depois combine duas fontes de evidência:

```text
docker logs --tail 15 catalogo-entrada
docker logs --tail 15 catalogo-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 034 — Inicie a entrada e verifique os dois trechos

**Contexto do livro:**

> A entrada registra o atendimento, e o catálogo registra a requisição encaminhada. Em uma aplicação maior, identificadores de requisição ajudariam a correlacionar os registros; não fingiremos que a nossa pequena configuração já implementa rastreamento distribuído.

> Também é possível testar o trecho do proxy a partir da rede:

```text
docker run --rm --pull=never --network tnp-catalogo-rede tnp-catalogo:1.4 node diagnostico.js http://catalogo-entrada:8080/api/anotacoes
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 035 — Falha controlada: a entrada está ativa, mas o destino parou

**Contexto do livro:**

> Vamos interromper somente a dependência. Não apague containers, redes ou dados:

```text
docker stop catalogo-web
docker ps -a --filter name=catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 036 — Falha controlada: a entrada está ativa, mas o destino parou

**Contexto do livro:**

> A entrada continua em execução. Acesse novamente /health pela porta 8084. Neste experimento, esperamos um erro do proxy, normalmente HTTP 502, em vez do JSON do catálogo. Um timeout também pode produzir outra resposta de erro; o importante é distinguir a resposta da entrada da resposta da aplicação.

> Observe antes de corrigir:

```text
docker logs --tail 15 catalogo-entrada
docker inspect --format "{{.State.Status}}" catalogo-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 037 — Falha controlada: a entrada está ativa, mas o destino parou

**Contexto do livro:**

> Não transforme todo 502 em “o container está parado”: uma porta errada, uma recusa de conexão ou outro problema no destino pode produzir um sintoma semelhante. Aqui conhecemos a ação que provocou a falha e podemos comprová-la pelo estado. Em uma ocorrência real, precisamos reunir essa evidência.

> Retome o catálogo e confirme primeiro o trecho interno:

```text
docker start catalogo-web
docker run --rm --pull=never --network tnp-catalogo-rede tnp-catalogo:1.4 node diagnostico.js http://catalogo:3000/health
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 038 — Falha controlada: a entrada está ativa, mas o destino parou

**Contexto do livro:**

> Só depois da resposta válida, recarregue a configuração da entrada:

```text
docker exec catalogo-entrada nginx -s reload
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 039 — Pratique agora: uma consulta sem publicação e sem escrita

**Contexto do livro:**

> Os critérios de conclusão são: resposta HTTP válida com as anotações esperadas, ausência de publicação no servidor de revisão, montagem de dados com RW=false e preservação do volume original.

> Depois da verificação, pare e remova somente catalogo-revisao. Confira os participantes de tnp-rede-revisao e remova somente essa rede:

```text
docker network inspect tnp-rede-revisao
docker network rm tnp-rede-revisao
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 040 — Prepare a continuidade para o Compose

**Contexto do livro:**

> O resultado não é somente “dois containers estão rodando”. Agora existe uma definição que precisa ser reproduzida: imagens, comandos, rede, alias, ambiente, publicação, montagem e ordem de verificação.

> Com os dois servidores ativos, faça a conferência final:

```text
docker port catalogo-entrada
docker port catalogo-web
docker inspect --format "{{json .Mounts}}" catalogo-web
docker inspect --format "{{json .NetworkSettings.Networks}}" catalogo-web
docker exec catalogo-web node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 041 — Prepare a continuidade para o Compose

**Contexto do livro:**

> A entrada deve publicar 127.0.0.1:8084 para sua porta 8080; o catálogo não deve ter publicação no host. Ambos devem pertencer a tnp-catalogo-rede. O catálogo utiliza o alias catalogo, a imagem 1.4, o ambiente de .env.cap06 e o volume original no destino conhecido.

> Confira a página e as rotas uma última vez. Em seguida, deixe os dois containers parados, sem removê-los:

```text
docker stop catalogo-entrada
docker stop catalogo-web
docker ps -a --filter name=catalogo
docker network ls --filter name=tnp-catalogo-rede
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*
