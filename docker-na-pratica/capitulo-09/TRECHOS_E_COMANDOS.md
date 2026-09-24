# Capítulo 9 — trechos e comandos para consulta

> NÃO EXECUTE ESTE ARQUIVO INTEIRO. Ele contém comandos, trechos parciais, modelos, saídas e falhas deliberadas. Use somente a etapa indicada no livro, com suas pré-condições e verificações.

Fonte: manuscrito consolidado R02. O texto de cada bloco foi preservado, inclusive quebras reais. A numeração abaixo localiza os blocos neste arquivo; não é uma sequência automática de execução.

Marcadores como `ID_OBTIDO` não são valores reais. Comandos de remoção, alterações e falhas controladas exigem a identificação prévia dos recursos. Os parágrafos de contexto são lembretes; não substituem a seção completa do livro.

## Trecho 001 — Retome a configuração antes de restringi-la

**Contexto do livro:**

> O estado de saída do capítulo 8 contém os serviços catalogo e entrada parados, no projeto tnp-catalogo. O catálogo usa a imagem 1.4; o proxy usa 1.0. A rede gerenciada chama-se tnp-catalogo_rede, e o volume externo contém as anotações do leitor. A entrada publica 127.0.0.1:8084:8080; o catálogo não publica porta no host.

> Extraia o novo pacote em uma pasta separada e execute os comandos em laboratorio. Não sobrescreva backups, dados de bind mount nem arquivos pessoais. O pacote não contém suas anotações reais. Ele preserva os fontes e inclui compose.cap08.yaml, uma cópia da definição anterior para observar e iniciar as instâncias existentes.

```text
docker version
docker compose version
docker compose -f compose.cap08.yaml config --quiet
docker compose -f compose.cap08.yaml ps -a
docker volume inspect tnp-catalogo-dados
docker image inspect tnp-catalogo:1.4 tnp-entrada:1.0
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 002 — Primeiro reduza o que entra, não apenas o tamanho que sai

**Contexto do livro:**

> Continuaremos com node:24-bookworm-slim. Não mudaremos para Alpine nem para uma imagem sem shell apenas para parecer mais avançado. Nosso projeto não utiliza pacotes npm externos: acrescentar um package.json fictício ou instalar um compilador não resolveria uma necessidade real.

> O contexto também merece controle. Em vez de aumentar indefinidamente uma lista de exclusões, adotaremos uma lista explícita dos arquivos admitidos. Substitua catalogo-estudos/.dockerignore por:

```text
*
!Dockerfile
!.dockerignore
!app.js
!diagnostico.js
!armazenamento.js
!anotar.js
!index.html
!temas.json
!validar-build.cjs
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 003 — Verificar e distribuir em estágios

**Contexto do livro:**

> Essa checagem não executa um navegador, não valida toda a semântica do JavaScript e não examina anotações do usuário. A análise de sintaxe continua explícita em node --check. O relatório serve como evidência de uma verificação limitada, não como selo de aplicação sem defeitos.

> O Dockerfile completo do catálogo passa a ser:

```text
FROM node:24-bookworm-slim AS base
WORKDIR /app

FROM base AS verificacao
COPY app.js diagnostico.js armazenamento.js anotar.js ./
RUN node --check app.js && node --check diagnostico.js \
    && node --check armazenamento.js && node --check anotar.js
COPY index.html temas.json validar-build.cjs ./
RUN node validar-build.cjs

FROM base AS execucao
RUN mkdir -p /app/dados \
    && printf '[]\n' > /app/dados/anotacoes.json \
    && chown -R node:node /app/dados \
    && chmod 700 /app/dados && chmod 600 /app/dados/anotacoes.json
COPY --from=verificacao /app/app.js /app/diagnostico.js ./
COPY --from=verificacao /app/armazenamento.js /app/anotar.js ./
COPY --from=verificacao /app/index.html /app/temas.json ./
USER node
EXPOSE 3000
CMD ["node", "app.js"]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 004 — Construa sem substituir o que já funciona

**Contexto do livro:**

> Antes do primeiro build, confira se tnp-catalogo:1.5 não identifica outro trabalho. Nesta etapa, os serviços anteriores continuam parados e preservados. Execute:

```text
docker build --progress=plain -t tnp-catalogo:1.5 ./catalogo-estudos
docker image inspect --format "{{.Id}}" tnp-catalogo:1.5
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 005 — Construa sem substituir o que já funciona

**Contexto do livro:**

> O estágio final é o último do arquivo. Se uma análise falhar, a construção não deve ser considerada aprovada. Corrija o arquivo indicado pela mensagem; não retire a verificação só para obter uma tag. Se uma tag já existia antes de uma tentativa que falhou, sua permanência não comprova que a tentativa nova funcionou.

> Agora consulte os artefatos pela imagem recém-criada, sem rede de aplicação e sem montar dados:

```text
docker run --rm --pull=never tnp-catalogo:1.5 node -e "const fs=require('node:fs'); console.log(fs.existsSync('/app/validar-build.cjs'),fs.existsSync('/app/verificacao.json'))"
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 006 — Construa sem substituir o que já funciona

**Contexto do livro:**

> O resultado esperado é false false. O programa do catálogo permanece na imagem, mas os dois arquivos exclusivos da verificação não. Esse comando substitui a tarefa padrão por uma consulta curta; não inicia outro servidor.

> Para examinar deliberadamente o estágio intermediário, use uma tag separada:

```text
docker build --target verificacao -t tnp-catalogo:verificacao-cap09 ./catalogo-estudos
docker run --rm --pull=never tnp-catalogo:verificacao-cap09 cat verificacao.json
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 007 — Cache: não confunda reaproveitamento com falta de atualização

**Contexto do livro:**

> Repita a construção final sem editar arquivos:

```text
docker build --progress=plain -t tnp-catalogo:1.5 ./catalogo-estudos
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 008 — Cache: não confunda reaproveitamento com falta de atualização

**Contexto do livro:**

> Há duas decisões diferentes em uma reconstrução: consultar a base novamente e reutilizar etapas do build. --pull solicita atualização da base; --no-cache desabilita o reaproveitamento das etapas. --no-cache, sozinho, não garante uma base atualizada. [1]

> Quando a intenção for avaliar uma atualização, use uma referência distinta da já aprovada:

```text
docker build --pull --no-cache -t tnp-catalogo:avaliacao-cap09 ./catalogo-estudos
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 009 — Declare somente as exceções de escrita necessárias

**Contexto do livro:**

> O modo 01777 representa a convenção de um diretório temporário compartilhável com sticky bit. Não estamos aplicando chmod 777 ao volume das anotações nem aos fontes. O número aparece somente na montagem temporária do Nginx, permitindo que seu usuário não-root crie os arquivos de trabalho.

> Substitua compose.yaml pelo modelo completo abaixo. O pacote contém a mesma versão. Mantemos o arquivo de ambiente catalogo-estudos/.env.cap08, porque os valores não mudaram.

```text
name: tnp-catalogo

services:
  catalogo:
    image: tnp-catalogo:1.5
    build:
      context: ./catalogo-estudos
      target: execucao
    pull_policy: never
    env_file:
      - ./catalogo-estudos/.env.cap08
    volumes:
      - type: volume
        source: dados
        target: /app/dados
    networks:
      - rede
    healthcheck:
      test: ["CMD", "node", "diagnostico.js"]
      interval: 5s
      timeout: 4s
      retries: 6
      start_period: 5s
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - "no-new-privileges:true"
    mem_limit: 256m
    cpus: 1.0
    pids_limit: 128
    logging:
      driver: local
      options:
        max-size: "10m"
        max-file: "3"
    stop_grace_period: 10s
    restart: "no"

  entrada:
    image: tnp-entrada:1.0
    build:
      context: ./entrada
    pull_policy: never
    ports:
      - "127.0.0.1:${TNP_PORTA_HTTP:?Defina TNP_PORTA_HTTP no .env}:8080"
    networks:
      - rede
    depends_on:
      catalogo:
        condition: service_healthy
    read_only: true
    volumes:
      - type: tmpfs
        target: /tmp
        tmpfs:
          size: 16777216
          mode: 01777
    cap_drop:
      - ALL
    security_opt:
      - "no-new-privileges:true"
    mem_limit: 128m
    cpus: 0.5
    pids_limit: 64
    logging:
      driver: local
      options:
        max-size: "10m"
        max-file: "3"
    stop_grace_period: 10s
    restart: "no"

networks:
  rede:
    driver: bridge

volumes:
  dados:
    external: true
    name: tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 010 — Proteja os dados antes de aplicar a definição nova

**Contexto do livro:**

> A nova imagem já deve existir. Ainda não execute up. Primeiro use a definição antiga para iniciar apenas o catálogo preservado e reconhecer as anotações:

```text
docker compose -f compose.cap08.yaml start --wait --wait-timeout 60 catalogo
docker compose -f compose.cap08.yaml exec -T catalogo node anotar.js --listar
docker compose -f compose.cap08.yaml stop
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 011 — Proteja os dados antes de aplicar a definição nova

**Contexto do livro:**

> Confirme o conteúdo e não permita outra tarefa de escrita durante esta etapa. Crie uma pasta nova para a cópia. Se backup-cap09 já existir, escolha outro destino e mantenha a cópia anterior.

```text
mkdir backup-cap09
docker compose -f compose.cap08.yaml cp catalogo:/app/dados/anotacoes.json ./backup-cap09/anotacoes.json
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 012 — Proteja os dados antes de aplicar a definição nova

**Contexto do livro:**

> A cópia utiliza o serviço e sua instância parada. Abra o arquivo no editor e confirme o JSON. Esse procedimento continua limitado ao nosso arquivo pequeno, com gravações interrompidas; não o generalize para copiar arquivos de um banco de dados em atividade. [18]

> Agora consulte o modelo novo:

```text
docker compose config --quiet
docker compose config
docker image inspect tnp-catalogo:1.5 tnp-entrada:1.0
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 013 — Proteja os dados antes de aplicar a definição nova

**Contexto do livro:**

> Confirme projeto, imagens, volume externo, montagem temporária e publicação. A configuração deve continuar apontando para tnp-catalogo-dados, não para outro nome semelhante. Uma validação de YAML não comprova que os controles serão suportados ou que a aplicação funcionará sob eles.

> Aplique e aguarde:

```text
docker compose up -d --no-build --wait --wait-timeout 60
docker compose ps -a
docker compose logs --tail 20 catalogo entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 014 — Verifique o controle e a função

**Contexto do livro:**

> Acesse http://127.0.0.1:8084/ e confira a Edição 3, os três temas e as rotas. Compare /api/anotacoes com a cópia anterior. A mudança na forma de construção não deveria alterar esse conteúdo.

> Confirme as identidades dos processos e faça uma consulta interna:

```text
docker compose exec -T catalogo id
docker compose exec -T entrada id
docker compose exec -T catalogo node diagnostico.js
docker compose port entrada 8080
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 015 — Verifique o controle e a função

**Contexto do livro:**

> Para consultar a configuração efetivamente recebida pelo Engine, obtenha o ID do catálogo:

```text
docker compose ps -q catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 016 — Verifique o controle e a função

**Contexto do livro:**

> Nas linhas seguintes, substitua ID_CATALOGO pelo valor dessa instância, sem executar o marcador literalmente:

```text
docker inspect --format "{{.HostConfig.ReadonlyRootfs}}" ID_CATALOGO
docker inspect --format "{{json .HostConfig.CapDrop}}" ID_CATALOGO
docker inspect --format "{{json .HostConfig.SecurityOpt}}" ID_CATALOGO
docker inspect --format "{{json .Mounts}}" ID_CATALOGO
docker inspect --format "{{json .HostConfig.LogConfig}}" ID_CATALOGO
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 017 — Verifique o controle e a função

**Contexto do livro:**

> Esperamos raiz somente leitura, capacidades removidas, a opção de privilégios e a montagem gravável do volume no caminho correto. A grafia normalizada de uma opção pode diferir da escrita no YAML. Compare o significado, não apenas a aparência.

> Faça agora uma previsão: o programa adicional deverá conseguir gravar um arquivo em /tmp do catálogo, onde não declaramos uma exceção de escrita?

```text
docker compose exec -T catalogo node -e "require('node:fs').writeFileSync('/tmp/tnp-cap09.txt','teste')"
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 018 — Verifique o controle e a função

**Contexto do livro:**

> Esperamos recusa, normalmente EROFS, e saída diferente de zero. Não tentamos alterar código nem apagar dados. Se a escrita funcionar, interrompa a conclusão e compare a instância, o campo de raiz somente leitura e as montagens; talvez a configuração não tenha sido aplicada. Não transforme a falha esperada em motivo para desligar a proteção. A verificação vale para esse caminho: o Engine possui outras montagens próprias, e uma raiz somente leitura não deve ser descrita como proibição absoluta de qualquer escrita em todo o ambiente. [12]

> Agora teste a operação que deve continuar permitida. Em uma sessão sem outros gravadores, acrescente uma anotação didática:

```text
docker compose exec -T catalogo node anotar.js "Controle de escrita verificado no Capitulo 9."
docker compose exec -T catalogo node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 019 — Falha controlada: o proxy precisava de um temporário

**Contexto do livro:**

> O catálogo funciona com a raiz somente leitura. Isso permite concluir que qualquer programa também funcionará assim, sem mais nenhuma configuração? Vamos testar a hipótese no proxy.

> Somente em entrada, remova temporariamente o bloco de montagem volumes que contém type: tmpfs. Não altere o bloco de dados do catálogo, o nome externo do volume ou read_only: true. Aplique apenas a entrada:

```text
docker compose config --quiet
docker compose up -d --no-build --no-deps --wait --wait-timeout 30 entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 020 — Falha controlada: o proxy precisava de um temporário

**Contexto do livro:**

> O Nginx deve falhar ao inicializar. O comando pode informar falha de espera ou terminar antes de a saída do processo ficar visível. Consulte o estado novamente antes de concluir. Antes de corrigir, observe:

```text
docker compose ps -a
docker compose logs --tail 30 entrada
docker compose exec -T catalogo node diagnostico.js
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 021 — Falha controlada: o proxy precisava de um temporário

**Contexto do livro:**

> O problema não é a imagem do catálogo, o DNS nem as anotações. Retiramos o armazenamento que atendia a uma necessidade do proxy. A correção de menor escopo é restaurar exatamente a montagem temporária da entrada, não executar tudo como root nem tornar toda a raiz gravável.

> Depois de restaurar o bloco:

```text
docker compose config --quiet
docker compose up -d --no-build --no-deps --wait --wait-timeout 60 entrada
docker compose exec -T entrada nginx -t
docker compose logs --tail 15 entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 022 — Experimento opcional, somente com um valor fictício

**Contexto do livro:**

> O pacote contém exemplos/segredo-ficticio.txt, com um texto sem credencial. O arquivo fica fora do contexto exemplos/segredo-build. O Dockerfile desse contexto é:

```text
# syntax=docker/dockerfile:1
FROM node:24-bookworm-slim
RUN --mount=type=secret,id=exemplo,required=true \
    test -s /run/secrets/exemplo
USER node
CMD ["node", "--version"]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 023 — Experimento opcional, somente com um valor fictício

**Contexto do livro:**

> O test -s apenas exige um arquivo não vazio; não autentica em nenhum serviço e não imprime seu conteúdo. A diretiva de sintaxe utiliza o frontend Dockerfile atual da linha 1 e pode requerer obtenção desse frontend. Não tente executar essa instrução em um construtor legado sem suporte ao recurso. [21][22]

> A partir de laboratorio, a construção opcional é:

```text
docker build --secret id=exemplo,src=./exemplos/segredo-ficticio.txt -t tnp-segredo:cap09 ./exemplos/segredo-build
docker run --rm --pull=never tnp-segredo:cap09 node -e "console.log(require('node:fs').existsSync('/run/secrets/exemplo'))"
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 024 — Atualizações e segurança exigem evidências

**Contexto do livro:**

> Uma imagem aprovada hoje pode precisar ser substituída depois. Para avaliar uma atualização, preserve o artefato anterior, construa uma referência candidata, execute as verificações e só então aplique a nova seleção. Não use uma edição manual dentro do container como processo normal de atualização.

> Uma ferramenta de análise de vulnerabilidades acrescenta outra fonte de informação. Com Docker Scout disponível e configurado, por exemplo, é possível examinar CVEs da imagem local:

```text
docker scout cves local://tnp-catalogo:1.5
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 025 — Pratique agora: prove a diferença entre código, temporário e dados

**Contexto do livro:**

> No catálogo, consulte a montagem e as anotações. Não provoque a remoção de um volume para provar que ele é importante. O exercício está concluído quando você explica por que um temporário desapareceu e os dados permaneceram, além de comprovar que o caminho completo pelo proxy voltou a responder.

> Observe também o consumo sem provocar saturação:

```text
docker compose stats --no-stream
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 026 — Prepare a continuidade com uma versão verificável

**Contexto do livro:**

> Restaure o compose.yaml completo deste capítulo: catálogo 1.5, entrada 1.0, montagem temporária da entrada, sonda correta e volume externo original. Nenhuma falha controlada deve permanecer escondida na configuração.

```text
docker compose config --quiet
docker compose ps -a
docker compose exec -T catalogo node anotar.js --listar
docker compose port entrada 8080
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 027 — Prepare a continuidade com uma versão verificável

**Contexto do livro:**

> Confira a página, os temas, as rotas e a anotação acrescentada deliberadamente. Depois deixe o conjunto parado:

```text
docker compose stop
docker compose ps -a
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 028 — Prepare a continuidade com uma versão verificável

**Contexto do livro:**

> Preserve as imagens anteriores, a nova 1.5, a configuração e as cópias de recuperação. O pacote inclui ESTADO_PARA_CAPITULO_10.json, com o estado esperado, não uma captura de um Engine que você ainda não executou.

> Para retirar uma tag intermediária criada exclusivamente neste exercício, confirme que ela não identifica outro trabalho e que nenhum container de diagnóstico permanece associado. Depois remova apenas essa referência:

```text
docker image rm tnp-catalogo:verificacao-cap09
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 029 — validar-build.cjs — uma verificação com escopo declarado

**Contexto do livro:**

> Este arquivo é fornecido pronto. Ele executa no estágio de verificação, não no servidor. As operações de leitura e escrita utilizam a API de arquivos do Node.js. O relatório anterior desse estágio é removido antes da nova verificação para não deixar uma evidência antiga diante de uma falha. Não há acesso ao volume nem leitura de segredos. [27]

```text
"use strict";
const fs = require("node:fs");
const { createHash } = require("node:crypto");
const arquivos = [
  "app.js", "diagnostico.js", "armazenamento.js", "anotar.js",
  "index.html", "temas.json"
];
try {
  fs.rmSync("verificacao.json", { force: true });
  const temas = JSON.parse(fs.readFileSync("temas.json", "utf8"));
  if (!Array.isArray(temas) || temas.length === 0 ||
      temas.some(t => !t || !Number.isSafeInteger(t.id) || t.id < 1 ||
        typeof t.nome !== "string" || !t.nome.trim()) ||
      new Set(temas.map(t => t.id)).size !== temas.length) {
    throw new Error("Temas devem ter IDs positivos unicos e nomes nao vazios.");
  }
  const pagina = fs.readFileSync("index.html", "utf8");
  if (!pagina.includes("/api/temas") || !pagina.includes("/api/anotacoes")) {
    throw new Error("A pagina deve preservar os caminhos das APIs do catalogo.");
  }
  const sha256 = {};
  for (const arquivo of arquivos) {
    sha256[arquivo] = createHash("sha256")
      .update(fs.readFileSync(arquivo)).digest("hex");
  }
  fs.writeFileSync("verificacao.json", JSON.stringify({
    escopo: "Estrutura de temas, caminhos no HTML e hashes dos arquivos.",
    quantidadeTemas: temas.length, sha256
  }, null, 2) + "\n");
  console.log("Verificacao de build concluida.");
} catch (erro) {
  console.error(`Falha na verificacao de build: ${erro.message}`);
  process.exitCode = 1;
}
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*
