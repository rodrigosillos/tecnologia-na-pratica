# Capítulo 4 — trechos e comandos para consulta

> NÃO EXECUTE ESTE ARQUIVO INTEIRO. Ele contém comandos, trechos parciais, modelos, saídas e falhas deliberadas. Use somente a etapa indicada no livro, com suas pré-condições e verificações.

Fonte: manuscrito consolidado R02. O texto de cada bloco foi preservado, inclusive quebras reais. A numeração abaixo localiza os blocos neste arquivo; não é uma sequência automática de execução.

Marcadores como `ID_OBTIDO` não são valores reais. Comandos de remoção, alterações e falhas controladas exigem a identificação prévia dos recursos. Os parágrafos de contexto são lembretes; não substituem a seção completa do livro.

## Trecho 001 — Prepare os arquivos sem instalar Node.js no host

**Contexto do livro:**

> Crie uma pasta nova chamada catalogo-estudos. Não reutilize uma pasta importante de outro projeto. A estrutura mínima será:

```text
catalogo-estudos/
  app.js
  index.html
  temas.json
  Dockerfile
  .dockerignore
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 002 — Prepare os arquivos sem instalar Node.js no host

**Contexto do livro:**

> O runtime virá da imagem base. Portanto, executar os exercícios Docker não exige instalar Node.js, npm ou um editor específico no computador. Abra um terminal na pasta catalogo-estudos e use o mesmo Engine local com containers Linux dos capítulos anteriores.

> Antes de construir, consulte:

```text
docker version
docker ps -a --filter name=catalogo
docker image ls tnp-catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 003 — Dockerfile: a construção precisa ficar explícita

**Contexto do livro:**

> Até aqui, obtivemos imagens prontas com pull. Um Dockerfile permite descrever como produzir uma imagem a partir de uma base e dos arquivos do projeto. Ele é um arquivo de instruções para o builder, o componente que realiza a construção. Não é um script que deve ser colado inteiro no terminal. [1][2]

> Crie o arquivo Dockerfile, sem extensão, com este conteúdo:

```text
FROM node:24-bookworm-slim
WORKDIR /app
COPY app.js ./
RUN node --check app.js
COPY index.html temas.json ./
USER node
EXPOSE 3000
CMD ["node", "app.js"]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 004 — EXPOSE e CMD: descrição e inicialização

**Contexto do livro:**

> CMD ["node", "app.js"] registra o comando padrão de inicialização. A forma de lista usa a sintaxe JSON, com aspas duplas normais. Não substitua essas aspas por aspas tipográficas do editor. [1]

> A diferença essencial está no momento da ação:

```text
RUN node --check app.js
  construção: verifica e termina

CMD ["node", "app.js"]
  execução: define o servidor a iniciar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 005 — O ponto final do comando tem significado

**Contexto do livro:**

> Nesta construção local, os caminhos de origem dos COPY são relativos a esse contexto. O argumento -f, quando utilizado, escolhe outro Dockerfile; ele não muda, por si só, a raiz do contexto. Para este primeiro laboratório, evite essa variação: mantenha o Dockerfile junto dos três arquivos e abra o terminal nessa pasta.

> O encadeamento que queremos é simples:

```text
pasta catalogo-estudos
  -> contexto, filtrado por .dockerignore
  -> arquivos selecionados pelos COPY
  -> sistema de arquivos da imagem
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 006 — .dockerignore: nem tudo do projeto pertence ao build

**Contexto do livro:**

> Crie .dockerignore, no mesmo diretório do Dockerfile, com:

```text
.git
node_modules
.env
.env.*
*.log
coverage
tmp
README.md
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 007 — Construa a primeira versão, sem iniciar o servidor

**Contexto do livro:**

> Agora temos uma base escolhida, três arquivos de aplicação e instruções de construção. O estado desejado é uma imagem local chamada tnp-catalogo:1.0, ainda sem um container de aplicação em execução.

> Na pasta catalogo-estudos, execute:

```text
docker build --pull -t tnp-catalogo:1.0 .
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 008 — Construa a primeira versão, sem iniciar o servidor

**Contexto do livro:**

> Também não presuma que todo build obrigatoriamente carrega seu resultado no armazenamento usado pelo docker run. Este laboratório utiliza o builder padrão associado ao Engine local, que faz esse carregamento. Builders personalizados podem exigir uma saída explícita, como --load em um build de plataforma única com Buildx. Se o comando concluir e a imagem não aparecer, investigue o builder e sua saída antes de repetir comandos ao acaso. [11]

> Confira:

```text
docker image ls tnp-catalogo
docker ps -a --filter name=catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 009 — Verifique o artefato antes de confiar nele

**Contexto do livro:**

> Inspecione a imagem que você acabou de construir:

```text
docker image inspect --format "{{.Config.WorkingDir}}" tnp-catalogo:1.0
docker image inspect --format "{{.Config.User}}" tnp-catalogo:1.0
docker image inspect --format "{{json .Config.Cmd}}" tnp-catalogo:1.0
docker image inspect --format "{{json .Config.Entrypoint}}" tnp-catalogo:1.0
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 010 — Verifique o artefato antes de confiar nele

**Contexto do livro:**

> As primeiras consultas deverão mostrar /app, node e o comando com node e app.js. A última revela a configuração de entrada herdada. Estamos examinando propriedades do artefato, não logs de uma aplicação em execução. [12]

> Para observar a sequência registrada na construção:

```text
docker image history tnp-catalogo:1.0
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 011 — Verifique o artefato antes de confiar nele

**Contexto do livro:**

> Retome a distinção do capítulo 3: uma linha do histórico pode representar configuração, e não uma nova camada com arquivos. Aqui o histórico é uma pista complementar; o Dockerfile e os arquivos do projeto continuam sendo a descrição que devemos preservar.

> Podemos ainda fazer uma verificação curta do runtime, substituindo o comando padrão apenas para essa execução:

```text
docker run --rm --pull=never tnp-catalogo:1.0 node --version
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 012 — Inicie o catálogo e verifique três respostas

**Contexto do livro:**

> Queremos agora um container chamado catalogo-web, utilizando a imagem local, acessível na porta 8084 apenas pelo próprio host. Execute a linha inteira:

```text
docker run --pull=never -d --name catalogo-web -p 127.0.0.1:8084:3000 tnp-catalogo:1.0
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 013 — Inicie o catálogo e verifique três respostas

**Contexto do livro:**

> Na aplicação fornecida, o servidor escuta em 0.0.0.0:3000 dentro do ambiente do container. A publicação usa 127.0.0.1:8084 no host. São decisões em lugares diferentes: a primeira permite receber a conexão encaminhada ao container; a segunda restringe o ponto de entrada local do laboratório.

> Confira existência, estado e porta:

```text
docker ps --filter name=catalogo-web
docker port catalogo-web
docker logs --tail 10 catalogo-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 014 — Inicie o catálogo e verifique três respostas

**Contexto do livro:**

> Abra http://127.0.0.1:8084. A página deverá apresentar Catálogo de Estudos, Edição 1 e os três temas. Em seguida, abra http://127.0.0.1:8084/api/temas: deverá aparecer o JSON entregue em temas.json.

> Por fim, acesse http://127.0.0.1:8084/health. Nossa implementação retorna:

```text
{"status":"ok"}
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 015 — Cache: o que precisa ser executado novamente?

**Contexto do livro:**

> Sem alterar os arquivos, execute:

```text
docker build --progress=plain -t tnp-catalogo:1.0 .
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 016 — Uma alteração no computador não altera o container

**Contexto do livro:**

> O catálogo está funcionando, mas queremos identificar visualmente uma nova entrega. Abra index.html na pasta do host e altere apenas:

```text
<p id="edicao">Edição 1</p>
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 017 — Uma alteração no computador não altera o container

**Contexto do livro:**

> para:

```text
<p id="edicao">Edição 2</p>
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 018 — Uma alteração no computador não altera o container

**Contexto do livro:**

> O resultado esperado ainda é Edição 1. Não criamos uma montagem da pasta do host. A cópia que entrou na imagem anterior não é um vínculo permanente com o arquivo que você está editando agora.

> O estado está separado:

```text
arquivo no host        -> Edição 2
imagem 1.0             -> conteúdo do build anterior
container catalogo-web -> continua usando a imagem de criação
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 019 — Reconstruir ainda não é substituir o servidor

**Contexto do livro:**

> Produza a nova imagem com outro nome de versão:

```text
docker build --progress=plain -t tnp-catalogo:1.1 .
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 020 — Reconstruir ainda não é substituir o servidor

**Contexto do livro:**

> Mantivemos 1.0 para comparação. Essas tags locais representam etapas do exercício; não são promessas de imutabilidade impostas pelo Docker.

> Confira os dois artefatos:

```text
docker image ls tnp-catalogo
docker image inspect --format "{{.Id}}" tnp-catalogo:1.0
docker image inspect --format "{{.Id}}" tnp-catalogo:1.1
docker inspect --format "{{.Image}}" catalogo-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 021 — Compare antes de substituir

**Contexto do livro:**

> Crie um candidato com outro nome e outra porta:

```text
docker run --pull=never -d --name catalogo-candidato -p 127.0.0.1:8085:3000 tnp-catalogo:1.1
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 022 — Compare antes de substituir

**Contexto do livro:**

> Verifique:

```text
docker ps --filter name=catalogo
docker logs --tail 10 catalogo-candidato
docker inspect --format "{{.Image}}" catalogo-candidato
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 023 — Substitua somente o objeto descartável do laboratório

**Contexto do livro:**

> Depois de verificar o candidato, queremos Edição 2 no endereço principal, a porta 8084. Nosso catálogo ainda não grava dados de usuários, não usa volumes e é inteiramente reproduzível com os três arquivos fornecidos. Podemos substituir esse container específico.

> Pare o objeto antigo, confira seu estado e remova-o:

```text
docker stop catalogo-web
docker ps -a --filter name=catalogo-web
docker rm catalogo-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 024 — Substitua somente o objeto descartável do laboratório

**Contexto do livro:**

> Crie o novo container usando a imagem 1.1:

```text
docker run --pull=never -d --name catalogo-web -p 127.0.0.1:8084:3000 tnp-catalogo:1.1
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 025 — Substitua somente o objeto descartável do laboratório

**Contexto do livro:**

> Confirme estado, imagem e acesso:

```text
docker ps --filter name=catalogo-web
docker inspect --format "{{.Image}}" catalogo-web
docker image inspect --format "{{.Id}}" tnp-catalogo:1.1
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 026 — Substitua somente o objeto descartável do laboratório

**Contexto do livro:**

> A página na porta 8084 deverá apresentar Edição 2 e continuar carregando os três temas. O nome foi reaproveitado, mas o ID do container é novo. Não confunda igualdade de nome com continuidade do objeto.

> O candidato já cumpriu sua função. Remova somente ele:

```text
docker stop catalogo-candidato
docker rm catalogo-candidato
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 027 — Falha controlada: o arquivo existe, mas o COPY não o encontra

**Contexto do livro:**

> Vamos investigar um erro sem danificar os arquivos da aplicação nem interromper o servidor que funciona. Abra .dockerignore e acrescente temporariamente esta linha ao final:

```text
index.html
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 028 — Falha controlada: o arquivo existe, mas o COPY não o encontra

**Contexto do livro:**

> O arquivo continua visível na pasta. Antes de construir, formule uma hipótese: o que o builder encontrará quando chegar ao COPY que exige esse arquivo?

> Use uma tag nova, reservada para a tentativa:

```text
docker build -t tnp-catalogo:falha .
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 029 — Falha controlada: o arquivo existe, mas o COPY não o encontra

**Contexto do livro:**

> O raciocínio é: a origem solicitada pelo COPY existe no host, mas foi excluída das entradas disponibilizadas ao builder. A indicação de cache na mensagem não transforma o cache na causa do problema. [7][16]

> Não apague imagens nem containers para corrigir isso. Remova somente a linha index.html que você acabou de acrescentar ao .dockerignore. Preserve as demais exclusões. Confirme que index.html continua salvo e execute:

```text
docker build -t tnp-catalogo:validacao .
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 030 — Falha controlada: o arquivo existe, mas o COPY não o encontra

**Contexto do livro:**

> O build deverá concluir. Verifique a referência e depois remova apenas essa imagem ou tag temporária, que não foi usada para iniciar a aplicação:

```text
docker image inspect tnp-catalogo:validacao
docker image rm tnp-catalogo:validacao
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 031 — Deixe um estado conhecido para o próximo capítulo

**Contexto do livro:**

> Preserve os arquivos do projeto, com index.html em Edição 2, temas.json com os três temas originais e .dockerignore sem a exclusão temporária de index.html. Preserve também as imagens tnp-catalogo:1.0 e tnp-catalogo:1.1.

> Vamos deixar catalogo-web, criado a partir de 1.1, parado para não ocupar recursos enquanto você não estuda. Depois das verificações pelo navegador, execute:

```text
docker stop catalogo-web
docker ps -a --filter name=catalogo
docker image ls tnp-catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 032 — app.js — servidor e rotas

**Contexto do livro:**

> Este servidor lê somente arquivos associados às rotas conhecidas. Ele não publica livremente a pasta inteira. Também registra requisições, informa falhas de leitura e trata os sinais usados para solicitar encerramento. O módulo HTTP e a operação de fechamento do servidor pertencem à API do Node.js. [17]

```text
'use strict';
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

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
  if (caminho === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ status: 'ok' }));
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
  console.error(erro.message);
  process.exitCode = 1;
});
servidor.listen(3000, '0.0.0.0', () => {
  console.log('Catalogo de Estudos: porta 3000.');
});
for (const sinal of ['SIGTERM', 'SIGINT']) {
  process.on(sinal, () => {
    console.log(`Encerrando: ${sinal}`);
    const limite = setTimeout(() => process.exit(1), 5000);
    limite.unref();
    servidor.close(() => {
      clearTimeout(limite);
      process.exit(0);
    });
  });
}
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 033 — index.html — página inicial

**Contexto do livro:**

> A página busca a lista na API e usa conteúdo textual para apresentar os nomes. A marca Edição 1 é o ponto de partida do experimento de reconstrução. O arquivo de referência de Edição 2, no laboratório, altera somente essa marca.

```text
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Catálogo de Estudos</title>
  <style>
    body { font: 18px/1.6 system-ui; background: #f4f7fb;
      color: #102744; margin: 0; padding: 32px 20px; }
    main { max-width: 720px; margin: auto; padding: 24px;
      background: white; border-radius: 12px; }
    h1 { line-height: 1.2; }
    .serie { color: #a44110; font-weight: bold; }
    li { margin: 8px 0; }
    a { color: #174e87; }
  </style>
</head>
<body>
  <main>
    <p class="serie">Tecnologia na Prática</p>
    <h1>Catálogo de Estudos</h1>
    <p id="edicao">Edição 1</p>
    <p>Temas para organizar sua trilha de aprendizado.</p>
    <ul id="temas"><li>Carregando temas...</li></ul>
    <p><a href="/api/temas">Ver dados da API</a></p>
    <p><a href="/health">Ver resposta de saúde</a></p>
  </main>
  <script>
    async function carregar() {
      const lista = document.getElementById('temas');
      try {
        const resposta = await fetch('/api/temas');
        if (!resposta.ok) throw new Error('API indisponível.');
        const temas = await resposta.json();
        lista.replaceChildren();
        for (const tema of temas) {
          const item = document.createElement('li');
          item.textContent = tema.nome;
          lista.appendChild(item);
        }
      } catch {
        lista.textContent = 'Não foi possível carregar os temas.';
      }
    }
    carregar();
  </script>
</body>
</html>
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 034 — temas.json — dados iniciais

```text
[
  { "id": 1, "nome": "Git e GitHub" },
  { "id": 2, "nome": "SQL" },
  { "id": 3, "nome": "Docker" }
]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*
