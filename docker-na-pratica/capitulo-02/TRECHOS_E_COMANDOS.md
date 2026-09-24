# Capítulo 2 — trechos e comandos para consulta

> NÃO EXECUTE ESTE ARQUIVO INTEIRO. Ele contém comandos, trechos parciais, modelos, saídas e falhas deliberadas. Use somente a etapa indicada no livro, com suas pré-condições e verificações.

Fonte: manuscrito consolidado R02. O texto de cada bloco foi preservado, inclusive quebras reais. A numeração abaixo localiza os blocos neste arquivo; não é uma sequência automática de execução.

Marcadores como `ID_OBTIDO` não são valores reais. Comandos de remoção, alterações e falhas controladas exigem a identificação prévia dos recursos. Os parágrafos de contexto são lembretes; não substituem a seção completa do livro.

## Trecho 001 — Um processo que precisa permanecer ativo

**Contexto do livro:**

> Isso cria um contraste útil com hello-world.

> No primeiro capítulo:

```text
processo inicia
    ↓
imprime uma mensagem
    ↓
processo termina
    ↓
container fica parado
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 002 — Um processo que precisa permanecer ativo

**Contexto do livro:**

> Agora esperamos:

```text
processo inicia
    ↓
servidor fica aguardando requisições
    ↓
processo permanece ativo
    ↓
container permanece em execução
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 003 — Criando e iniciando o primeiro servidor

**Contexto do livro:**

> Execute:

```text
docker run -d --name web-lab nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 004 — Criando e iniciando o primeiro servidor

**Contexto do livro:**

> docker run cria um novo container e inicia o processo definido pela imagem.

> A opção:

```text
-d
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 005 — Criando e iniciando o primeiro servidor

**Contexto do livro:**

> significa detached mode. Em vez de manter o terminal anexado à saída principal do container, Docker inicia o container em segundo plano e devolve o controle do terminal.

> A opção:

```text
--name web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 006 — Criando e iniciando o primeiro servidor

**Contexto do livro:**

> define um nome legível para o container.

> Por fim:

```text
nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 007 — Observe antes de fazer qualquer outra coisa

**Contexto do livro:**

> Execute:

```text
docker ps
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 008 — Observe antes de fazer qualquer outra coisa

**Contexto do livro:**

> Procure uma linha cujo nome seja:

```text
web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 009 — Container ativo não significa aplicação acessível

**Contexto do livro:**

> O container está em execução. O servidor Nginx também está em execução dentro dele.

> Agora tente abrir no navegador:

```text
http://127.0.0.1:8080
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 010 — Container ativo não significa aplicação acessível

**Contexto do livro:**

> Temos evidências de que o container está em execução. Então precisamos investigar o que falta entre o processo dentro do container e o navegador no host.

> Pergunte ao Docker quais portas desse container foram publicadas:

```text
docker port web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 011 — Expor não é o mesmo que publicar

**Contexto do livro:**

> Para isso, precisamos publicar uma porta.

> A forma básica é:

```text
-p HOST_PORT:CONTAINER_PORT
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 012 — Expor não é o mesmo que publicar

**Contexto do livro:**

> Por exemplo:

```text
-p 8080:80
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 013 — Expor não é o mesmo que publicar

**Contexto do livro:**

> significa:

```text
host:8080
    ↓
container:80
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 014 — Expor não é o mesmo que publicar

**Contexto do livro:**

> Quando você publica apenas 8080:80, Docker normalmente associa a porta a todas as interfaces do host. Em um ambiente de desenvolvimento, muitas vezes queremos que o serviço seja acessível apenas pela própria máquina.

> Por isso, nossos exemplos locais usarão:

```text
-p 127.0.0.1:8080:80
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 015 — Expor não é o mesmo que publicar

**Contexto do livro:**

> A leitura fica:

```text
127.0.0.1 do host, porta 8080
              ↓
container, porta 80
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 016 — Podemos adicionar a porta ao container atual?

**Contexto do livro:**

> iniciar novamente preserva a configuração do container existente; recriar permite aplicar uma nova configuração.

> Antes de remover qualquer coisa, observe o estado atual mais uma vez:

```text
docker ps
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 017 — Podemos adicionar a porta ao container atual?

**Contexto do livro:**

> Confirme que web-lab está em execução.

> Agora interrompa o container:

```text
docker stop web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 018 — Podemos adicionar a porta ao container atual?

**Contexto do livro:**

> Verifique:

```text
docker ps
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 019 — Podemos adicionar a porta ao container atual?

**Contexto do livro:**

> Ele não deverá aparecer entre os containers ativos.

> Depois:

```text
docker ps -a
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 020 — Podemos adicionar a porta ao container atual?

**Contexto do livro:**

> A diferença entre "parado" e "removido" continua importante.

> Somente depois dessa verificação, remova o container:

```text
docker rm web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 021 — Podemos adicionar a porta ao container atual?

**Contexto do livro:**

> Confirme:

```text
docker ps -a --filter name=web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 022 — Podemos adicionar a porta ao container atual?

**Contexto do livro:**

> A imagem, porém, não foi removida.

> Você pode conferir:

```text
docker image ls nginx
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 023 — Podemos adicionar a porta ao container atual?

**Contexto do livro:**

> Esse pequeno exercício mostra o escopo das ações:

```text
docker stop
    ↓
interrompe a execução
container continua existindo


docker rm
    ↓
remove o objeto container
imagem continua existindo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 024 — Recriando com a porta publicada

**Contexto do livro:**

> Agora execute:

```text
docker run -d --name web-lab -p 127.0.0.1:8080:80 nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 025 — Recriando com a porta publicada

**Contexto do livro:**

> um mapeamento entre a porta 8080 do host e a porta 80 do container.

> Verifique:

```text
docker ps
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 026 — Recriando com a porta publicada

**Contexto do livro:**

> Depois consulte diretamente o mapeamento:

```text
docker port web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 027 — Recriando com a porta publicada

**Contexto do livro:**

> A forma exata da saída pode variar conforme o ambiente e a pilha de rede, mas deverá existir uma associação para a porta HTTP do container.

> Agora abra:

```text
http://127.0.0.1:8080
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 028 — Recriando com a porta publicada

**Contexto do livro:**

> O ponto principal não é a página.

> É a cadeia que agora conseguimos explicar:

```text
navegador
    ↓
127.0.0.1:8080 no host
    ↓
regra de publicação do Docker
    ↓
porta 80 do container
    ↓
processo Nginx
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 029 — Se a porta 8080 já estiver ocupada

**Contexto do livro:**

> Não escolha comandos aleatórios para "destravar" a situação.

> Primeiro observe se outro container já publica essa porta:

```text
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 030 — Se a porta 8080 já estiver ocupada

**Contexto do livro:**

> Antes de repetir docker run, consulte docker ps -a --filter name=web-lab. Uma falha de publicação pode deixar o container criado e o nome ocupado. Se o objeto existir, confira docker inspect web-lab. Remova com docker rm web-lab somente a tentativa descartável deste laboratório que não iniciou e não contém dados a preservar. Se o objeto não existir, omita a remoção. Não apague um servidor desconhecido para reutilizar o nome.

> Para continuar o laboratório sem interferir em outro serviço, você pode escolher outra porta no host:

```text
docker run -d --name web-lab -p 127.0.0.1:8081:80 nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 031 — Se a porta 8080 já estiver ocupada

**Contexto do livro:**

> Nesse caso, o acesso passa a ser:

```text
http://127.0.0.1:8081
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 032 — Logs: o que o processo está dizendo

**Contexto do livro:**

> Até agora, usamos estado e configuração. Falta outra fonte de evidência: a saída produzida pela aplicação.

> Execute:

```text
docker logs web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 033 — Logs: o que o processo está dizendo

**Contexto do livro:**

> No nosso laboratório, você deverá ver mensagens do Nginx e de seu processo de inicialização.

> Agora abra ou atualize a página no navegador algumas vezes e execute novamente:

```text
docker logs web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 034 — Logs: o que o processo está dizendo

**Contexto do livro:**

> Você deverá encontrar registros de requisições HTTP.

> Isso cria uma ligação importante:

```text
usuário acessa a aplicação
    ↓
processo recebe a requisição
    ↓
aplicação produz saída de log
    ↓
docker logs permite consultá-la
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 035 — Logs: o que o processo está dizendo

**Contexto do livro:**

> Se quiser ver apenas as últimas linhas:

```text
docker logs --tail 10 web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 036 — Logs: o que o processo está dizendo

**Contexto do livro:**

> Para acompanhar novas mensagens à medida que são produzidas:

```text
docker logs -f web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 037 — Logs: o que o processo está dizendo

**Contexto do livro:**

> Isso interrompe o comando local que está seguindo os logs; não significa, por si só, parar o container.

> Confirme depois:

```text
docker ps --filter name=web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 038 — docker inspect: configuração e estado detalhados

**Contexto do livro:**

> Quando precisamos de detalhes de configuração e estado, usamos inspeção.

> Execute:

```text
docker inspect web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 039 — docker inspect: configuração e estado detalhados

**Contexto do livro:**

> Podemos pedir apenas alguns valores.

> Para o estado:

```text
docker inspect --format "{{.State.Status}}" web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 040 — docker inspect: configuração e estado detalhados

**Contexto do livro:**

> Para a imagem configurada:

```text
docker inspect --format "{{.Config.Image}}" web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 041 — docker inspect: configuração e estado detalhados

**Contexto do livro:**

> Para observar a estrutura de portas:

```text
docker inspect --format "{{json .NetworkSettings.Ports}}" web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 042 — docker inspect: configuração e estado detalhados

**Contexto do livro:**

> A saída exata do último comando pode variar, mas o objetivo é identificar a configuração, não copiar um texto esperado.

> Compare as fontes:

```text
docker ps
    visão resumida do estado


docker logs
    saída produzida pelo processo


docker inspect
    configuração e estado detalhados do objeto
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 043 — Parar não é destruir

**Contexto do livro:**

> responde no navegador.

> Execute:

```text
docker stop web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 044 — Parar não é destruir

**Contexto do livro:**

> Esse comportamento importa porque "parar" não deve ser entendido como simplesmente cortar a execução sem dar oportunidade para o processo encerrar adequadamente.

> Agora verifique:

```text
docker ps --filter name=web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 045 — Parar não é destruir

**Contexto do livro:**

> O container não deverá aparecer como ativo.

> Depois:

```text
docker ps -a --filter name=web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 046 — Antes do stop

**Contexto do livro:**

> Temos:

```text
container existe
processo ativo
aplicação responde
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 047 — Depois do stop

```text
container existe
processo parado
aplicação não responde
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 048 — start: iniciar novamente o mesmo container

**Contexto do livro:**

> Agora queremos voltar ao estado anterior sem mudar a configuração.

> Essa é exatamente a situação para:

```text
docker start web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 049 — start: iniciar novamente o mesmo container

**Contexto do livro:**

> Verifique:

```text
docker ps --filter name=web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 050 — start: iniciar novamente o mesmo container

**Contexto do livro:**

> Consulte novamente a porta:

```text
docker port web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 051 — restart: parar e iniciar novamente

**Contexto do livro:**

> Há situações em que queremos reiniciar o processo sem executar manualmente stop e depois start.

> Execute:

```text
docker restart web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 052 — restart: parar e iniciar novamente

**Contexto do livro:**

> Depois:

```text
docker ps --filter name=web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 053 — restart: parar e iniciar novamente

**Contexto do livro:**

> restart não significa "criar outro container".

> Conceitualmente:

```text
mesmo container
    ↓
interrompe processo
    ↓
inicia novamente
    ↓
mesma configuração de criação
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 054 — Uma falha controlada: o container existe, mas não inicia como esperado

**Contexto do livro:**

> Até aqui, nossas operações principais funcionaram. Um livro prático, porém, precisa preparar você para resultados diferentes.

> Imagine que você execute um novo docker run tentando usar o mesmo nome enquanto web-lab ainda existe:

```text
docker run -d --name web-lab nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 055 — Uma falha controlada: o container existe, mas não inicia como esperado

**Contexto do livro:**

> A reação útil não é mudar nomes aleatoriamente até algum comando funcionar.

> Pergunte primeiro:

```text
docker ps -a --filter name=web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 056 — Uma falha controlada: o container existe, mas não inicia como esperado

**Contexto do livro:**

> A partir daí, a decisão depende da intenção.

> Se quer continuar usando o container existente:

```text
docker start web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 057 — Uma falha controlada: o container existe, mas não inicia como esperado

**Contexto do livro:**

> O problema não é "Docker não deixa criar".

> O problema concreto é:

```text
estado atual:
existe um container chamado web-lab

estado desejado:
criar outro container com o mesmo nome

conflito:
um nome precisa identificar um único container naquele daemon
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 058 — Remover: qual objeto desaparece?

**Contexto do livro:**

> Vamos encerrar o laboratório.

> Antes de remover, confirme:

```text
docker ps --filter name=web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 059 — Remover: qual objeto desaparece?

**Contexto do livro:**

> Se estiver em execução, pare-o:

```text
docker stop web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 060 — Remover: qual objeto desaparece?

**Contexto do livro:**

> Agora remova:

```text
docker rm web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 061 — Remover: qual objeto desaparece?

**Contexto do livro:**

> Verifique:

```text
docker ps -a --filter name=web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 062 — Remover: qual objeto desaparece?

**Contexto do livro:**

> O container não deverá mais existir.

> Confira a imagem:

```text
docker image ls nginx
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 063 — Remover: qual objeto desaparece?

**Contexto do livro:**

> Ela deverá continuar disponível localmente.

> Essa separação merece ser repetida:

```text
imagem
    ↓
serve de base para criar containers

container
    ↓
objeto criado a partir da imagem
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 064 — Remover: qual objeto desaparece?

**Contexto do livro:**

> Remover o container não equivale a remover a imagem.

> Também existe:

```text
docker rm -f web-lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 065 — Quando --rm faz sentido

**Contexto do livro:**

> Existe outra estratégia para containers descartáveis.

> A opção:

```text
--rm
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 066 — Quando --rm faz sentido

**Contexto do livro:**

> Mas há uma troca.

> No primeiro capítulo, manter o container hello-world depois da execução foi útil porque pudemos observá-lo com:

```text
docker ps -a
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 067 — Quando --rm faz sentido

**Contexto do livro:**

> Se ele tivesse sido removido automaticamente, perderíamos esse objeto para inspeção posterior.

> Portanto:

```text
container descartável e sem necessidade de análise posterior
    ↓
--rm pode ser conveniente

container que pode precisar de diagnóstico após encerrar
    ↓
manter o objeto pode ser mais útil
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 068 — O ciclo de vida que você acabou de controlar

**Contexto do livro:**

> Podemos agora representar o laboratório inteiro:

```text
IMAGEM
nginx:alpine
    ↓

docker run
    ↓
CONTAINER CRIADO + INICIADO
    ↓
STATUS: running
    ↓

docker stop
    ↓
STATUS: exited/stopped
    ↓

docker start
    ↓
STATUS: running
    ↓

docker restart
    ↓
mesmo container volta a executar
    ↓

docker stop
    ↓

docker rm
    ↓
CONTAINER NÃO EXISTE MAIS

imagem continua disponível
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 069 — Executar docker run toda vez que quer iniciar a aplicação

**Contexto do livro:**

> docker run cria um novo container.

> Se você já possui um container parado e pretende apenas iniciar aquele mesmo objeto, use:

```text
docker start NOME
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 070 — Achar que docker ps vazio significa que não existem containers

**Contexto do livro:**

> docker ps mostra, por padrão, containers em execução.

> Para incluir os parados:

```text
docker ps -a
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 071 — Confundir porta do host com porta do container

**Contexto do livro:**

> Em:

```text
127.0.0.1:8080:80
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 072 — Publicar serviços sem pensar na interface de rede

**Contexto do livro:**

> A forma curta:

```text
-p 8080:80
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 073 — Publicar serviços sem pensar na interface de rede

**Contexto do livro:**

> pode publicar a porta em todas as interfaces do host.

> Para laboratórios locais, preferimos:

```text
-p 127.0.0.1:8080:80
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 074 — Remover antes de observar

**Contexto do livro:**

> Quando um container falha ou encerra inesperadamente, apagar imediatamente pode eliminar informações úteis para análise.

> Antes de remover, considere:

```text
docker ps -a
docker logs NOME
docker inspect NOME
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 075 — Pratique agora: opere o ciclo completo sem copiar a sequência anterior

**Contexto do livro:**

> Agora você fará um segundo laboratório com menos orientação.

> O objetivo é criar um servidor chamado:

```text
web-pratica
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 076 — 3. Verifique a aplicação

**Contexto do livro:**

> Acesse:

```text
http://127.0.0.1:8082
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 077 — Verificação do capítulo

**Contexto do livro:**

> quando --rm pode ser útil e quando pode atrapalhar um diagnóstico.

> Faça também esta verificação prática final:

```text
docker ps
docker ps -a
docker image ls nginx
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*
