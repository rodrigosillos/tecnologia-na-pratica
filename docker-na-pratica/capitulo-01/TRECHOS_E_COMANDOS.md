# Capítulo 1 — trechos e comandos para consulta

> NÃO EXECUTE ESTE ARQUIVO INTEIRO. Ele contém comandos, trechos parciais, modelos, saídas e falhas deliberadas. Use somente a etapa indicada no livro, com suas pré-condições e verificações.

Fonte: manuscrito consolidado R02. O texto de cada bloco foi preservado, inclusive quebras reais. A numeração abaixo localiza os blocos neste arquivo; não é uma sequência automática de execução.

Marcadores como `ID_OBTIDO` não são valores reais. Comandos de remoção, alterações e falhas controladas exigem a identificação prévia dos recursos. Os parágrafos de contexto são lembretes; não substituem a seção completa do livro.

## Trecho 001 — O problema não começa no Docker

**Contexto do livro:**

> A dificuldade não está apenas em copiar arquivos. Está em reproduzir condições.

> Uma forma tradicional de reduzir esse problema é documentar o ambiente:

```text
Instale o runtime X.
Instale a biblioteca Y.
Configure a variável Z.
Crie a pasta A.
Copie o arquivo B.
Execute o comando C.
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 002 — Container e máquina virtual não são a mesma coisa

**Contexto do livro:**

> Um container representa principalmente um ambiente isolado para processos.

> Uma comparação conceitual simplificada ajuda:

```text
MÁQUINAS VIRTUAIS

Hardware
└── Hipervisor
    ├── Sistema operacional convidado
    │   └── Aplicação A
    └── Sistema operacional convidado
        └── Aplicação B
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 003 — Container e máquina virtual não são a mesma coisa

**Contexto do livro:**

> Em um host Linux executando containers Linux, a ideia é mais próxima de:

```text
CONTAINERS

Hardware
└── Sistema operacional / kernel
    └── Docker Engine
        ├── Container A
        │   └── Processo da aplicação A
        └── Container B
            └── Processo da aplicação B
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 004 — O que torna um ambiente reproduzível

**Contexto do livro:**

> A imagem é a definição. O container é uma instância criada a partir dela.

> Uma analogia útil é pensar em uma classe e seus objetos, sem levar a comparação longe demais:

```text
Imagem
  ↓
Container 1
Container 2
Container 3
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 005 — Imagem não é container parado

**Contexto do livro:**

> A imagem é o pacote usado para criar containers. Ela é formada por camadas imutáveis. Quando um container é criado, recebe também uma camada gravável própria para alterações do seu filesystem durante a execução.

> Mais adiante estudaremos essas camadas em detalhes. Por enquanto, retenha a separação:

```text
IMAGEM = base para criação
CONTAINER = instância criada a partir da imagem
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 006 — Docker Client

**Contexto do livro:**

> O programa docker que você utiliza no terminal funciona como cliente.

> Quando executa:

```text
docker ps
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 007 — Docker Client

**Contexto do livro:**

> ou:

```text
docker run ...
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 008 — Docker Engine

**Contexto do livro:**

> O daemon é o processo de longa duração que recebe solicitações e coordena operações no ambiente Docker.

> Quando o terminal mostra um comando simples como:

```text
docker run hello-world
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 009 — Registry

**Contexto do livro:**

> Quando uma imagem necessária não existe localmente, Docker pode buscá-la em um registry configurado.

> A relação pode ser visualizada assim:

```text
Docker Client
     │
     │ comando/API
     ▼
Docker Engine
     │
     ├── cria e executa containers
     ├── mantém imagens locais
     ├── gerencia redes
     └── gerencia volumes
     │
     │ pull / push de imagens
     ▼
Registry
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 010 — O que realmente acontece em docker run

**Contexto do livro:**

> Leia primeiro esta sequência como uma explicação do funcionamento. A instalação e a execução guiada aparecem nas seções “Preparando o ambiente do livro” e “Pratique agora”; não é necessário antecipar os comandos antes de preparar o ambiente.

> Considere novamente:

```text
docker run hello-world
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 011 — “Rodando” e “existindo” são estados diferentes

**Contexto do livro:**

> Isso permite observar uma diferença importante.

> Execute:

```text
docker ps
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 012 — “Rodando” e “existindo” são estados diferentes

**Contexto do livro:**

> Esse comando mostra, por padrão, containers em execução.

> Agora execute:

```text
docker ps -a
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 013 — “Rodando” e “existindo” são estados diferentes

**Contexto do livro:**

> Se você acabou de executar hello-world, é provável que o container apareça nessa segunda listagem com um estado de saída.

> Portanto:

```text
Container em execução
        ↓
processo principal termina
        ↓
Container parado
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 014 — Preparando o ambiente do livro

**Contexto do livro:**

> No Windows, pode ser PowerShell ou Windows Terminal. No macOS e Linux, utilize seu terminal habitual.

> Execute:

```text
docker version
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 015 — Preparando o ambiente do livro

**Contexto do livro:**

> O comando apresenta informações de versão do cliente e, quando a conexão está funcionando, também do servidor.

> Esse detalhe permite diagnosticar dois problemas diferentes:

```text
"docker" não é reconhecido
        ↓
provável problema de instalação/PATH

cliente aparece, mas servidor não responde
        ↓
Docker Engine/Desktop pode não estar em execução
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 016 — Preparando o ambiente do livro

**Contexto do livro:**

> Agora execute:

```text
docker info
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 017 — Uma regra que vamos usar durante todo o livro

**Contexto do livro:**

> Primeiro descubra em qual camada o problema está.

> Por exemplo:

```text
O comando docker existe?
        ↓
O cliente consegue falar com o Engine?
        ↓
A imagem existe ou pode ser obtida?
        ↓
O container foi criado?
        ↓
O processo iniciou?
        ↓
O processo permaneceu em execução?
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 018 — Pratique agora: seu primeiro container

**Contexto do livro:**

> Neste exercício, docker run poderá obter uma imagem, criar um container e iniciar o processo definido nela. Não usaremos remoção automática; portanto, depois que o processo terminar, esperamos que o container continue registrado em estado parado.

> Com o Docker em execução, rode:

```text
docker run hello-world
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 019 — Pratique agora: seu primeiro container

**Contexto do livro:**

> Leia a saída até o fim.

> Depois execute:

```text
docker ps
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 020 — Pratique agora: seu primeiro container

**Contexto do livro:**

> O container hello-world provavelmente não aparecerá como ativo porque seu processo já terminou.

> Agora execute:

```text
docker ps -a
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 021 — Pratique agora: seu primeiro container

**Contexto do livro:**

> Localize o container criado.

> Por fim, liste as imagens disponíveis:

```text
docker image ls
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 022 — Pratique agora: seu primeiro container

**Contexto do livro:**

> Procure a imagem usada pelo teste.

> Você acabou de observar três objetos/estados diferentes:

```text
imagem disponível localmente
        ↓
container criado a partir dela
        ↓
processo executado e encerrado
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 023 — Leia o estado antes de agir

**Contexto do livro:**

> Suponha que alguém execute:

```text
docker run hello-world
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 024 — Leia o estado antes de agir

**Contexto do livro:**

> veja a mensagem esperada e, em seguida, rode:

```text
docker ps
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 025 — Leia o estado antes de agir

**Contexto do livro:**

> O comando consultado mostra apenas containers em execução. A pergunta feita ao sistema foi incompleta.

> Ao executar:

```text
docker ps -a
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 026 — Achar que docker ps mostra tudo

**Contexto do livro:**

> Por padrão, docker ps mostra containers em execução.

> Para incluir os parados:

```text
docker ps -a
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 027 — Tentar “consertar” tudo reinstalando Docker

**Contexto do livro:**

> Se o cliente existe, mas não consegue falar com o servidor, reinstalar imediatamente pode esconder o diagnóstico real.

> Comece por:

```text
docker version
docker info
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 028 — Para ir além: Docker é cliente-servidor

**Contexto do livro:**

> Isso significa que o terminal é uma interface para uma API — não uma ligação inseparável com um único daemon local.

> Você não precisa configurar acesso remoto agora. A importância dessa ideia é perceber que:

```text
CLI ≠ daemon
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*

## Trecho 029 — Verificação do capítulo

**Contexto do livro:**

> o que você investigaria se docker version mostrasse o cliente, mas não conseguisse consultar o servidor.

> Agora faça uma verificação prática:

```text
docker version
docker info
docker run hello-world
docker ps
docker ps -a
docker image ls
```

*Consulte as condições e a verificação da seção antes de executar ou salvar este trecho.*
