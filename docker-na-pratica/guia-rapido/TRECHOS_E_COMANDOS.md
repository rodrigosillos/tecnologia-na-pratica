# Guia rápido — trechos e comandos para consulta

> NÃO EXECUTE ESTE ARQUIVO INTEIRO. Ele contém comandos, trechos parciais, modelos, saídas e falhas deliberadas. Use somente a etapa indicada no livro, com suas pré-condições e verificações.

Fonte: manuscrito consolidado R02. O texto de cada bloco foi preservado, inclusive quebras reais. A numeração abaixo localiza os blocos neste arquivo; não é uma sequência automática de execução.

Marcadores como `ID_OBTIDO` não são valores reais. Comandos de remoção, alterações e falhas controladas exigem a identificação prévia dos recursos. Os parágrafos de contexto são lembretes; não substituem a seção completa do livro.

## Trecho 001 — 01. Confirmar o ambiente e o projeto

**Contexto do livro:**

> Pergunta: a CLI está falando com o Engine esperado e o Compose está selecionando o conjunto correto?

```text
docker version
docker info
docker compose version
docker compose config --quiet
docker compose config
docker compose ps -a
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 002 — 01. Confirmar o ambiente e o projeto

**Contexto do livro:**

> Confira: projeto, imagem, publicação, arquivo de ambiente da aplicação e nome externo do volume. Variáveis exportadas no terminal, opções -p, -f e arquivos adicionais podem mudar a seleção. A premissa do laboratório é não haver substituições ocultas por COMPOSE_*, TNP_* ou overrides. [3]

> Para observar o modelo de aceite do Capítulo 10, sem iniciá-lo:

```text
docker compose --env-file .env.aceite config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 003 — 02. Retomar ou pausar o conjunto

**Contexto do livro:**

> Para uma pausa, preservando as instâncias:

```text
docker compose stop
docker compose ps -a
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 004 — 02. Retomar ou pausar o conjunto

**Contexto do livro:**

> O efeito é interromper a execução, não remover os containers. Confirme que o volume original continua disponível. [4]

> Para retomar instâncias existentes, com configuração inalterada:

```text
docker compose start --wait --wait-timeout 60 catalogo
docker compose start entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 005 — 02. Retomar ou pausar o conjunto

**Contexto do livro:**

> Só execute a segunda linha se a primeira concluir com sucesso. A espera usa a saúde configurada no catálogo. start não cria instâncias ausentes nem aplica edições do YAML. [5]

> Quando for necessário criar ou aplicar o modelo conferido:

```text
docker compose up -d --no-build --wait --wait-timeout 60
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 006 — 03. Identificar a imagem usada

**Contexto do livro:**

> Pergunta: qual conteúdo a referência seleciona agora e qual imagem foi associada à instância?

```text
docker image ls tnp-catalogo
docker image inspect --format "{{.Id}}" tnp-catalogo:1.6
docker image inspect --format "{{.Os}}/{{.Architecture}}" tnp-catalogo:1.6
docker compose ps -q catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 007 — 03. Identificar a imagem usada

**Contexto do livro:**

> Copie o ID da instância retornado pela última consulta. Se não houver instância em execução, use docker compose ps -a para localizar o objeto; não invente um ID nem conclua que as imagens desapareceram.

```text
docker inspect --format "{{.Config.Image}}" ID_CATALOGO
docker inspect --format "{{.Image}}" ID_CATALOGO
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 008 — 03. Identificar a imagem usada

**Contexto do livro:**

> Config.Image registra a referência configurada na criação; Image identifica a imagem associada ao objeto. Compare com o registro da entrega no mesmo Engine e plataforma. Uma tag pode mudar de alvo sem alterar um container já criado. [7][8]

> Para investigar a construção, e não os logs da aplicação:

```text
docker image history tnp-catalogo:1.6
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 009 — 04. Construir uma candidata sem substituir a aprovada

**Contexto do livro:**

> Antes: reconheça os fontes, o Dockerfile, o contexto e uma referência livre para a candidata. Preserve a imagem aprovada e a de retorno. Não construa os fontes novos sob o nome 1.5 para suprir sua ausência.

> O modelo abaixo adapta a construção explícita do Capítulo 10. Substitua IMAGEM_CANDIDATA por uma referência deliberadamente escolhida:

```text
docker build --progress=plain --target execucao -t IMAGEM_CANDIDATA ./catalogo-estudos
docker image inspect IMAGEM_CANDIDATA
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 010 — 05. Aplicar configuração sem confundir com reinício

**Contexto do livro:**

> Pergunta: o valor mudou no arquivo, no modelo resolvido ou na instância em execução?

> No projeto final, .env fornece projeto, imagem, porta do host e volume para interpolação. catalogo-estudos/.env.cap08 fornece as variáveis lidas pelo Node.js. PORT escolhe a escuta da aplicação; TNP_PORTA_HTTP escolhe a publicação da entrada. [3]

```text
docker compose config
docker compose exec -T catalogo node diagnostico.js http://127.0.0.1:3000/api/config
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 011 — 05. Aplicar configuração sem confundir com reinício

**Contexto do livro:**

> A segunda consulta pressupõe o contrato final em 3000 e o catálogo ativo. Se a porta foi alterada deliberadamente, compare primeiro a configuração e os logs; não transforme a falha dessa URL em prova de servidor encerrado.

> Reiniciar o mesmo objeto, quando essa for a intenção:

```text
docker compose restart --no-deps catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 012 — 05. Aplicar configuração sem confundir com reinício

**Contexto do livro:**

> Esse reinício não aplica novos valores do arquivo de ambiente. Aplicar uma definição alterada, depois de conferir seus efeitos e proteger os dados, é outro objetivo: [11]

```text
docker compose up -d --no-build --wait --wait-timeout 60 catalogo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 013 — 05. Aplicar configuração sem confundir com reinício

**Contexto do livro:**

> Se apenas o catálogo for substituído com a entrada ativa, confirme a saúde interna e depois valide e recarregue nosso Nginx:

```text
docker compose exec -T entrada nginx -t
docker compose exec -T entrada nginx -s reload
docker compose logs --tail 15 entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 014 — 06. Investigar logs, encerramento e saúde

**Contexto do livro:**

> Comece pela evidência, antes de recriar:

```text
docker compose ps -a
docker compose logs --since 5m --timestamps --tail 30 catalogo entrada
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 015 — 06. Investigar logs, encerramento e saúde

**Contexto do livro:**

> Para acompanhar novas mensagens, use docker compose logs -f catalogo entrada. Ctrl+C encerra o acompanhamento, não é uma ordem para parar esses serviços. Logs dependem do que os processos registram; ausência de uma linha não explica, sozinha, uma falha. [13]

> Com o ID real da instância, consulte estado e resultado de saída:

```text
docker inspect --format "{{.State.Status}}" ID_CATALOGO
docker inspect --format "{{.State.ExitCode}}" ID_CATALOGO
docker inspect --format "{{.State.OOMKilled}}" ID_CATALOGO
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 016 — 06. Investigar logs, encerramento e saúde

**Contexto do livro:**

> Um código de saída só faz sentido no contexto da execução. Não transforme 137, isoladamente, em diagnóstico de falta de memória. Se o processo nem iniciou, examine também State.Error. Não use exec em um container encerrado para tentar corrigir sua configuração. [8]

> Quando o problema é a saúde configurada:

```text
docker inspect --format "{{json .Config.Healthcheck.Test}}" ID_CATALOGO
docker inspect --format "{{json .State.Health}}" ID_CATALOGO
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 017 — 06. Investigar logs, encerramento e saúde

**Contexto do livro:**

> No catálogo ativo, compare com a consulta conhecida:

```text
docker compose exec -T catalogo node diagnostico.js
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 018 — 07. Seguir o caminho de uma requisição

**Contexto do livro:**

> Primeiro identifique de onde parte o acesso. No host, use http://127.0.0.1:8084. Na rede do projeto, a entrada alcança http://catalogo:3000. O loopback de um cliente temporário aponta para ele próprio, não para o catálogo.

```text
docker compose port entrada 8080
docker network inspect tnp-catalogo_rede
docker inspect --format "{{json .NetworkSettings.Networks}}" ID_CATALOGO
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 019 — 07. Seguir o caminho de uma requisição

**Contexto do livro:**

> Para testar a API a partir de outro container, sem montar as anotações:

```text
docker run --rm --pull=never --network tnp-catalogo_rede tnp-catalogo:1.6 node diagnostico.js http://catalogo:3000/api/anotacoes
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 020 — 08. Localizar os dados e conferir a montagem

**Contexto do livro:**

> Pergunta: qual armazenamento atende ao caminho que a aplicação realmente usa?

```text
docker volume inspect tnp-catalogo-dados
docker inspect --format "{{json .Mounts}}" ID_CATALOGO
docker compose exec -T catalogo node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 021 — 08. Localizar os dados e conferir a montagem

**Contexto do livro:**

> A última consulta requer instância ativa. Na montagem, compare tipo, nome, destino e RW: o esperado é volume tnp-catalogo-dados, em /app/dados, com escrita habilitada. Depois confira /api/anotacoes pela entrada. Nome certo sem destino certo não comprova que o programa está lendo aqueles dados. [16]

> Para investigar dependências, inclusive paradas:

```text
docker ps -a --filter volume=tnp-catalogo-dados
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 022 — 09. Escolher entre processo adicional e tarefa temporária

**Contexto do livro:**

> A instância já executa e quero fazer uma consulta nela:

```text
docker compose exec -T catalogo node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 023 — 09. Escolher entre processo adicional e tarefa temporária

**Contexto do livro:**

> exec inicia um processo adicional na instância ativa. -T evita alocar um terminal para esta saída simples. Ele não cria outro container nem reconfigura o servidor. [18]

> Quero uma instância temporária a partir da definição do serviço:

```text
docker compose run --rm --no-deps -T catalogo node anotar.js --listar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 024 — 10. Conferir permissões e recursos

**Contexto do livro:**

> Pergunta: a configuração efetiva corresponde aos controles escolhidos e a aplicação continua funcionando?

```text
docker compose exec -T catalogo id
docker compose exec -T entrada id
docker inspect --format "{{.HostConfig.ReadonlyRootfs}}" ID_CATALOGO
docker inspect --format "{{json .HostConfig.CapDrop}}" ID_CATALOGO
docker inspect --format "{{json .HostConfig.SecurityOpt}}" ID_CATALOGO
docker compose stats --no-stream
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 025 — 11. Fazer uma cópia e planejar a recuperação

**Contexto do livro:**

> Antes: reconheça o conteúdo, confirme o volume e interrompa todos os gravadores. A pausa dos serviços não controla uma tarefa externa que alguém ainda esteja executando. O procedimento abaixo serve apenas ao JSON pequeno do laboratório.

> Escolha uma pasta nova. backup-consulta é um exemplo: se já existir, use outro destino em todas as linhas correspondentes.

```text
docker compose stop
mkdir backup-consulta
docker compose cp catalogo:/app/dados/anotacoes.json ./backup-consulta/anotacoes.json
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 026 — 12. Distinguir aceite, promoção e retorno

**Contexto do livro:**

> Retorno: selecionar a imagem anterior somente depois de examinar a causa e a compatibilidade dos dados. No nosso exercício, 1.5 e 1.6 usam o mesmo armazenamento. A volta da página para Edição 3 não deveria apagar as anotações atuais.

> Quando a decisão de retornar no principal já foi tomada, com dados reconhecidos, cópia protegida e gravadores interrompidos, o roteiro do capítulo utiliza:

```text
docker compose stop entrada
docker compose --env-file .env.retorno config
docker compose --env-file .env.retorno up -d --no-build --wait --wait-timeout 60
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 027 — 13. Transportar imagens sem confundi-las com dados

**Contexto do livro:**

> O Capítulo 10 apresenta uma opção sem publicação em registry. Com as imagens presentes, espaço disponível e uma pasta de entrega nova, o comando é:

```text
docker image save --output ./entrega-cap10/imagens.tar tnp-catalogo:1.6 tnp-catalogo:1.5 tnp-entrada:1.0
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 028 — 13. Transportar imagens sem confundi-las com dados

**Contexto do livro:**

> Ele grava imagens e referências locais. Não acrescenta o volume de anotações, containers em execução ou os arquivos do host automaticamente. Preserve os dados e a configuração separadamente. [22]

> Em outro ambiente, depois de conferir a origem, a integridade e possíveis conflitos com tags locais:

```text
docker image load --input imagens.tar
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 029 — 14. Remover somente o que foi decidido

**Contexto do livro:**

> Primeiro observe o consumo e as dependências:

```text
docker system df
docker system df -v
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 030 — 14. Remover somente o que foi decidido

**Contexto do livro:**

> Conteúdo compartilhado, caches e imagens sem container ativo ainda podem ser úteis. Espaço indicado como recuperável não é autorização para apagar. [24]

> Container manual descartável: confirme o nome, a origem, os dados e o estado. Se estiver ativo, pare; só depois remova. Nos projetos Compose, prefira a operação pelo projeto em vez de desmontar instâncias isoladamente sem necessidade.

```text
docker stop NOME_CONTAINER
docker rm NOME_CONTAINER
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*
