# Capítulo 8 — trechos e comandos para consulta

> NÃO EXECUTE ESTE ARQUIVO INTEIRO. Ele contém comandos, trechos parciais, modelos, saídas e falhas deliberadas. Use somente a etapa indicada no livro, com suas pré-condições e verificações.

Fonte: manuscrito consolidado R02. O texto de cada bloco foi preservado, inclusive quebras reais. A numeração abaixo localiza os blocos neste arquivo; não é uma sequência automática de execução.

Marcadores como `ID_OBTIDO` não são valores reais. Comandos de remoção, alterações e falhas controladas exigem a identificação prévia dos recursos. Os parágrafos de contexto são lembretes; não substituem a seção completa do livro.

## Trecho 001 — Retome o ambiente antes de escrever o YAML

**Contexto do livro:**

> Extraia o pacote desta entrega em uma pasta nova. Execute os comandos a partir de laboratorio, onde ficará compose.yaml. O ZIP contém o programa e exemplos de configuração, não uma cópia das anotações reais do seu volume. Preserve também os backups e a pasta de bind mount dos capítulos anteriores.

> Comece pelas consultas:

```text
docker version
docker compose version
docker ps -a --filter name=catalogo
docker image inspect tnp-catalogo:1.4 tnp-entrada:1.0
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 002 — O que vamos preservar e o que passará a ser gerenciado

**Contexto do livro:**

> Essa decisão mantém os containers manuais parados como ponto de retorno temporário, sem misturar seus aliases com os novos. Não é necessário apagar o funcionamento anterior para começar a descrever o próximo estado.

> O caminho final continuará equivalente:

```text
Navegador -> 127.0.0.1:8084
         -> serviço entrada, porta 8080
         -> serviço catalogo, porta 3000
         -> /app/dados no volume tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 003 — Prepare os arquivos sem misturar suas responsabilidades

**Contexto do livro:**

> A estrutura relevante será:

```text
laboratorio/
  compose.yaml
  .env
  catalogo-estudos/
    .env.cap06
    .env.cap08
    Dockerfile
    app.js e demais arquivos preservados
  entrada/
    Dockerfile
    nginx.conf
    .dockerignore
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 004 — Prepare os arquivos sem misturar suas responsabilidades

**Contexto do livro:**

> Na raiz de laboratorio, o arquivo .env contém somente:

```text
TNP_PORTA_HTTP=8084
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 005 — Prepare os arquivos sem misturar suas responsabilidades

**Contexto do livro:**

> Em catalogo-estudos/.env.cap08, mantenha a mesma configuração válida do capítulo anterior:

```text
APP_ENV=desenvolvimento
HOST=0.0.0.0
PORT=3000
DATA_DIR=/app/dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 006 — Prepare os arquivos sem misturar suas responsabilidades

**Contexto do livro:**

> São arquivos UTF-8 com valores fictícios e não sensíveis. A cópia .env.cap08 permite experimentar sem alterar .env.cap06, que documenta a execução anterior. As regras .env e .env.* continuam no .dockerignore do catálogo.

> Agora crie compose.yaml com o conteúdo completo abaixo. Use espaços para indentação, não tabulações. O alinhamento indica a quem cada campo pertence: volumes dentro de um serviço configura montagens; volumes na raiz declara recursos do modelo. Não acrescente version: "3.8": esse campo é obsoleto e não seleciona a versão do programa Compose instalado. [5]

```text
name: tnp-catalogo

services:
  catalogo:
    image: tnp-catalogo:1.4
    build:
      context: ./catalogo-estudos
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

## Trecho 007 — Imagem define o artefato; build define como construí-lo

**Contexto do livro:**

> Incluímos as duas informações para documentar tanto a execução quanto a reconstrução. Isso não obriga a reconstruir a aplicação em toda retomada. Usaremos pull_policy: never e up --no-build na primeira migração: queremos reutilizar as imagens locais já observadas, sem buscar um repositório remoto que por acaso tenha nome semelhante.

> Se uma imagem necessária não existir, a operação deverá falhar. Somente nesse caso de recuperação, ou quando houver uma mudança de código deliberada, escolha a construção correspondente:

```text
docker compose build catalogo
docker compose build entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 008 — Estar iniciado ainda não significa estar pronto

**Contexto do livro:**

> A entrada depende do catálogo. Uma lista simples em depends_on ordenaria a inicialização, mas não comprovaria uma resposta HTTP. Usamos condition: service_healthy para aguardar o resultado da sonda do catálogo antes de iniciar o serviço dependente. [8]

> O comando da sonda é o mesmo cliente HTTP já utilizado:

```text
test: ["CMD", "node", "diagnostico.js"]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 009 — .env não é sinônimo de ambiente do container

**Contexto do livro:**

> O .env da raiz fornece TNP_PORTA_HTTP para a interpolação da publicação. Já env_file aponta para o arquivo que fornece APP_ENV, HOST, PORT e DATA_DIR ao container do catálogo. São usos diferentes. [10]

> Observe a expressão na porta:

```text
${TNP_PORTA_HTTP:?Defina TNP_PORTA_HTTP no .env}
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 010 — Valide a configuração antes de tocar na execução

**Contexto do livro:**

> Agora consulte o modelo que será aplicado:

```text
docker compose config --quiet
docker compose config
docker compose config --services
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 011 — Valide a configuração antes de tocar na execução

**Contexto do livro:**

> config não é um ensaio de implantação. Uma configuração válida não prova que o volume existe, que a porta está livre, que a imagem está disponível ou que o servidor responderá. Essas verificações dependem do estado do Engine e da aplicação.

> Antes da primeira criação, confirme também que não existe outro conjunto operado com o mesmo nome de projeto:

```text
docker compose ls --all
docker ps -a --filter label=com.docker.compose.project=tnp-catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 012 — Faça uma conferência dos dados antes da migração

**Contexto do livro:**

> Os containers manuais ainda devem estar parados. Inspecione catalogo-web e confirme a montagem original. Use-o para reconhecer as anotações antes de substituí-lo:

```text
docker inspect --format "{{json .Mounts}}" catalogo-web
docker start catalogo-web
docker exec catalogo-web node diagnostico.js
docker exec catalogo-web node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 013 — Faça uma conferência dos dados antes da migração

**Contexto do livro:**

> Espere a sonda responder antes de avançar; um início recente pode exigir repetir somente a consulta. Guarde o conteúdo da listagem para comparar depois. Não escreva anotações durante a migração.

> Pare o catálogo e o proxy manuais, caso estejam ativos. A porta 8084 precisa estar livre:

```text
docker stop catalogo-entrada
docker stop catalogo-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 014 — Faça uma conferência dos dados antes da migração

**Contexto do livro:**

> Atualize também a cópia de recuperação em uma pasta nova. A partir de laboratorio, crie backup-cap08 somente se esse destino ainda não contiver uma cópia anterior:

```text
mkdir backup-cap08
docker cp catalogo-web:/app/dados/anotacoes.json ./backup-cap08/anotacoes.json
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 015 — Crie o conjunto e verifique o que passou a existir

**Contexto do livro:**

> Com a configuração conferida, as imagens disponíveis e os serviços antigos parados, execute:

```text
docker compose up -d --no-build --wait --wait-timeout 60
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 016 — Crie o conjunto e verifique o que passou a existir

**Contexto do livro:**

> Para o catálogo, esperamos healthy. Para a entrada, que não possui sonda Docker própria, a espera comprova apenas execução. Por isso, o navegador continua fazendo parte do teste. Um retorno com erro também não garante que tudo foi desfeito: consulte quais objetos ficaram criados.

> Observe:

```text
docker compose ps -a
docker compose port entrada 8080
docker compose logs --tail 15 catalogo entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 017 — Crie o conjunto e verifique o que passou a existir

**Contexto do livro:**

> A listagem deve mostrar os dois serviços do projeto. O comando de porta deve indicar 127.0.0.1:8084, ou a porta escolhida no .env. O catálogo não deve apresentar uma publicação própria no host. ps oferece a visão por serviço; logs permitem relacionar a inicialização e as requisições aos dois processos. [16][17]

> Confira o trecho interno e os dados:

```text
docker compose exec -T catalogo node diagnostico.js
docker compose exec -T catalogo node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 018 — Crie o conjunto e verifique o que passou a existir

**Contexto do livro:**

> Abra http://127.0.0.1:8084/. Confira Edição 3, os três temas e as rotas /health, /api/config, /api/temas e /api/anotacoes. Compare as anotações com a leitura anterior, não com uma lista fixa inventada no texto.

> Para observar a montagem real, obtenha o ID atual:

```text
docker compose ps -q catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 019 — Crie o conjunto e verifique o que passou a existir

**Contexto do livro:**

> Copie o resultado e substitua ID_OBTIDO na consulta abaixo; não execute o marcador literalmente:

```text
docker inspect --format "{{json .Mounts}}" ID_OBTIDO
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 020 — Só depois da prova retire a execução manual

**Contexto do livro:**

> Agora há duas definições de operação: a antiga, em containers manuais parados, e a nova, gerenciada pelo Compose. Não mantenha ambas prontas para receber gravações no mesmo JSON. Após conferir o novo caminho e a cópia de recuperação, inspecione os objetos antigos uma última vez:

```text
docker inspect --format "{{.State.Status}} {{.Config.Image}}" catalogo-web
docker inspect --format "{{.State.Status}} {{.Config.Image}}" catalogo-entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 021 — Só depois da prova retire a execução manual

**Contexto do livro:**

> Se forem os containers parados desta transição, remova somente eles:

```text
docker rm catalogo-entrada catalogo-web
docker network inspect tnp-catalogo-rede
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 022 — Só depois da prova retire a execução manual

**Contexto do livro:**

> Confirme que nenhuma instância remanescente depende da rede antiga. Somente então remova essa rede, sem confundi-la com a nova tnp-catalogo_rede:

```text
docker network rm tnp-catalogo-rede
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 023 — Uma configuração nova não entra por restart

**Contexto do livro:**

> Queremos executar o mesmo catálogo em homologação, sem reconstruir suas imagens. Em catalogo-estudos/.env.cap08, altere somente:

```text
APP_ENV=homologacao
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 024 — Uma configuração nova não entra por restart

**Contexto do livro:**

> As outras três linhas permanecem. Rode docker compose config e observe o valor resolvido. Anote o ID atual de catalogo usando docker compose ps -q catalogo. Antes de executar, faça uma previsão: reiniciar o mesmo container fará o Compose substituir seu ambiente?

```text
docker compose restart --no-deps catalogo
docker compose exec -T catalogo node diagnostico.js http://127.0.0.1:3000/api/config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 025 — Uma configuração nova não entra por restart

**Contexto do livro:**

> Se a primeira consulta ocorrer antes de o servidor abrir a escuta, aguarde e repita apenas a sonda. O resultado esperado continua sendo desenvolvimento, e o ID é o mesmo. restart não aplica mudanças de configuração à instância existente; --no-deps limita o reinício solicitado ao serviço escolhido. [20]

> Agora aplique a definição nova:

```text
docker compose up -d --no-build --wait --wait-timeout 60 catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 026 — O proxy ainda precisa reencontrar o destino

**Contexto do livro:**

> Não considere o trabalho concluído apenas porque o novo catálogo ficou saudável. Nosso Nginx mantém a forma simples de resolução do capítulo 7. Primeiro confirme a resposta interna; depois valide e recarregue a entrada:

```text
docker compose exec -T entrada nginx -t
docker compose exec -T entrada nginx -s reload
docker compose logs --tail 15 entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 027 — Uma tarefa temporária não é um exec

**Contexto do livro:**

> Para executar a ferramenta de leitura em uma nova instância, existe:

```text
docker compose run --rm --no-deps catalogo node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 028 — Falha controlada: a verificação pergunta pelo lugar errado

**Contexto do livro:**

> Até aqui, usamos a sonda correta. Agora vamos alterar somente o que ela consulta. A aplicação continuará igual. Faça este experimento apenas no laboratório local, pois a entrada ficará temporariamente indisponível.

> Pare primeiro o serviço dependente:

```text
docker compose stop entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 029 — Falha controlada: a verificação pergunta pelo lugar errado

**Contexto do livro:**

> Em compose.yaml, substitua somente a linha test do healthcheck por:

```text
test: ["CMD", "node", "diagnostico.js", "http://127.0.0.1:3000/rota-inexistente"]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 030 — Falha controlada: a verificação pergunta pelo lugar errado

**Contexto do livro:**

> Não altere o volume, as imagens ou o programa. Antes da tentativa, explique: o YAML está incorreto ou a verificação está perguntando por uma rota que não existe?

```text
docker compose config --quiet
docker compose up -d --no-build --wait --wait-timeout 60
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 031 — Falha controlada: a verificação pergunta pelo lugar errado

**Contexto do livro:**

> A configuração pode ser válida e a inicialização do conjunto falhar. Depois das tentativas da sonda, esperamos o catálogo em execução, mas marcado como unhealthy; a condição da dependência não foi satisfeita para iniciar a entrada. Dependendo do instante, o comando pode terminar por falha de saúde ou pelo prazo de espera.

> Não repita up até alguma coisa mudar. Reúna evidências:

```text
docker compose ps -a
docker compose logs --tail 20 catalogo
docker compose exec -T catalogo node diagnostico.js
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 032 — Falha controlada: a verificação pergunta pelo lugar errado

**Contexto do livro:**

> A última consulta utiliza a rota correta e deverá receber HTTP 200. As requisições da sonda configurada atingem a rota inexistente, produzem HTTP 404 e fazem o cliente encerrar com código diferente de zero. O servidor não precisou cair para a verificação falhar.

> Obtenha novamente o ID com docker compose ps -q catalogo e inspecione a saúde. Substitua o marcador pelo ID desta instância:

```text
docker inspect --format "{{json .State.Health}}" ID_OBTIDO
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 033 — Falha controlada: a verificação pergunta pelo lugar errado

**Contexto do livro:**

> Consulte também o comando efetivamente configurado:

```text
docker inspect --format "{{json .Config.Healthcheck.Test}}" ID_OBTIDO
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 034 — Parar, iniciar e remover: escolha pelo estado desejado

**Contexto do livro:**

> Se o objetivo é fazer uma pausa preservando as instâncias, use:

```text
docker compose stop
docker compose ps -a
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 035 — Parar, iniciar e remover: escolha pelo estado desejado

**Contexto do livro:**

> stop interrompe a execução, sem remover os containers. start inicia instâncias existentes; não cria as ausentes nem aplica uma nova configuração. Essas responsabilidades continuam semelhantes às que você aprendeu antes do Compose. [21][22]

> Para retomar com uma verificação explícita da dependência, mantendo a configuração inalterada:

```text
docker compose start --wait --wait-timeout 60 catalogo
docker compose start entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 036 — Parar, iniciar e remover: escolha pelo estado desejado

**Contexto do livro:**

> Depois teste a entrada e as anotações. Compare os IDs: continuam sendo os mesmos objetos. Se o arquivo mudou, não substitua up por start esperando que o novo conteúdo seja aplicado.

> Já quando o objetivo é retirar as instâncias e a rede gerenciada do projeto, depois de confirmar o nome do projeto e a associação do volume, existe:

```text
docker compose down
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 037 — Parar, iniciar e remover: escolha pelo estado desejado

**Contexto do livro:**

> Na configuração deste laboratório, a operação remove os containers do projeto e sua rede. As imagens com nossas tags continuam disponíveis, e o volume externo permanece. A camada gravável de cada instância removida não é preservada por esse comando. [24]

> Observe separadamente:

```text
docker compose ps -a
docker network inspect tnp-catalogo_rede
docker volume inspect tnp-catalogo-dados
docker image inspect tnp-catalogo:1.4 tnp-entrada:1.0
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 038 — A prova de reconstrução do conjunto

**Contexto do livro:**

> Execute novamente:

```text
docker compose up -d --no-build --wait --wait-timeout 60
docker compose exec -T catalogo node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 039 — Prepare a continuidade: um modelo e um estado conhecidos

**Contexto do livro:**

> A configuração final deverá voltar ao arquivo completo deste capítulo: porta externa 8084, APP_ENV=desenvolvimento, sonda correta, volume externo original e nenhuma publicação direta no catálogo. Nenhum fonte do programa ou do Nginx precisou mudar.

> Faça a conferência final:

```text
docker compose config --quiet
docker compose ps -a
docker compose port entrada 8080
docker compose exec -T catalogo node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 040 — Prepare a continuidade: um modelo e um estado conhecidos

**Contexto do livro:**

> Confira a página e as rotas pelo host. Em seguida, deixe o conjunto parado para a próxima sessão:

```text
docker compose stop
docker compose ps -a
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*
