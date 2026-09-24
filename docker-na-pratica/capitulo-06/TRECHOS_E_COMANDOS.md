# Capítulo 6 — trechos e comandos para consulta

> NÃO EXECUTE ESTE ARQUIVO INTEIRO. Ele contém comandos, trechos parciais, modelos, saídas e falhas deliberadas. Use somente a etapa indicada no livro, com suas pré-condições e verificações.

Fonte: manuscrito consolidado R02. O texto de cada bloco foi preservado, inclusive quebras reais. A numeração abaixo localiza os blocos neste arquivo; não é uma sequência automática de execução.

Marcadores como `ID_OBTIDO` não são valores reais. Comandos de remoção, alterações e falhas controladas exigem a identificação prévia dos recursos. Os parágrafos de contexto são lembretes; não substituem a seção completa do livro.

## Trecho 001 — Retome o estado do capítulo anterior

**Contexto do livro:**

> O ponto de partida é catalogo-web, criado de tnp-catalogo:1.3, parado, com publicação em 127.0.0.1:8084:3000. O cliente Docker usou .env.cap05 para configurar essa instância. A aplicação conserva a página em Edição 2 e apresenta os três temas originais. Ainda não existem anotações gravadas pelo usuário nem volumes do projeto.

> Consulte antes de modificar:

```text
docker version
docker ps -a --filter name=catalogo
docker image ls tnp-catalogo
docker volume ls
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 002 — O que realmente precisa persistir?

**Contexto do livro:**

> Sem uma montagem de dados cobrindo o caminho de gravação, mudanças ordinárias em arquivos ficam na camada gravável do container. Essa camada acompanha aquele objeto. Parar o processo não a remove; remover o container, sim. A imagem de origem não recebe automaticamente essas alterações. [1]

> Isso produz dois resultados que parecem contraditórios, mas não são:

```text
parar e iniciar o mesmo container
    -> mesma camada gravável
    -> o arquivo pode continuar lá

remover e criar outro container da mesma imagem
    -> outra camada gravável
    -> as anotações da instância anterior não acompanham a nova
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 003 — Arquivos e construção

**Contexto do livro:**

> O pacote acompanha a pasta catalogo-estudos completa nesta versão. Os arquivos JavaScript novos ou alterados também estão ao final do capítulo. Preserve temas.json e diagnostico.js. No HTML, substitua Edição 2 por Edição 3 e acrescente, junto aos demais links:

```text
<p><a href="/api/anotacoes">Ver anotações salvas</a></p>
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 004 — Arquivos e construção

**Contexto do livro:**

> O Dockerfile completo será:

```text
FROM node:24-bookworm-slim
WORKDIR /app
COPY app.js diagnostico.js armazenamento.js anotar.js ./
RUN node --check app.js && node --check diagnostico.js \
    && node --check armazenamento.js && node --check anotar.js
COPY index.html temas.json ./
RUN mkdir -p /app/dados \
    && printf '[]\n' > /app/dados/anotacoes.json \
    && chown -R node:node /app/dados \
    && chmod 700 /app/dados && chmod 600 /app/dados/anotacoes.json
USER node
EXPOSE 3000
CMD ["node", "app.js"]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 005 — Arquivos e construção

**Contexto do livro:**

> Deliberadamente não declaramos VOLUME no Dockerfile. A montagem será escolhida de forma explícita em cada criação; isso permite comparar a execução sem volume com as demais. Uma declaração VOLUME não selecionaria sozinha o nome de volume ou a pasta do host que desejamos reutilizar. [4]

> Acrescente estas exclusões ao .dockerignore, mantendo as regras anteriores, inclusive .env e .env.*:

```text
dados
dados-host
backup-cap06
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 006 — Arquivos e construção

**Contexto do livro:**

> Os dados reais e as cópias de recuperação não devem entrar no contexto de construção. O arquivo vazio da imagem é criado pelo RUN, não copiado de anotações do computador. .dockerignore não apaga arquivos do host e não substitui .gitignore. [5]

> Crie .env.cap06 com:

```text
APP_ENV=desenvolvimento
HOST=0.0.0.0
PORT=3000
DATA_DIR=/app/dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 007 — Arquivos e construção

**Contexto do livro:**

> Na pasta do projeto, construa e confira:

```text
docker build -t tnp-catalogo:1.4 .
docker image inspect --format "{{.Id}}" tnp-catalogo:1.4
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 008 — Primeiro experimento: o dado está no container

**Contexto do livro:**

> Crie uma instância sem montagem de dados:

```text
docker run --pull=never -d --name catalogo-efemero --env-file .env.cap06 -p 127.0.0.1:8091:3000 tnp-catalogo:1.4
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 009 — Primeiro experimento: o dado está no container

**Contexto do livro:**

> As linhas longas são comandos únicos, mesmo quando o Word as quebra visualmente. O arquivo de comandos do laboratório contém as mesmas linhas para cópia.

> Confira estado e saúde antes de gravar:

```text
docker ps --filter name=catalogo-efemero
docker exec catalogo-efemero node diagnostico.js
docker inspect --format "{{json .Mounts}}" catalogo-efemero
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 010 — Primeiro experimento: o dado está no container

**Contexto do livro:**

> Não deve existir uma montagem de dados para /app/dados. Abra http://127.0.0.1:8091/api/anotacoes: esperamos []. A página inicial deverá mostrar Edição 3 e os três temas.

> Agora produza uma informação de teste:

```text
docker exec catalogo-efemero node anotar.js "Anotacao apenas deste container."
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 011 — Primeiro experimento: o dado está no container

**Contexto do livro:**

> O processo adicional executa a ferramenta e termina. O servidor continua ativo. Atualize /api/anotacoes: o texto deverá aparecer. A rota lê o arquivo a cada requisição, portanto não exige reiniciar o servidor para enxergar essa gravação.

> Observe também:

```text
docker diff catalogo-efemero
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 012 — Reiniciar preservou. Isso já comprova o que precisamos?

**Contexto do livro:**

> Anote o ID e faça uma previsão antes da próxima sequência:

```text
docker inspect --format "{{.Id}}" catalogo-efemero
docker stop catalogo-efemero
docker start catalogo-efemero
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 013 — Reiniciar preservou. Isso já comprova o que precisamos?

**Contexto do livro:**

> Consulte o ID novamente e abra a rota de anotações. O mesmo objeto deverá conservar o texto. Esse resultado comprova a sobrevivência ao reinício, não à substituição do container. [11]

> Vamos testar a segunda situação. A anotação deste experimento é fictícia e será descartada intencionalmente. Não aplique a sequência a uma instância com dados importantes sem antes identificar e proteger seu armazenamento.

```text
docker stop catalogo-efemero
docker rm catalogo-efemero
docker run --pull=never -d --name catalogo-efemero --env-file .env.cap06 -p 127.0.0.1:8091:3000 tnp-catalogo:1.4
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 014 — Reiniciar preservou. Isso já comprova o que precisamos?

**Contexto do livro:**

> O novo ID deverá ser diferente. A rota deverá voltar a []. Não houve um apagamento misterioso dentro da imagem: removemos o objeto cuja camada gravável continha a anotação e criamos outro a partir da base vazia.

> Depois de verificar, encerre somente essa instância:

```text
docker stop catalogo-efemero
docker rm catalogo-efemero
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 015 — Um volume nomeado para os dados da aplicação

**Contexto do livro:**

> Antes de criar, consulte:

```text
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 016 — Um volume nomeado para os dados da aplicação

**Contexto do livro:**

> Na primeira execução, esperamos que esse nome ainda não exista. Essa ausência é diferente de uma falha geral de comunicação com o Engine. Se o volume já existir, investigue sua origem e seus dados; não presuma que esteja vazio.

> Crie o volume novo do laboratório:

```text
docker volume create --label tnp.capitulo=06 tnp-catalogo-dados
docker volume ls --filter name=tnp-catalogo-dados
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 017 — Um volume nomeado para os dados da aplicação

**Contexto do livro:**

> A inspeção mostra informações como nome, driver e localização gerenciada. O Mountpoint pertence ao ambiente do daemon. Use os mecanismos do Docker para operar o volume, em vez de editar à mão sua estrutura interna de armazenamento. [8]

> Crie a aplicação com a montagem:

```text
docker run --pull=never -d --name catalogo-volume --env-file .env.cap06 -p 127.0.0.1:8091:3000 --mount type=volume,src=tnp-catalogo-dados,dst=/app/dados tnp-catalogo:1.4
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 018 — Verifique a montagem, não apenas o container

**Contexto do livro:**

> Uma observação importante: a montagem de um volume com nome inexistente pode criá-lo automaticamente. Um erro de digitação em src pode, portanto, selecionar um armazenamento novo, vazio, em vez do volume que você pretendia reutilizar. Conferir o nome antes e depois da criação evita um diagnóstico errado de perda de dados. [7][10]

```text
docker inspect --format "{{json .Mounts}}" catalogo-volume
docker exec catalogo-volume id
docker exec catalogo-volume ls -ld /app/dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 019 — Verifique a montagem, não apenas o container

**Contexto do livro:**

> Por padrão, ao montar um volume vazio sobre um diretório com conteúdo, Docker copia o conteúdo inicial desse destino para o volume. Aqui existe somente a lista vazia preparada na imagem. Um volume já populado não é reinicializado a cada container. Essa preparação não é sincronização contínua com a imagem; volume-nocopy permite impedir a cópia inicial quando isso for desejado. [2]

> Grave e consulte:

```text
docker exec catalogo-volume node anotar.js "Esta anotacao pertence ao volume."
docker exec catalogo-volume node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 020 — A prova que faltava: outra instância, mesmo armazenamento

**Contexto do livro:**

> Anote o ID do container atual. A previsão é: o objeto será substituído, mas o nome do volume e a anotação serão preservados.

```text
docker inspect --format "{{.Id}}" catalogo-volume
docker stop catalogo-volume
docker rm catalogo-volume
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 021 — A prova que faltava: outra instância, mesmo armazenamento

**Contexto do livro:**

> O volume deverá continuar existindo. Crie outro container:

```text
docker run --pull=never -d --name catalogo-volume --env-file .env.cap06 -p 127.0.0.1:8091:3000 --mount type=volume,src=tnp-catalogo-dados,dst=/app/dados tnp-catalogo:1.4
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 022 — Falha controlada: volume certo, destino errado

**Contexto do livro:**

> Mantenha o servidor anterior. Vamos criar um segundo container, sem escrever no volume, para investigar uma aparente ausência de informações:

```text
docker run --pull=never -d --name catalogo-mount-errado --env-file .env.cap06 -p 127.0.0.1:8092:3000 --mount type=volume,src=tnp-catalogo-dados,dst=/app/outra-pasta tnp-catalogo:1.4
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 023 — Falha controlada: volume certo, destino errado

**Contexto do livro:**

> Abra http://127.0.0.1:8092/api/anotacoes. Esperamos uma lista vazia, enquanto a porta 8091 continua mostrando a anotação preservada.

> Antes de decidir que o volume perdeu dados, compare:

```text
docker inspect --format "{{json .Mounts}}" catalogo-mount-errado
docker exec catalogo-mount-errado node -p "process.env.DATA_DIR"
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 024 — Falha controlada: volume certo, destino errado

**Contexto do livro:**

> O volume foi montado em /app/outra-pasta, mas o programa usa /app/dados. Nesse segundo caminho, a instância encontrou o arquivo vazio vindo da imagem. O problema está na associação entre caminho e armazenamento, não no texto da anotação.

> Não copie os dados para um lugar aleatório nem reconstrua a imagem. O estado desejado exige uma montagem no caminho que o programa realmente utiliza. Como este container auxiliar não recebeu gravações, substitua somente ele:

```text
docker stop catalogo-mount-errado
docker rm catalogo-mount-errado
docker run --pull=never -d --name catalogo-mount-errado --env-file .env.cap06 -p 127.0.0.1:8092:3000 --mount type=volume,src=tnp-catalogo-dados,dst=/app/dados tnp-catalogo:1.4
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 025 — Falha controlada: volume certo, destino errado

**Contexto do livro:**

> A mesma rota agora deverá mostrar a anotação. O volume não precisou ser restaurado porque não havia perdido o arquivo. Depois da comparação, pare e remova o auxiliar:

```text
docker stop catalogo-mount-errado
docker rm catalogo-mount-errado
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 026 — Bind mount: quando a pasta pertence ao host

**Contexto do livro:**

> Agora a necessidade é outra: preparar um arquivo no editor do computador e fazer o container consultá-lo, sem reconstruir a imagem. Um bind mount expressa essa dependência de um caminho do host. [12]

> O pacote contém dados-host/anotacoes.json. Para montar o projeto manualmente, crie a pasta dados-host dentro de catalogo-estudos e salve nela, em UTF-8 sem BOM, o arquivo:

```text
["Anotacao criada no host."]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 027 — Bind mount: quando a pasta pertence ao host

**Contexto do livro:**

> Precisamos conferir a pasta, o arquivo de anotações e o caminho que será usado como origem. Na pasta do projeto, escolha somente a instrução correspondente ao seu terminal. Uma pasta vazia não substitui o arquivo que você preparou.

> PowerShell, no Windows:

```text
$pasta = Join-Path (Get-Location).Path 'dados-host'
$arquivo = Join-Path $pasta 'anotacoes.json'
if (-not (Test-Path -LiteralPath $pasta -PathType Container)) {
    throw 'Pasta de origem ausente. Nao prossiga com o mount.'
}
if (-not (Test-Path -LiteralPath $arquivo -PathType Leaf)) {
    throw 'Arquivo de anotacoes ausente. Nao prossiga.'
}
$origem = (Resolve-Path -LiteralPath $pasta).Path
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 028 — Bind mount: quando a pasta pertence ao host

**Contexto do livro:**

> Bash ou Zsh, no Linux/macOS:

> Confira previamente que dados-host é um diretório e que contém anotacoes.json. A atribuição abaixo apenas forma o caminho absoluto; não faz essa validação por você. Se a pasta ou o arquivo estiverem ausentes, interrompa a sequência antes do comando de montagem.

```text
origem="$(pwd)/dados-host"
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 029 — Bind mount: quando a pasta pertence ao host

**Contexto do livro:**

> Depois, a linha de criação é a mesma nos dois casos:

```text
docker run --pull=never -d --name catalogo-bind --env-file .env.cap06 -p 127.0.0.1:8093:3000 --mount "type=bind,src=$origem,dst=/app/dados,readonly" tnp-catalogo:1.4
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 030 — Observe a origem e mude o arquivo

**Contexto do livro:**

> readonly é intencional: o editor do host prepara os dados, e o container apenas lê. Um bind mount sem essa opção permite escrita pelo container, sujeita às permissões e aos controles do sistema. Isso pode alterar ou excluir arquivos reais do host. Monte apenas a pasta necessária, nunca diretórios pessoais ou de sistema por conveniência. [3]

```text
docker inspect --format "{{json .Mounts}}" catalogo-bind
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 031 — Observe a origem e mude o arquivo

**Contexto do livro:**

> Esperamos Type=bind, Destination=/app/dados e RW=false. Não esperamos um novo volume gerenciado listado por docker volume ls.

> Abra http://127.0.0.1:8093/api/anotacoes. A resposta deve conter a anotação criada no host. Agora edite o arquivo do host para:

```text
["Anotacao criada no host.", "Arquivo alterado sem novo build."]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 032 — A montagem de leitura realmente impede a escrita?

**Contexto do livro:**

> Faça uma previsão e execute apenas neste container de teste:

```text
docker exec catalogo-bind node anotar.js "Esta escrita deve ser recusada."
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 033 — A montagem de leitura realmente impede a escrita?

**Contexto do livro:**

> Atualize a API e examine o arquivo no editor: os dois textos do host devem permanecer, sem a tentativa adicional. O erro pertence à tarefa iniciada por exec; o servidor pode continuar ativo e respondendo às leituras.

> Depois pare e remova somente catalogo-bind. Confirme que dados-host/anotacoes.json permanece no computador:

```text
docker stop catalogo-bind
docker rm catalogo-bind
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 034 — Copie com as gravações interrompidas

**Contexto do livro:**

> O container catalogo-volume contém a anotação que será preservada. Não execute outra tarefa de escrita enquanto realiza esta etapa. Pare esse servidor e confirme o estado:

```text
docker stop catalogo-volume
docker inspect --format "{{.State.Status}}" catalogo-volume
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 035 — Copie com as gravações interrompidas

**Contexto do livro:**

> Crie uma pasta nova backup-cap06 no projeto. Se ela já contiver uma cópia anterior, preserve-a e escolha outro destino; não sobrescreva um backup útil para tornar a sequência mais curta.

```text
mkdir backup-cap06
docker cp catalogo-volume:/app/dados/anotacoes.json ./backup-cap06/anotacoes.json
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 036 — Restaure em um volume novo, não no original

**Contexto do livro:**

> Confirme primeiro que tnp-catalogo-restaurado e catalogo-restauracao estão livres. A ausência do volume é esperada nesta primeira execução:

```text
docker volume inspect tnp-catalogo-restaurado
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 037 — Restaure em um volume novo, não no original

**Contexto do livro:**

> Crie o destino de teste e uma instância que o inicialize:

```text
docker volume create --label tnp.capitulo=06 tnp-catalogo-restaurado
docker run --pull=never -d --name catalogo-restauracao --env-file .env.cap06 -p 127.0.0.1:8094:3000 --mount type=volume,src=tnp-catalogo-restaurado,dst=/app/dados tnp-catalogo:1.4
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 038 — Restaure em um volume novo, não no original

**Contexto do livro:**

> Confira /health e a lista vazia na porta 8094. Depois pare a instância e copie o arquivo para esse destino:

```text
docker stop catalogo-restauracao
docker cp ./backup-cap06/anotacoes.json catalogo-restauracao:/app/dados/anotacoes.json
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 039 — Restaure em um volume novo, não no original

**Contexto do livro:**

> A propriedade merece atenção: a cópia para um container pode produzir um arquivo pertencente a root. Nosso programa deve continuar usando node. Vamos normalizar somente o dono desse arquivo no volume novo, com uma tarefa curta:

```text
docker run --rm --pull=never --user 0:0 --mount type=volume,src=tnp-catalogo-restaurado,dst=/app/dados tnp-catalogo:1.4 chown node:node /app/dados/anotacoes.json
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 040 — Restaure em um volume novo, não no original

**Contexto do livro:**

> Essa é uma ação administrativa delimitada: usa nossa imagem, não monta pastas do host, não usa --privileged e não inicia o servidor como root. Não aplique a operação a volumes desconhecidos. Ajustar o dono do arquivo copiado evita ampliar permissões indiscriminadamente. [14]

> Inicie a instância novamente:

```text
docker start catalogo-restauracao
docker exec catalogo-restauracao node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 041 — Restaure em um volume novo, não no original

**Contexto do livro:**

> Consulte http://127.0.0.1:8094/api/anotacoes. Compare o conteúdo com a cópia no host. O volume original continua preservado, e o destino recuperado consegue apresentar a anotação pela aplicação.

> Somente depois dessa verificação, descarte os recursos da restauração de teste:

```text
docker stop catalogo-restauracao
docker rm catalogo-restauracao
docker volume rm tnp-catalogo-restaurado
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 042 — Remoção exige identificar o dono dos dados

**Contexto do livro:**

> A ação importante aqui não é decorar mais um rm. É distinguir seu alvo. docker rm opera sobre containers; docker volume rm opera sobre o armazenamento gerenciado indicado. Remover esse armazenamento pode eliminar as informações que sobreviviam às instâncias. [15]

> Para investigar quais containers referenciam um volume, inclusive parados, consulte:

```text
docker ps -a --filter volume=tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 043 — Prepare a continuidade com dados preservados

**Contexto do livro:**

> Vamos tornar 1.4 a versão do endereço principal. O antigo catalogo-web do capítulo 5 deve estar parado, associado a 1.3 e sem gravações de usuário. Confira com docker inspect catalogo-web. Se estiver ativo, pare-o; se não existir, omita a remoção. Não substitua um serviço desconhecido com o mesmo nome.

> Depois dessa confirmação:

```text
docker rm catalogo-web
docker run --pull=never -d --name catalogo-web --env-file .env.cap06 -p 127.0.0.1:8084:3000 --mount type=volume,src=tnp-catalogo-dados,dst=/app/dados tnp-catalogo:1.4
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 044 — Prepare a continuidade com dados preservados

**Contexto do livro:**

> Na porta 8084, confira página em Edição 3, os três temas, /health, /api/config e /api/anotacoes. Confirme também a origem dos dados:

```text
docker inspect --format "{{json .Mounts}}" catalogo-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 045 — Prepare a continuidade com dados preservados

**Contexto do livro:**

> O auxiliar catalogo-volume está parado desde a cópia de recuperação. Remova somente esse objeto, depois deixe o principal parado para a próxima sessão:

```text
docker rm catalogo-volume
docker stop catalogo-web
docker ps -a --filter name=catalogo
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 046 — armazenamento.js — um arquivo pequeno, com limites explícitos

**Contexto do livro:**

> Não há gravação automática na inicialização, nem recuperação silenciosa de JSON inválido. A escrita usa um temporário no mesmo diretório e pressupõe um único gravador por vez. As chamadas síncronas mantêm o laboratório curto; não são uma recomendação de arquitetura para um servidor de alto volume de requisições.

```text
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { randomUUID } = require('node:crypto');

function diretorioDados() {
  const dir = process.env.DATA_DIR ?? path.join(__dirname, 'dados');
  if (!dir.trim() || !path.isAbsolute(dir)) {
    throw new Error('DATA_DIR deve ser um caminho absoluto nao vazio.');
  }
  if (!fs.statSync(dir).isDirectory()) {
    throw new Error('DATA_DIR deve apontar para um diretorio existente.');
  }
  return dir;
}

function lerAnotacoes() {
  const arquivo = path.join(diretorioDados(), 'anotacoes.json');
  let texto;
  try {
    if (fs.statSync(arquivo).size > 262144) {
      throw new Error('Arquivo excede o limite de 256 KiB do laboratorio.');
    }
    texto = fs.readFileSync(arquivo, 'utf8');
  } catch (erro) {
    if (erro.code === 'ENOENT') return [];
    throw erro;
  }
  const notas = JSON.parse(texto);
  const valida = (nota) => typeof nota === 'string' &&
    nota.trim().length > 0 && nota.length <= 240;
  if (!Array.isArray(notas) || notas.length > 100 || !notas.every(valida)) {
    throw new Error('Anotacoes devem ser ate 100 textos de 1 a 240 caracteres.');
  }
  return notas;
}

function adicionarAnotacao(texto) {
  const nota = typeof texto === 'string' ? texto.trim() : '';
  if (!nota || nota.length > 240) {
    throw new Error('Informe uma anotacao de 1 a 240 caracteres.');
  }
  const notas = lerAnotacoes();
  if (notas.length >= 100) throw new Error('Limite de 100 anotacoes atingido.');
  notas.push(nota);
  const dir = diretorioDados();
  const destino = path.join(dir, 'anotacoes.json');
  const temporario = path.join(dir, `.anotacoes-${randomUUID()}.tmp`);
  let criado = false;
  try {
    fs.writeFileSync(temporario, JSON.stringify(notas, null, 2) + '\n', {
      encoding: 'utf8', flag: 'wx', mode: 0o600
    });
    criado = true;
    fs.renameSync(temporario, destino);
  } finally {
    if (criado && fs.existsSync(temporario)) fs.unlinkSync(temporario);
  }
  return notas;
}

module.exports = { diretorioDados, lerAnotacoes, adicionarAnotacao };
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 047 — anotar.js — escrita controlada e consulta

**Contexto do livro:**

> A ferramenta aceita exatamente uma anotação ou a opção --listar. As falhas retornam código diferente de zero, permitindo distinguir “o processo executou” de “o dado foi gravado”.

```text
'use strict';
const { lerAnotacoes, adicionarAnotacao } = require('./armazenamento');
try {
  const argumentos = process.argv.slice(2);
  if (argumentos.length !== 1) {
    throw new Error('Uso: node anotar.js "texto" ou node anotar.js --listar');
  }
  const notas = argumentos[0] === '--listar'
    ? lerAnotacoes()
    : adicionarAnotacao(argumentos[0]);
  console.log(JSON.stringify(notas));
} catch (erro) {
  console.error(`Falha nas anotacoes: ${erro.code ?? 'DADOS'}: ${erro.message}`);
  process.exitCode = 1;
}
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 048 — app.js — rotas anteriores e leitura das anotações

**Contexto do livro:**

> /api/config continua expondo somente ambiente e porta. A validação de armazenamento ocorre na inicialização; depois, uma falha de leitura em /api/anotacoes produz HTTP 500 sem apagar o arquivo. /health continua sendo uma resposta simples de disponibilidade, não um teste completo de persistência.

```text
'use strict';
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { diretorioDados, lerAnotacoes } = require('./armazenamento');

function lerConfiguracao() {
  const textoPorta = process.env.PORT ?? '3000';
  const porta = Number(textoPorta);
  const host = process.env.HOST ?? '0.0.0.0';
  const ambiente = process.env.APP_ENV ?? 'desenvolvimento';
  if (!/^\d+$/.test(textoPorta) || !Number.isInteger(porta) ||
      porta < 1024 || porta > 65535) {
    throw new Error('PORT deve ser um inteiro entre 1024 e 65535.');
  }
  if (!['0.0.0.0', '127.0.0.1'].includes(host)) {
    throw new Error('HOST deve ser 0.0.0.0 ou 127.0.0.1 neste laboratorio.');
  }
  if (!['desenvolvimento', 'homologacao', 'producao'].includes(ambiente)) {
    throw new Error('APP_ENV deve ser desenvolvimento, homologacao ou producao.');
  }
  return { porta, host, ambiente };
}

function iniciar() {
  let config;
  try {
    config = lerConfiguracao();
    config.diretorio = diretorioDados();
    lerAnotacoes();
  } catch (erro) {
    console.error(`Inicializacao invalida: ${erro.message}`);
    process.exitCode = 1;
    return;
  }
  const arquivos = new Map([
    ['/', ['index.html', 'text/html; charset=utf-8']],
    ['/api/temas', ['temas.json', 'application/json; charset=utf-8']]
  ]);
  const servidor = http.createServer((req, res) => {
    res.setHeader('Cache-Control', 'no-store');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    let caminho;
    try {
      caminho = new URL(req.url, 'http://localhost').pathname;
    } catch {
      res.writeHead(400);
      return res.end('Requisicao invalida.');
    }
    console.log(JSON.stringify({ metodo: req.method, caminho }));
    if (req.method !== 'GET') {
      res.writeHead(405, { Allow: 'GET' });
      return res.end('Metodo nao permitido.');
    }
    if (caminho === '/health' || caminho === '/api/config') {
      const resposta = caminho === '/health'
        ? { status: 'ok' }
        : { ambiente: config.ambiente, porta: config.porta };
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      return res.end(JSON.stringify(resposta));
    }
    if (caminho === '/api/anotacoes') {
      try {
        const notas = lerAnotacoes();
        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        return res.end(JSON.stringify(notas));
      } catch (erro) {
        console.error(`Falha nos dados: ${erro.code ?? 'DADOS'}: ${erro.message}`);
        res.writeHead(500);
        return res.end('Falha ao ler anotacoes. Consulte os logs.');
      }
    }
    const arquivo = arquivos.get(caminho);
    if (!arquivo) {
      res.writeHead(404);
      return res.end('Rota nao encontrada.');
    }
    fs.readFile(path.join(__dirname, arquivo[0]), (erro, dados) => {
      if (erro) {
        console.error(erro.message);
        res.writeHead(500);
        return res.end('Falha ao ler arquivo da aplicacao.');
      }
      res.writeHead(200, { 'Content-Type': arquivo[1] });
      res.end(dados);
    });
  });
  servidor.on('error', (erro) => {
    console.error(`Falha ao iniciar: ${erro.code ?? 'ERRO'}: ${erro.message}`);
    process.exitCode = 1;
  });
  servidor.listen(config.porta, config.host, () => {
    console.log(JSON.stringify({ evento: 'inicio', pid: process.pid, ...config }));
  });
  let encerrando = false;
  for (const sinal of ['SIGTERM', 'SIGINT']) {
    process.on(sinal, () => {
      if (encerrando) return;
      encerrando = true;
      console.log(`Encerrando: ${sinal}`);
      const limite = setTimeout(() => process.exit(1), 5000);
      limite.unref();
      servidor.close(() => {
        clearTimeout(limite);
        process.exitCode = 0;
      });
    });
  }
}

iniciar();
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*
