# Capítulo 3 — trechos e comandos para consulta

> NÃO EXECUTE ESTE ARQUIVO INTEIRO. Ele contém comandos, trechos parciais, modelos, saídas e falhas deliberadas. Use somente a etapa indicada no livro, com suas pré-condições e verificações.

Fonte: manuscrito consolidado R02. O texto de cada bloco foi preservado, inclusive quebras reais. A numeração abaixo localiza os blocos neste arquivo; não é uma sequência automática de execução.

Marcadores como `ID_OBTIDO` não são valores reais. Comandos de remoção, alterações e falhas controladas exigem a identificação prévia dos recursos. Os parágrafos de contexto são lembretes; não substituem a seção completa do livro.

## Trecho 001 — Retome o ambiente sem apagar o que já existe

**Contexto do livro:**

> Use o mesmo ambiente de containers Linux dos capítulos anteriores. O laboratório pressupõe um Docker Engine local, acessível pelo terminal, e acesso ao Docker Hub para os downloads iniciais. Não troque de contexto no meio da prática: o contexto seleciona o ambiente ao qual o cliente se conecta. [1]

> Comece consultando:

```text
docker version
docker ps -a
docker image ls nginx
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 002 — Retome o ambiente sem apagar o que já existe

**Contexto do livro:**

> Confirme que o servidor responde à primeira consulta. A última listagem deverá mostrar nginx:alpine se você preservou a imagem do capítulo 2. Uma listagem vazia não impede continuar; vamos obter a imagem explicitamente mais adiante.

> Reservaremos os containers web-imagens e web-imagens-novo, as tags locais tnp-web:lab e tnp-web:reserva e a porta 8083 no host. Verifique se esses nomes já pertencem a outro trabalho:

```text
docker ps -a --filter name=web-imagens
docker image ls tnp-web
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 003 — Leia a referência antes de baixar

**Contexto do livro:**

> Até aqui, usamos nginx:alpine como um nome conveniente. Agora podemos separar suas partes.

> Na resolução padrão de nomes do Docker, essa referência corresponde a:

```text
docker.io/library/nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 004 — Obter uma imagem é diferente de iniciar uma aplicação

**Contexto do livro:**

> Nos capítulos anteriores, docker run cuidou da obtenção da imagem quando ela não estava disponível. Agora separaremos essa etapa da criação do container.

> Queremos que a referência nginx:alpine esteja disponível no armazenamento do Engine, sem iniciar nenhum servidor. Execute:

```text
docker pull nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 005 — Obter uma imagem é diferente de iniciar uma aplicação

**Contexto do livro:**

> Há duas situações normais: o Docker pode obter conteúdo diferente do que estava disponível localmente, ou concluir que a referência já corresponde ao conteúdo disponível. Não é preciso haver um download grande para a consulta ter sido útil.

> Agora verifique dois tipos de objeto:

```text
docker image ls nginx
docker ps -a
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 006 — Inspecione a imagem, não apenas seu nome

**Contexto do livro:**

> Uma listagem responde “o que está disponível?”. A inspeção ajuda a responder “o que esta imagem descreve?”.

> Execute:

```text
docker image inspect nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 007 — Inspecione a imagem, não apenas seu nome

**Contexto do livro:**

> A saída é estruturada em JSON. Assim como no capítulo anterior, não precisamos ler tudo de uma vez. Vamos selecionar informações de interesse. A opção --format permite pedir campos específicos. [8]

> Consulte a identidade apresentada pelo Engine e os nomes associados:

```text
docker image inspect --format "{{.Id}}" nginx:alpine
docker image inspect --format "{{json .RepoTags}}" nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 008 — Inspecione a imagem, não apenas seu nome

**Contexto do livro:**

> Depois, consulte a plataforma:

```text
docker image inspect --format "{{.Os}}/{{.Architecture}}" nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 009 — Inspecione a imagem, não apenas seu nome

**Contexto do livro:**

> Anote o resultado do primeiro comando. Não copie um ID de uma ilustração ou de outra pessoa: os valores reais do seu ambiente serão nossa referência.

> Também podemos observar parâmetros padrão de inicialização:

```text
docker image inspect --format "{{json .Config.Entrypoint}}" nginx:alpine
docker image inspect --format "{{json .Config.Cmd}}" nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 010 — Camadas: reutilizar uma base sem transformar tudo em uma cópia

**Contexto do livro:**

> Uma imagem reúne camadas de alterações no sistema de arquivos, acompanhadas de configuração. Essas camadas são imutáveis depois de criadas e podem ser reutilizadas por outras imagens. [10]

> Pense em um exemplo conceitual, não no detalhamento exato do Nginx:

```text
Base com bibliotecas e utilitários
    + arquivos do servidor
    + configuração da aplicação
    + conteúdo que será servido
    = visão do sistema de arquivos da imagem
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 011 — Por que o tamanho não se resume a contar nomes

**Contexto do livro:**

> Suponha que três referências apontem para o mesmo conteúdo. A existência de três linhas na listagem não significa três downloads completos nem três cópias independentes de todas as camadas.

> Para observar o uso de armazenamento com mais contexto, existe uma consulta que não remove recursos:

```text
docker system df
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 012 — Por que o tamanho não se resume a contar nomes

**Contexto do livro:**

> Quando precisar distinguir tamanho compartilhado e exclusivo com mais detalhe, consulte:

```text
docker system df -v
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 013 — O histórico explica a construção, não a execução

**Contexto do livro:**

> Precisamos agora de outra perspectiva: quais passos ficaram registrados na formação da imagem?

> Execute:

```text
docker image history nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 014 — O histórico explica a construção, não a execução

**Contexto do livro:**

> Observe as informações de criação, comando registrado e tamanho. O histórico costuma ser apresentado dos registros mais recentes para os mais antigos. Para evitar o encurtamento de campos, use:

```text
docker image history --no-trunc nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 015 — Laboratório: dois nomes para a mesma imagem

**Contexto do livro:**

> Vamos construir uma prova pequena e controlada. Queremos dar nomes de laboratório ao conteúdo já obtido, sem modificar a referência oficial do Nginx.

> Se as tags reservadas ainda estiverem livres, execute:

```text
docker image tag nginx:alpine tnp-web:lab
docker image tag nginx:alpine tnp-web:reserva
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 016 — Laboratório: dois nomes para a mesma imagem

**Contexto do livro:**

> Antes de consultar, faça uma previsão: esses comandos construíram dois novos servidores ou apenas criaram outros nomes para a mesma base?

> Confira:

```text
docker image ls tnp-web
docker image inspect --format "{{.Id}}" nginx:alpine
docker image inspect --format "{{.Id}}" tnp-web:lab
docker image inspect --format "{{.Id}}" tnp-web:reserva
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 017 — Crie o servidor e registre sua origem

**Contexto do livro:**

> Queremos agora um container criado a partir de tnp-web:lab, acessível apenas pelo host na porta 8083. Usaremos --pull=never para impedir um download implícito: se a referência local estiver ausente, o comando deverá falhar, em vez de tentar encontrá-la no registry. [14]

> Execute a linha inteira:

```text
docker run --pull=never -d --name web-imagens -p 127.0.0.1:8083:80 tnp-web:lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 018 — Crie o servidor e registre sua origem

**Contexto do livro:**

> Confira:

```text
docker ps --filter name=web-imagens
docker port web-imagens
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 019 — Crie o servidor e registre sua origem

**Contexto do livro:**

> Se a porta estiver ocupada, escolha outra porta local livre. Antes de repetir run, consulte docker ps -a: uma falha de inicialização pode deixar o container criado e o nome ocupado. Inspecione-o e remova somente o objeto descartável desta tentativa, depois de confirmar sua identidade e seu estado. Não remova um serviço desconhecido para liberar a porta.

> Agora registre três informações do container:

```text
docker inspect --format "{{.Id}}" web-imagens
docker inspect --format "{{.Config.Image}}" web-imagens
docker inspect --format "{{.Image}}" web-imagens
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 020 — Uma troca controlada: o nome fica, o conteúdo apontado muda

**Contexto do livro:**

> Este passo é intencionalmente inadequado como configuração de um servidor. Execute-o apenas nas tags de laboratório. Vamos fazer tnp-web:lab apontar para hello-world. Não vamos modificar nginx:alpine, tnp-web:reserva nem recursos de outros projetos.

> Primeiro obtenha a outra imagem:

```text
docker pull hello-world:latest
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 021 — Uma troca controlada: o nome fica, o conteúdo apontado muda

**Contexto do livro:**

> Antes de continuar, responda: mudar a tag deveria trocar o processo dentro do servidor que já está executando?

> Agora altere a referência local:

```text
docker image tag hello-world:latest tnp-web:lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 022 — Uma troca controlada: o nome fica, o conteúdo apontado muda

**Contexto do livro:**

> Verifique a nova associação:

```text
docker image inspect --format "{{.Id}}" tnp-web:lab
docker image inspect --format "{{.Id}}" hello-world:latest
docker image inspect --format "{{.Id}}" tnp-web:reserva
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 023 — Uma troca controlada: o nome fica, o conteúdo apontado muda

**Contexto do livro:**

> As duas primeiras consultas deverão coincidir. A reserva continuará associada ao conteúdo do Nginx.

> Não houve uma transformação do Nginx em outro programa. Houve uma mudança de referência. O estado lógico agora é:

```text
tnp-web:reserva -> imagem do Nginx
tnp-web:lab     -> imagem do hello-world
web-imagens    -> continua associado à sua imagem de criação
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 024 — O que aconteceu com o servidor antigo?

**Contexto do livro:**

> Consulte novamente:

```text
docker inspect --format "{{.Id}}" web-imagens
docker inspect --format "{{.Config.Image}}" web-imagens
docker inspect --format "{{.Image}}" web-imagens
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 025 — O que aconteceu com o servidor antigo?

**Contexto do livro:**

> Compare com suas anotações. O container continua sendo o mesmo, e a identificação de sua imagem não deve ter mudado. O texto tnp-web:lab também permanece em sua configuração, embora a referência local com esse nome agora aponte para outra base.

> Acesse a página e confirme o estado com docker ps. O Nginx antigo continua sendo o processo do servidor. Agora reinicie esse mesmo objeto:

```text
docker restart web-imagens
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 026 — O que um novo container encontrará?

**Contexto do livro:**

> Vamos usar o mesmo nome de imagem, mas criar outro objeto, sem publicar porta e sem -d:

```text
docker run --pull=never --name web-imagens-novo tnp-web:lab
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 027 — O que um novo container encontrará?

**Contexto do livro:**

> O resultado esperado é a mensagem do hello-world, seguida do encerramento normal do programa. Não esperamos um segundo servidor web. Mantivemos o container após a saída para poder examiná-lo.

> Consulte:

```text
docker ps -a --filter name=web-imagens
docker inspect --format "{{.Config.Image}}" web-imagens-novo
docker inspect --format "{{.Image}}" web-imagens-novo
docker inspect --format "{{.State.ExitCode}}" web-imagens-novo
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 028 — Para ir além: digest e plataforma

**Contexto do livro:**

> Uma tag é confortável para leitura, mas pode mudar de alvo. Quando precisamos registrar exatamente o artefato selecionado no registry, utilizamos uma referência por digest. [6]

> Consulte as referências conhecidas depois do pull:

```text
docker image inspect --format "{{json .RepoDigests}}" nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 029 — Para ir além: digest e plataforma

**Contexto do livro:**

> A saída pode conter uma referência com nome de repositório, @sha256: e uma sequência hexadecimal. Copie o valor completo do seu ambiente, sem aspas ou colchetes. Para solicitar esse artefato, a forma é:

```text
docker pull REFERENCIA_COMPLETA_COM_DIGEST
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 030 — Remover uma referência não é apagar tudo que se relaciona com ela

**Contexto do livro:**

> Vamos encerrar o experimento preservando as imagens oficiais usadas como base. Primeiro observe:

```text
docker ps -a --filter name=web-imagens
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 031 — Remover uma referência não é apagar tudo que se relaciona com ela

**Contexto do livro:**

> O servidor web-imagens deverá estar ativo, e web-imagens-novo, encerrado. Se o estado estiver diferente, entenda a diferença antes de seguir.

> Pare o servidor e confirme que ele saiu da lista de ativos:

```text
docker stop web-imagens
docker ps --filter name=web-imagens
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 032 — Remover uma referência não é apagar tudo que se relaciona com ela

**Contexto do livro:**

> Os dois containers são descartáveis e não receberam dados importantes nem montagens do host neste laboratório. Remova apenas esses objetos:

```text
docker rm web-imagens web-imagens-novo
docker ps -a --filter name=web-imagens
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 033 — Remover uma referência não é apagar tudo que se relaciona com ela

**Contexto do livro:**

> Agora remova as referências locais criadas para a experiência:

```text
docker image rm tnp-web:lab
docker image rm tnp-web:reserva
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 034 — Remover uma referência não é apagar tudo que se relaciona com ela

**Contexto do livro:**

> Nesse estado, hello-world:latest ainda referencia sua imagem, e nginx:alpine ainda referencia a outra. Esperamos remover os nomes de laboratório, não os conteúdos que continuam referenciados pelas imagens oficiais. A resposta pode indicar Untagged. [17]

> Confira separadamente:

```text
docker image ls tnp-web
docker image ls nginx:alpine
docker image ls hello-world:latest
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 035 — Remover uma referência não é apagar tudo que se relaciona com ela

**Contexto do livro:**

> docker image rm atua no armazenamento do Engine consultado, não apaga a publicação no registry. Quando a última referência é removida e o conteúdo pode ser liberado, a operação pode excluir dados locais. Containers existentes e conteúdo compartilhado influenciam o que pode ser removido. Não acrescente --force automaticamente diante de uma recusa. [17]

> Se precisar investigar dependentes de uma imagem, uma consulta útil é:

```text
docker ps -a --filter ancestor=nginx:alpine
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*
