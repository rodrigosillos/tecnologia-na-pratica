# Capítulo 10 — trechos e comandos para consulta

> NÃO EXECUTE ESTE ARQUIVO INTEIRO. Ele contém comandos, trechos parciais, modelos, saídas e falhas deliberadas. Use somente a etapa indicada no livro, com suas pré-condições e verificações.

Fonte: manuscrito consolidado R02. O texto de cada bloco foi preservado, inclusive quebras reais. A numeração abaixo localiza os blocos neste arquivo; não é uma sequência automática de execução.

Marcadores como `ID_OBTIDO` não são valores reais. Comandos de remoção, alterações e falhas controladas exigem a identificação prévia dos recursos. Os parágrafos de contexto são lembretes; não substituem a seção completa do livro.

## Trecho 001 — Retome o estado e preserve uma referência

**Contexto do livro:**

> O Capítulo 9 termina com o projeto tnp-catalogo parado, catálogo 1.5, entrada 1.0, rede tnp-catalogo_rede e volume externo tnp-catalogo-dados. A página ainda está em Edição 3, com Git e GitHub, SQL e Docker. Os controles de escrita, recursos e logs já estão na configuração.

> Extraia o pacote do capítulo em uma pasta nova. Trabalhe em laboratorio. O arquivo compose.cap09.yaml é uma cópia da definição anterior. A pasta referencia-cap09 preserva os fontes anteriores para comparação; nenhuma dessas cópias contém suas anotações reais.

```text
laboratorio/
  compose.cap09.yaml        definição anterior
  compose.yaml              definição de execução desta entrega
  compose.falha.yaml         alteração usada somente no teste
  .env                      valores do principal, versão 1.6
  .env.aceite                valores da execução de teste
  .env.aceite-retorno        teste com a imagem anterior
  .env.retorno               retorno do principal, se necessário
  catalogo-estudos/          fontes da versão 1.6
  entrada/                  Nginx preservado
  referencia-cap09/          fontes anteriores, para comparação
  testes/                   verificadores e seus resultados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 002 — Retome o estado e preserve uma referência

**Contexto do livro:**

> Use o mesmo contexto de Engine local e containers Linux. Comece consultando:

```text
docker version
docker compose version
docker compose -f compose.cap09.yaml config --quiet
docker compose -f compose.cap09.yaml ps -a
docker image inspect tnp-catalogo:1.5 tnp-entrada:1.0
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 003 — Reconheça os dados antes de testar outra versão

**Contexto do livro:**

> Não haverá gravações no principal durante a cópia e a avaliação. Use a definição anterior para iniciar apenas o catálogo existente:

```text
docker compose -f compose.cap09.yaml start --wait --wait-timeout 60 catalogo
docker compose -f compose.cap09.yaml exec -T catalogo node anotar.js --listar
docker compose -f compose.cap09.yaml stop
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 004 — Reconheça os dados antes de testar outra versão

**Contexto do livro:**

> Reconheça as anotações e confirme que a instância pertence ao projeto esperado. A cópia precisa partir do volume correto, não simplesmente de qualquer arquivo com o mesmo nome. Se as instâncias já não existirem, retome o procedimento de recuperação dos capítulos anteriores antes de seguir; start não cria o que está ausente.

> Crie backup-cap10 somente se esse destino ainda não existir. Havendo uma cópia anterior, escolha outro diretório e use o novo caminho em todos os passos correspondentes.

```text
mkdir backup-cap10
docker compose -f compose.cap09.yaml cp catalogo:/app/dados/anotacoes.json ./backup-cap10/anotacoes.json
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 005 — Faça uma mudança pequena e verificável

**Contexto do livro:**

> Em catalogo-estudos/index.html, troque somente a marca Edição 3 por Edição 4. Em temas.json, acrescente o quarto tema. O conteúdo completo desse JSON fica:

```text
[
  { "id": 1, "nome": "Git e GitHub" },
  { "id": 2, "nome": "SQL" },
  { "id": 3, "nome": "Docker" },
  { "id": 4, "nome": "Docker Compose" }
]
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 006 — Faça uma mudança pequena e verificável

**Contexto do livro:**

> O Dockerfile continua separando verificacao de execucao, copiando para o estágio final apenas os seis arquivos necessários ao catálogo. O COPY --from seleciona arquivos do estágio indicado; o contexto continua limitado pelo .dockerignore. [7] O pacote contém todos os arquivos, incluindo os que não mudaram.

> Verifique primeiro se a tag candidata está livre ou se pertence a uma tentativa sua que já foi identificada. Construa sem alterar 1.5:

```text
docker image ls tnp-catalogo:1.6
docker build --progress=plain --target execucao -t tnp-catalogo:1.6 ./catalogo-estudos
docker image inspect --format "{{.Id}} {{.Os}}/{{.Architecture}}" tnp-catalogo:1.6
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 007 — Uma definição de execução, quatro conjuntos de valores

**Contexto do livro:**

> Também tornamos explícitas quatro escolhas: projeto, imagem do catálogo, porta de entrada e volume. O restante dos controles permanece igual ao Capítulo 9.

> O compose.yaml completo é:

```text
name: ${TNP_PROJETO:?Defina TNP_PROJETO}

services:
  catalogo:
    image: ${TNP_IMAGEM_CATALOGO:?Defina TNP_IMAGEM_CATALOGO}
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
    name: ${TNP_VOLUME_DADOS:?Defina TNP_VOLUME_DADOS}
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 008 — Uma definição de execução, quatro conjuntos de valores

**Contexto do livro:**

> A retirada de build não remove os Dockerfiles do projeto. Ela separa o contrato de execução das instruções de construção. Usuários, raiz somente leitura, limites, logs, sonda, dependência e temporário da entrada mantêm a finalidade já estudada. [1]

> Na raiz, .env contém os valores do principal:

```text
TNP_PROJETO=tnp-catalogo
TNP_IMAGEM_CATALOGO=tnp-catalogo:1.6
TNP_PORTA_HTTP=8084
TNP_VOLUME_DADOS=tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 009 — Uma definição de execução, quatro conjuntos de valores

**Contexto do livro:**

> O arquivo .env.aceite usa outros recursos:

```text
TNP_PROJETO=tnp-cap10-aceite
TNP_IMAGEM_CATALOGO=tnp-catalogo:1.6
TNP_PORTA_HTTP=8096
TNP_VOLUME_DADOS=tnp-cap10-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 010 — Uma definição de execução, quatro conjuntos de valores

**Contexto do livro:**

> A cláusula external: true continua exigindo que o volume exista. Ela não compara seu conteúdo nem o torna imutável. [4] A diferença entre principal e aceite depende de três escolhas independentes: nome de projeto, porta e nome de volume. Trocar somente o projeto não isolaria o armazenamento externo.

> Antes de qualquer criação, consulte os dois modelos:

```text
docker compose config
docker compose --env-file .env.aceite config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 011 — Prepare o aceite sem tocar no volume original

**Contexto do livro:**

> Confirme a ausência dos recursos reservados e a disponibilidade da imagem candidata. Uma mensagem de volume inexistente é esperada na primeira consulta; uma falha de comunicação com o Engine não é a mesma situação.

```text
docker ps -a --filter label=com.docker.compose.project=tnp-cap10-aceite
docker volume inspect tnp-cap10-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 012 — Prepare o aceite sem tocar no volume original

**Contexto do livro:**

> Crie apenas o volume novo de teste, com uma identificação de finalidade:

```text
docker volume create --label tnp.capitulo=10 --label tnp.finalidade=aceite tnp-cap10-dados
docker compose --env-file .env.aceite up -d --no-build --wait --wait-timeout 60
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 013 — Restaure a cópia no destino de teste

**Contexto do livro:**

> O volume de aceite precisa estar vazio e pertencer a esta sessão. Vamos substituir seu JSON inicial pela cópia reconhecida, nunca o arquivo do volume original. Pare o conjunto e confira a seleção mais uma vez:

```text
docker compose --env-file .env.aceite stop
docker compose --env-file .env.aceite config --volumes
docker compose --env-file .env.aceite cp ./backup-cap10/anotacoes.json catalogo:/app/dados/anotacoes.json
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 014 — Restaure a cópia no destino de teste

**Contexto do livro:**

> A propriedade do arquivo copiado precisa ser compatível com node. Em vez de iniciar o servidor como root ou ampliar permissões do diretório, executaremos uma tarefa curta apenas nesse volume:

```text
docker compose --env-file .env.aceite run --rm --no-deps -T --user 0:0 --cap-add CHOWN --cap-add DAC_OVERRIDE catalogo chown node:node /app/dados/anotacoes.json
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 015 — Restaure a cópia no destino de teste

**Contexto do livro:**

> Essa exceção existe porque uma cópia pode deixar o arquivo com propriedade diferente. CHOWN permite ajustar o dono; DAC_OVERRIDE permite atravessar o diretório restrito de dados, que pertence a node. Ser root sem essas capacidades não equivale a ignorar todas as permissões. [10][24] Ela não autoriza alterar recursivamente todo armazenamento. O comando deve terminar sem erro. Se houver recusa, investigue permissões e configuração efetivas antes de prosseguir.

> Inicie novamente o conjunto de aceite:

```text
docker compose --env-file .env.aceite up -d --no-build --wait --wait-timeout 60
docker compose --env-file .env.aceite exec -T catalogo node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 016 — Reúna evidências que não se substituem

**Contexto do livro:**

> Primeiro confira o artefato. Obtenha o ID da instância de aceite com docker compose --env-file .env.aceite ps -q catalogo. Copie o valor e substitua o marcador nas consultas seguintes. Não execute ID_ACEITE literalmente.

```text
docker inspect --format "{{.Image}}" ID_ACEITE
docker inspect --format "{{json .Mounts}}" ID_ACEITE
docker inspect --format "{{.HostConfig.ReadonlyRootfs}}" ID_ACEITE
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 017 — Reúna evidências que não se substituem

**Contexto do livro:**

> Ver a lista de temas no JSON não comprova que o JavaScript do navegador a exibiu. Abra a página e observe a lista renderizada. Da mesma forma, o retorno da sonda interna não comprova a publicação no host.

> Por fim, confira a escrita autorizada. Se a cópia tiver menos de 100 anotações, acrescente somente no aceite:

```text
docker compose --env-file .env.aceite exec -T catalogo node anotar.js "Aceite do Capitulo 10."
docker compose --env-file .env.aceite exec -T catalogo node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 018 — Falha controlada: saudável para quem?

**Contexto do livro:**

> Imagine agora que ambos os serviços apareçam ativos e a saúde do catálogo esteja válida, mas o navegador receba um erro da entrada. Antes de culpar a imagem ou o volume, quais trechos da comunicação você precisaria comparar?

> Vamos produzir essa condição apenas no aceite. O arquivo compose.falha.yaml contém:

```text
services:
  catalogo:
    environment:
      PORT: "4000"
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 019 — Falha controlada: saudável para quem?

**Contexto do livro:**

> Esse arquivo não é carregado automaticamente. Ele só participa quando informado com -f, depois do arquivo base. O Compose combina os modelos; neste caso, a configuração acrescenta environment.PORT, que prevalece sobre o valor de env_file. Os caminhos permanecem relativos ao primeiro arquivo. [15]

> Aplique a alteração somente ao catálogo de aceite:

```text
docker compose --env-file .env.aceite -f compose.yaml -f compose.falha.yaml config --quiet
docker compose --env-file .env.aceite -f compose.yaml -f compose.falha.yaml up -d --no-build --wait --wait-timeout 60 catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 020 — Falha controlada: saudável para quem?

**Contexto do livro:**

> A sonda usa a variável PORT da instância e deve continuar passando. Como o catálogo foi substituído, valide e recarregue a entrada para que ela volte a resolver o destino atual; assim não confundiremos a falha planejada de porta com um endereço antigo em memória:

```text
docker compose --env-file .env.aceite exec -T entrada nginx -t
docker compose --env-file .env.aceite exec -T entrada nginx -s reload
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 021 — Compare a intenção com o caminho efetivo

**Contexto do livro:**

> Leia os logs de ambos e consulte o catálogo de dentro da própria instância:

```text
docker compose --env-file .env.aceite logs --tail 20 catalogo entrada
docker compose --env-file .env.aceite exec -T catalogo node diagnostico.js
docker compose --env-file .env.aceite exec -T catalogo node diagnostico.js http://127.0.0.1:4000/api/config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 022 — Compare a intenção com o caminho efetivo

**Contexto do livro:**

> As consultas exec iniciam tarefas na instância em execução; os logs mostram o que os processos registraram. Nenhuma dessas operações aplica outra configuração ao servidor. [16][17]

> A correção neste exercício é retirar a alteração de teste e voltar à porta interna acordada. Não mudaremos o programa, o volume nem as restrições. Aplique somente o arquivo base, depois valide e recarregue a entrada:

```text
docker compose --env-file .env.aceite -f compose.yaml up -d --no-build --wait --wait-timeout 60 catalogo
docker compose --env-file .env.aceite exec -T entrada nginx -t
docker compose --env-file .env.aceite exec -T entrada nginx -s reload
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 023 — Ensaie o retorno antes de precisar dele

**Contexto do livro:**

> A hipótese é: selecionar 1.5 deve trazer Edição 3 e os três temas originais, sem desfazer as gravações. Isso é possível neste projeto porque as duas versões utilizam o mesmo código de armazenamento e o mesmo formato de arquivo. Em um sistema com migração incompatível, voltar a imagem poderia falhar ou corromper dados. Não trate o procedimento como garantia universal.

> Confira .env.aceite-retorno: projeto de aceite, porta 8096, volume de aceite e imagem 1.5. Pare a entrada para que ela carregue o destino novamente depois da troca:

```text
docker compose --env-file .env.aceite stop entrada
docker compose --env-file .env.aceite-retorno config --images
docker compose --env-file .env.aceite-retorno up -d --no-build --wait --wait-timeout 60
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 024 — Ensaie o retorno antes de precisar dele

**Contexto do livro:**

> Essa comparação separa duas operações. Retornar a versão seleciona outro programa compatível com os dados atuais. Restaurar uma cópia recupera o conteúdo de um momento anterior e exige decidir o que fazer com mudanças posteriores.

> Depois da prova, volte à candidata sem reconstruí-la:

```text
docker compose --env-file .env.aceite-retorno stop entrada
docker compose --env-file .env.aceite up -d --no-build --wait --wait-timeout 60
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 025 — Promova o artefato, não os dados de teste

**Contexto do livro:**

> O principal continua parado desde a cópia inicial. Se alguém voltou a gravar nele durante a avaliação, interrompa a promoção, reconheça o novo estado e atualize a cópia em outro destino. Uma referência antiga não deve ser anunciada como backup do estado atual.

> Confira o modelo padrão e as identidades preservadas:

```text
docker compose config
docker image inspect --format "{{.Id}}" tnp-catalogo:1.6
docker image inspect --format "{{.Id}}" tnp-catalogo:1.5
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 026 — Promova o artefato, não os dados de teste

**Contexto do livro:**

> O modelo precisa selecionar tnp-catalogo, porta 8084 e volume original. Não use .env.aceite nesta operação e não copie o JSON modificado do teste para o principal. O que passou no aceite e será reutilizado é a imagem, acompanhada do mesmo contrato de execução.

> Aplique sem build:

```text
docker compose up -d --no-build --wait --wait-timeout 60
docker compose ps -a
docker compose port entrada 8080
docker compose exec -T catalogo node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 027 — Se for necessário retornar no principal

**Contexto do livro:**

> A decisão depende da causa. Uma publicação de porta incorreta não exige voltar o código; uma regressão da candidata pode justificar o retorno. Primeiro preserve logs e observações. Confirme que o armazenamento continua legível pela versão anterior e interrompa gravadores durante a troca.

> O arquivo .env.retorno seleciona o projeto e o volume originais com a imagem 1.5. A sequência de retorno, somente se essa decisão for necessária, é:

```text
docker compose stop entrada
docker compose --env-file .env.retorno config
docker compose --env-file .env.retorno up -d --no-build --wait --wait-timeout 60
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 028 — Prepare uma entrega que outra pessoa consiga conferir

**Contexto do livro:**

> Uma pasta com YAML e uma mensagem “aqui funcionou” não descreve tudo que foi entregue. Reserve uma pasta nova entrega-cap10 para as evidências. Ela não fica no contexto de build do catálogo nem no da entrada.

```text
mkdir entrega-cap10
docker compose config --output ./entrega-cap10/compose.resolvido.yaml
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 029 — Transportar imagens não transporta os volumes

**Contexto do livro:**

> Para guardar os artefatos locais de execução e retorno, há uma alternativa sem publicar em um registry:

```text
docker image save --output ./entrega-cap10/imagens.tar tnp-catalogo:1.6 tnp-catalogo:1.5 tnp-entrada:1.0
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 030 — Encerre o teste sem apagar a entrega

**Contexto do livro:**

> Depois de verificar o principal, a execução de aceite pode ser retirada. Confirme que não precisa mais das anotações exclusivas do teste e que .env.aceite ainda aponta para seus recursos reservados.

```text
docker compose --env-file .env.aceite config
docker compose --env-file .env.aceite down
docker volume inspect tnp-cap10-dados
docker ps -a --filter volume=tnp-cap10-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 031 — Encerre o teste sem apagar a entrega

**Contexto do livro:**

> down remove as instâncias e a rede gerenciada desse projeto; o volume externo permanece. [20] Confira sua identificação de teste e suas dependências antes de decidir pela remoção final. Somente se ele for o volume descartável desta sessão, sem dados a preservar, execute:

```text
docker volume rm tnp-cap10-dados
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 032 — Encerre o teste sem apagar a entrega

**Contexto do livro:**

> A primeira operação remove armazenamento e pode eliminar seu conteúdo; a segunda deve continuar encontrando o volume original. Não use --force, prune ou limpeza global para encerrar o exercício. Uma recusa de remoção exige investigar quem referencia o volume, não remover dependências desconhecidas. [21]

> No principal, depois da conferência final, faça a pausa:

```text
docker compose stop
docker compose ps -a
docker volume inspect tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*
