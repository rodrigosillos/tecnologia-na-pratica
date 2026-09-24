# Capítulo 5 — trechos e comandos para consulta

> NÃO EXECUTE ESTE ARQUIVO INTEIRO. Ele contém comandos, trechos parciais, modelos, saídas e falhas deliberadas. Use somente a etapa indicada no livro, com suas pré-condições e verificações.

Fonte: manuscrito consolidado R02. O texto de cada bloco foi preservado, inclusive quebras reais. A numeração abaixo localiza os blocos neste arquivo; não é uma sequência automática de execução.

Marcadores como `ID_OBTIDO` não são valores reais. Comandos de remoção, alterações e falhas controladas exigem a identificação prévia dos recursos. Os parágrafos de contexto são lembretes; não substituem a seção completa do livro.

## Trecho 001 — Retome o projeto sem perder o ponto de partida

**Contexto do livro:**

> O estado de continuidade do capítulo 4 é: catalogo-web, criado de tnp-catalogo:1.1, parado; a página em Edição 2; os três temas originais em temas.json; e as imagens 1.0 e 1.1 preservadas. O exercício temporário de quatro temas já foi encerrado. Não trataremos a tag 1.2 daquele exercício como base desta etapa.

> No mesmo terminal e contexto Docker, consulte:

```text
docker version
docker ps -a --filter name=catalogo
docker image ls tnp-catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 002 — Prepare a versão 1.3

**Contexto do livro:**

> Na pasta catalogo-estudos, substitua app.js pela versão completa ao final deste capítulo e acrescente diagnostico.js. Preserve index.html e temas.json. O ZIP contém a pasta completa nesta etapa, inclusive os arquivos ocultos; extraí-lo não modifica imagens ou containers já existentes.

> Ajuste somente as duas instruções de cópia e verificação do servidor. O Dockerfile completo fica:

```text
FROM node:24-bookworm-slim
WORKDIR /app
COPY app.js diagnostico.js ./
RUN node --check app.js && node --check diagnostico.js
COPY index.html temas.json ./
USER node
EXPOSE 3000
CMD ["node", "app.js"]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 003 — Prepare a versão 1.3

**Contexto do livro:**

> O && está dentro de uma instrução RUN: a segunda análise de sintaxe só será executada se a primeira terminar com sucesso. Não estamos iniciando a aplicação durante o build. A base, o usuário e o comando padrão permanecem os mesmos.

> Mantenha o .dockerignore do capítulo anterior, inclusive .env e .env.*. Com os arquivos salvos, construa:

```text
docker build -t tnp-catalogo:1.3 .
docker image inspect --format "{{.Id}}" tnp-catalogo:1.3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 004 — A primeira configuração pertence à execução

**Contexto do livro:**

> Queremos um catálogo identificado como homologação, na porta 8087 do host, mantendo a escuta interna padrão em 3000. Execute a linha inteira:

```text
docker run --pull=never -d --name catalogo-config -p 127.0.0.1:8087:3000 -e APP_ENV=homologacao tnp-catalogo:1.3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 005 — A primeira configuração pertence à execução

**Contexto do livro:**

> -e NOME=valor fornece uma variável ao ambiente do container criado. Aqui informamos apenas APP_ENV: os padrões de PORT e HOST são escolhas do nosso código. Todas as opções Docker estão antes da referência da imagem; depois dela começam o comando e seus argumentos. [3]

> Antes do navegador, consulte:

```text
docker ps --filter name=catalogo-config
docker port catalogo-config
docker logs --tail 10 catalogo-config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 006 — A primeira configuração pertence à execução

**Contexto do livro:**

> O log de inicialização da nossa aplicação informa evento, PID, porta, host e ambiente. Espere homologacao, 3000 e 0.0.0.0. Os números de identificação e horários do seu ambiente não precisam coincidir com os de outra pessoa.

> Abra http://127.0.0.1:8087/api/config. O resultado esperado é:

```text
{"ambiente":"homologacao","porta":3000}
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 007 — Um arquivo de ambiente não é uma ligação permanente

**Contexto do livro:**

> Quando a lista de opções cresce, é útil registrar os valores em um arquivo. Na pasta do projeto, crie .env.cap05-homologacao, em UTF-8, com exatamente:

```text
APP_ENV=homologacao
HOST=0.0.0.0
PORT=3000
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 008 — Um arquivo de ambiente não é uma ligação permanente

**Contexto do livro:**

> Também não presuma a interpolação de variáveis disponível em outros leitores de arquivos .env. Em particular, a interpolação do Compose não é uma propriedade do docker run --env-file. O Compose terá seu capítulo; aqui trabalhamos com o comando explícito. [5]

> Crie outra execução, na porta 8088:

```text
docker run --pull=never -d --name catalogo-envfile --env-file .env.cap05-homologacao -p 127.0.0.1:8088:3000 tnp-catalogo:1.3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 009 — Um arquivo de ambiente não é uma ligação permanente

**Contexto do livro:**

> Consulte http://127.0.0.1:8088/api/config. Deverá apresentar o mesmo ambiente da primeira execução. Compare as origens:

```text
docker inspect --format "{{.Image}}" catalogo-config
docker inspect --format "{{.Image}}" catalogo-envfile
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 010 — Preveja antes de reiniciar

**Contexto do livro:**

> Agora altere somente APP_ENV no arquivo para producao e salve. Não faça um build. Antes de agir, responda: o container existente conhece essa edição do arquivo no host?

> Execute:

```text
docker restart catalogo-envfile
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 011 — Preveja antes de reiniciar

**Contexto do livro:**

> Temos duas informações diferentes: o arquivo no host já contém o novo valor; o objeto existente conserva o valor recebido na criação. Para aplicar o arquivo atualizado, precisamos criar outro container com essa configuração.

> O catálogo continua somente de leitura, sem dados de usuários ou montagens. Depois de confirmar que este é o objeto descartável do exercício, substitua-o:

```text
docker stop catalogo-envfile
docker rm catalogo-envfile
docker run --pull=never -d --name catalogo-envfile --env-file .env.cap05-homologacao -p 127.0.0.1:8088:3000 tnp-catalogo:1.3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 012 — Preveja antes de reiniciar

**Contexto do livro:**

> A rota agora deverá informar producao. Confirme também que a imagem continua sendo 1.3. O nome do container foi reaproveitado, mas o objeto foi recriado. Nenhum arquivo de aplicação precisou ser reconstruído.

> Ao terminar a comparação, pare e remova apenas catalogo-envfile. Restaure APP_ENV para homologacao no arquivo do host, mantendo uma referência coerente com seu nome.

```text
docker stop catalogo-envfile
docker rm catalogo-envfile
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 013 — Uma requisição atravessa endereços diferentes

**Contexto do livro:**

> Retome a publicação da primeira execução:

```text
127.0.0.1:8087:3000
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 014 — Uma requisição atravessa endereços diferentes

**Contexto do livro:**

> O endereço 127.0.0.1 pertence ao lado do host. Ele limita o ponto de entrada escolhido para o laboratório. A porta 8087 é a entrada; 3000 é o destino no container. Isso não manda o Node.js abrir a porta 3000: o programa ainda precisa escutar no endereço e na porta compatíveis.

> Na configuração atual, a cadeia é:

```text
Navegador no host
  -> 127.0.0.1:8087
  -> publicação do Docker
  -> interface de rede do container, porta 3000
  -> servidor escutando em 0.0.0.0:3000
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 015 — docker exec: observar de dentro, sem criar outro servidor

**Contexto do livro:**

> Até aqui, observamos pelo Engine e pelo navegador. Agora queremos responder: o catálogo atende uma requisição feita dentro de seu próprio ambiente de rede?

> Execute:

```text
docker exec catalogo-config node diagnostico.js
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 016 — docker exec: observar de dentro, sem criar outro servidor

**Contexto do livro:**

> Isso é diferente de criar um novo container com docker run. Também não substitui o processo principal. A saúde respondida ao cliente interno não comprova, sozinha, que a publicação do host funciona: acabamos de testar outro trecho do caminho.

> Podemos consultar o diretório e a identidade do usuário sem instalar ferramentas:

```text
docker exec catalogo-config pwd
docker exec catalogo-config id
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 017 — docker exec: observar de dentro, sem criar outro servidor

**Contexto do livro:**

> O diretório esperado é /app, e a execução deve usar o usuário definido na imagem. Para uma inspeção interativa, existe:

```text
docker exec -it catalogo-config sh
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 018 — O ambiente do novo processo não reconfigura o servidor

**Contexto do livro:**

> Faça uma previsão antes desta consulta:

```text
docker exec -e APP_ENV=producao catalogo-config node -p "process.env.APP_ENV"
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 019 — Quem mantém o container em execução?

**Contexto do livro:**

> No capítulo 4, definimos CMD e preservamos o ENTRYPOINT da imagem base. Consulte ambos:

```text
docker image inspect --format "{{json .Config.Entrypoint}}" tnp-catalogo:1.3
docker image inspect --format "{{json .Config.Cmd}}" tnp-catalogo:1.3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 020 — Quem mantém o container em execução?

**Contexto do livro:**

> A entrada herdada é um script da imagem oficial do Node.js. Para o nosso comando, ele termina encaminhando a execução com exec, substituindo-se pelo programa escolhido. No laboratório padrão, sem --init ou compartilhamento especial de PID, esperamos que node app.js seja o processo principal no espaço de processos do container. [13]

> Observe o nome desse processo no ambiente Linux:

```text
docker exec catalogo-config cat /proc/1/comm
docker top catalogo-config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 021 — CMD, argumentos e ENTRYPOINT

**Contexto do livro:**

> A forma de lista em CMD ["node", "app.js"] não inicia automaticamente um shell para interpretar a linha. Na combinação usada aqui, ela fornece o comando padrão encaminhado pela entrada herdada. Não conte com expansão automática de variáveis de shell dentro de uma lista JSON. [10]

> Compare duas tarefas curtas:

```text
docker run --rm --pull=never tnp-catalogo:1.3 node --version
docker run --rm --pull=never --entrypoint node tnp-catalogo:1.3 --version
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 022 — Logs, estado e recursos respondem a perguntas diferentes

**Contexto do livro:**

> Agora que existem vários pontos de observação, precisamos escolher qual pergunta cada um pode responder.

> Para investigar requisições recentes e mensagens de inicialização:

```text
docker logs --since 5m --timestamps --tail 30 catalogo-config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 023 — Logs, estado e recursos respondem a perguntas diferentes

**Contexto do livro:**

> Nossa implementação escreve requisições em stdout e falhas em stderr. docker logs consulta o mecanismo de logs do container; não procura automaticamente qualquer arquivo .log dentro dele. Além disso, a saída do processo interativo de exec é recebida naquela sessão, não deve ser confundida com os logs do servidor principal. [17]

> Para uma fotografia do consumo:

```text
docker stats --no-stream catalogo-config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 024 — Encerramento é parte do funcionamento

**Contexto do livro:**

> Queremos interromper o servidor com oportunidade de finalizar conexões. Antes do comando, observe os logs e confirme que está operando o container correto:

```text
docker stop --timeout 10 catalogo-config
docker inspect --format "{{.State.Status}}" catalogo-config
docker inspect --format "{{.State.ExitCode}}" catalogo-config
docker logs --tail 10 catalogo-config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 025 — Encerramento é parte do funcionamento

**Contexto do livro:**

> Nosso código trata SIGTERM e SIGINT, interrompe a aceitação de novas conexões e reserva até cinco segundos para fechar o servidor. Na condição normal do laboratório, esperamos a mensagem de encerramento e código zero. O fechamento e o tratamento de conexões pertencem à aplicação, não são uma garantia fornecida apenas pelo comando stop. [2][20]

> Se o resultado for diferente, reúna estado e logs. Consulte também:

```text
docker inspect --format "{{.State.OOMKilled}}" catalogo-config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 026 — Encerramento é parte do funcionamento

**Contexto do livro:**

> Não classifique todo código 137 como falta de memória: um encerramento forçado pode ter outras origens. O estado OOMKilled, os logs e as condições de recursos ajudam a formular uma hipótese; um número isolado não basta. Não provocaremos falta de memória neste laboratório. [21]

> Retome o mesmo container para os experimentos seguintes:

```text
docker start catalogo-config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 027 — Falha controlada: o valor chegou, mas não é válido

**Contexto do livro:**

> Vamos produzir um erro de configuração sem interferir no servidor que funciona. O nome catalogo-falha precisa estar livre. Não publicaremos nenhuma porta e não usaremos --rm, porque o objeto será útil para análise.

```text
docker run --pull=never --name catalogo-falha -e PORT=abc tnp-catalogo:1.3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 028 — Falha controlada: o valor chegou, mas não é válido

**Contexto do livro:**

> Antes de ler a solução, pergunte: esta variável obriga Docker a validar uma porta, ou será interpretada pelo nosso programa?

> A aplicação recebe texto, rejeita abc, registra uma mensagem de configuração e encerra com código 1. A imagem pode estar perfeitamente construída; a falha pertence aos valores desta execução. Consulte:

```text
docker ps -a --filter name=catalogo-falha
docker logs catalogo-falha
docker inspect --format "{{.State.ExitCode}}" catalogo-falha
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 029 — Falha controlada: o valor chegou, mas não é válido

**Contexto do livro:**

> Outro caso seria uma variável obrigatória ausente. Nosso programa, porém, documenta padrões para os três campos; não vamos inventar uma obrigatoriedade que ele não implementa. Aqui, ausência e valor inválido são situações diferentes.

> Depois de registrar a causa, remova apenas esse objeto encerrado. Crie uma execução válida variando também a porta interna:

```text
docker rm catalogo-falha
docker run --pull=never -d --name catalogo-falha -e PORT=4000 -p 127.0.0.1:8089:4000 tnp-catalogo:1.3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 030 — Falha controlada: o valor chegou, mas não é válido

**Contexto do livro:**

> Se a publicação terminasse em :3000, ela não corresponderia à escuta desta execução. A correção seria alinhar o destino à porta do processo, não reconstruir a imagem ou trocar apenas a porta do navegador.

> Encerre esta tentativa válida antes do próximo experimento:

```text
docker stop catalogo-falha
docker rm catalogo-falha
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 031 — Falha controlada: funciona por dentro, falha por fora

**Contexto do livro:**

> Agora criaremos outra instância do mesmo artefato. O mapeamento terá os números corretos, mas o servidor escutará somente no loopback interno:

```text
docker run --pull=never -d --name catalogo-falha -e HOST=127.0.0.1 -p 127.0.0.1:8089:3000 tnp-catalogo:1.3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 032 — Falha controlada: funciona por dentro, falha por fora

**Contexto do livro:**

> Consulte estado, publicação e logs. Depois tente http://127.0.0.1:8089/health no host. Na rede bridge deste laboratório, não esperamos a resposta do catálogo. O texto da falha no navegador pode variar; não depende de reproduzir uma mensagem específica.

> Em seguida, faça a consulta interna:

```text
docker exec catalogo-falha node diagnostico.js
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 033 — Falha controlada: funciona por dentro, falha por fora

**Contexto do livro:**

> As evidências se complementam: Up indica execução; o log identifica HOST=127.0.0.1; a sonda interna comprova uma resposta local; o teste pelo host falha. Nenhuma dessas informações isoladas descrevia o caminho completo.

> A correção consiste em recriar esta instância com HOST=0.0.0.0. Mantemos a restrição em 127.0.0.1 do lado do host. Aqui omitiremos HOST para utilizar o padrão do código:

```text
docker stop catalogo-falha
docker rm catalogo-falha
docker run --pull=never -d --name catalogo-falha -p 127.0.0.1:8089:3000 tnp-catalogo:1.3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 034 — Falha controlada: funciona por dentro, falha por fora

**Contexto do livro:**

> Repita os testes interno e externo. Agora ambos deverão receber a resposta de saúde. Confira também página e API. Não foi necessário remover a restrição de acesso local, desligar firewall, utilizar rede host ou elevar privilégios.

> Depois de verificar, pare e remova somente catalogo-falha. Esse nome e a porta 8089 voltam a ficar disponíveis.

```text
docker stop catalogo-falha
docker rm catalogo-falha
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 035 — Uma falha antes de o programa começar: porta ocupada

**Contexto do livro:**

> O primeiro servidor, catalogo-config, continua atendendo na porta 8087. Vamos tentar reservar o mesmo endereço e porta para outro container, deliberadamente:

```text
docker run --pull=never -d --name catalogo-conflito -p 127.0.0.1:8087:3000 tnp-catalogo:1.3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 036 — Uma falha antes de o programa começar: porta ocupada

**Contexto do livro:**

> Esperamos uma recusa de publicação. Diferentemente de PORT=abc, o problema ocorre na preparação da execução pelo Engine, não na validação realizada por app.js. Não há razão para esperar um log de erro do nosso servidor se ele nem chegou a iniciar.

> Observe:

```text
docker ps -a --filter name=catalogo-conflito
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 037 — Uma falha antes de o programa começar: porta ocupada

**Contexto do livro:**

> Se a tentativa deixou o objeto criado, consulte:

```text
docker inspect --format "{{.State.Status}}" catalogo-conflito
docker inspect --format "{{.State.Error}}" catalogo-conflito
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 038 — Prepare a continuidade: mesma aplicação, estado conhecido

**Contexto do livro:**

> Vamos tornar 1.3 a base do endereço principal. Primeiro crie .env.cap05 na pasta do projeto:

```text
APP_ENV=desenvolvimento
HOST=0.0.0.0
PORT=3000
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 039 — Prepare a continuidade: mesma aplicação, estado conhecido

**Contexto do livro:**

> O container catalogo-web do capítulo 4 deverá estar parado e associado à versão anterior. Confirme sua identidade e seu estado com docker inspect catalogo-web. Se estiver ativo, pare-o antes da substituição. Não substitua um serviço desconhecido que por acaso use o mesmo nome.

> O catálogo ainda não armazena alterações de usuários: os dados continuam no JSON empacotado. Depois dessa confirmação, remova apenas o objeto antigo e crie a nova execução:

```text
docker rm catalogo-web
docker run --pull=never -d --name catalogo-web --env-file .env.cap05 -p 127.0.0.1:8084:3000 tnp-catalogo:1.3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 040 — Prepare a continuidade: mesma aplicação, estado conhecido

**Contexto do livro:**

> Se o container principal não existia mais, omita a remoção e faça somente a criação. Verifique na porta 8084 a página, os temas, a saúde e a configuração. A marca Edição 2 é preservada; a nova capacidade é configurar a execução externamente.

> O servidor auxiliar de homologação já cumpriu sua função. Pare e remova somente ele, depois deixe o principal parado para a próxima sessão:

```text
docker stop catalogo-config
docker rm catalogo-config
docker stop catalogo-web
docker ps -a --filter name=catalogo
docker image ls tnp-catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 041 — app.js — configuração, rotas e encerramento

**Contexto do livro:**

> A validação acontece antes de abrir a escuta. As restrições dos campos pertencem ao nosso laboratório. As rotas anteriores permanecem, /api/config expõe apenas dois valores escolhidos, e o encerramento evita tratar repetidamente o mesmo pedido de parada.

```text
'use strict';
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

function lerConfiguracao() {
  const textoPorta = process.env.PORT ?? '3000';
  const porta = Number(textoPorta);
  const host = process.env.HOST ?? '0.0.0.0';
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 042 — app.js — configuração, rotas e encerramento

**Contexto do livro:**

> A validação acontece antes de abrir a escuta. As restrições dos campos pertencem ao nosso laboratório. As rotas anteriores permanecem, /api/config expõe apenas dois valores escolhidos, e o encerramento evita tratar repetidamente o mesmo pedido de parada.

```text
  const ambiente = process.env.APP_ENV ?? 'desenvolvimento';
  if (!/^\d+$/.test(textoPorta) || !Number.isInteger(porta) ||
      porta < 1024 || porta > 65535) {
    throw new Error('PORT deve ser um inteiro entre 1024 e 65535.');
  }
  if (!['0.0.0.0', '127.0.0.1'].includes(host)) {
    throw new Error('HOST deve ser 0.0.0.0 ou 127.0.0.1 neste laboratorio.');
  }
  if (!['desenvolvimento', 'homologacao', 'producao'].includes(ambiente)) {
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 043 — app.js — configuração, rotas e encerramento

```text
    throw new Error('APP_ENV deve ser desenvolvimento, homologacao ou producao.');
  }
  return { porta, host, ambiente };
}

function iniciar() {
  let config;
  try {
    config = lerConfiguracao();
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 044 — app.js — configuração, rotas e encerramento

```text
  } catch (erro) {
    console.error(`Configuracao invalida: ${erro.message}`);
    process.exitCode = 1;
    return;
  }
  const arquivos = new Map([
    ['/', ['index.html', 'text/html; charset=utf-8']],
    ['/api/temas', ['temas.json', 'application/json; charset=utf-8']]
  ]);
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 045 — app.js — configuração, rotas e encerramento

```text
  const servidor = http.createServer((req, res) => {
    res.setHeader('Cache-Control', 'no-store');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    let caminho;
    try {
      caminho = new URL(req.url, 'http://localhost').pathname;
    } catch {
      res.writeHead(400);
      return res.end('Requisicao invalida.');
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 046 — app.js — configuração, rotas e encerramento

```text
    }
    console.log(JSON.stringify({ metodo: req.method, caminho }));
    if (req.method !== 'GET') {
      res.writeHead(405, { Allow: 'GET' });
      return res.end('Metodo nao permitido.');
    }
    if (caminho === '/health' || caminho === '/api/config') {
      const resposta = caminho === '/health'
        ? { status: 'ok' }
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 047 — app.js — configuração, rotas e encerramento

```text
        : { ambiente: config.ambiente, porta: config.porta };
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      return res.end(JSON.stringify(resposta));
    }
    const arquivo = arquivos.get(caminho);
    if (!arquivo) {
      res.writeHead(404);
      return res.end('Rota nao encontrada.');
    }
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 048 — app.js — configuração, rotas e encerramento

```text
    fs.readFile(path.join(__dirname, arquivo[0]), (erro, dados) => {
      if (erro) {
        console.error(erro.message);
        res.writeHead(500);
        return res.end('Falha ao ler arquivo da aplicacao.');
      }
      res.writeHead(200, { 'Content-Type': arquivo[1] });
      res.end(dados);
    });
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 049 — app.js — configuração, rotas e encerramento

```text
  });
  servidor.on('error', (erro) => {
    console.error(`Falha ao iniciar: ${erro.code ?? 'ERRO'}: ${erro.message}`);
    process.exitCode = 1;
  });
  servidor.listen(config.porta, config.host, () => {
    console.log(JSON.stringify({ evento: 'inicio', pid: process.pid, ...config }));
  });
  let encerrando = false;
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 050 — app.js — configuração, rotas e encerramento

```text
  for (const sinal of ['SIGTERM', 'SIGINT']) {
    process.on(sinal, () => {
      if (encerrando) return;
      encerrando = true;
      console.log(`Encerrando: ${sinal}`);
      const limite = setTimeout(() => process.exit(1), 5000);
      limite.unref();
      servidor.close(() => {
        clearTimeout(limite);
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 051 — app.js — configuração, rotas e encerramento

```text
        process.exitCode = 0;
      });
    });
  }
}

iniciar();
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 052 — diagnostico.js — uma consulta HTTP com prazo definido

**Contexto do livro:**

> O argumento opcional permite escolher outra URL; sem ele, a sonda consulta o loopback e a porta do ambiente de execução. Não substitui testes completos da aplicação nem configura automaticamente um HEALTHCHECK Docker. [12]

```text
'use strict';
const porta = process.env.PORT ?? '3000';
const url = process.argv[2] ?? `http://127.0.0.1:${porta}/health`;
fetch(url, { signal: AbortSignal.timeout(3000) })
  .then(async (resposta) => {
    console.log(`HTTP ${resposta.status}`);
    console.log(await resposta.text());
    if (!resposta.ok) process.exitCode = 1;
  })
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 053 — diagnostico.js — uma consulta HTTP com prazo definido

**Contexto do livro:**

> O argumento opcional permite escolher outra URL; sem ele, a sonda consulta o loopback e a porta do ambiente de execução. Não substitui testes completos da aplicação nem configura automaticamente um HEALTHCHECK Docker. [12]

```text
  .catch((erro) => {
    console.error(`Falha HTTP: ${erro.cause?.code ?? erro.name}`);
    process.exitCode = 1;
  });
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*
