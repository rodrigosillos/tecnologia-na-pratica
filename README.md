# Tecnologia na Prática

Material de apoio da série **Tecnologia na Prática**, de [Rodrigo Sillos](https://github.com/rodrigosillos).

Cada livro tem sua pasta. O leitor baixa o material, prepara o ambiente descrito no capítulo correspondente e acompanha os exercícios.

## Livros disponíveis

| Pasta | Livro | Estado |
| --- | --- | --- |
| [`sql-na-pratica/`](sql-na-pratica/) | **SQL na Prática** — Do primeiro SELECT às consultas profissionais | `1.0.0-rc.1` (candidata; homologação nativa e pgAdmin ainda pendentes) |
| [`docker-na-pratica/`](docker-na-pratica/) | **Docker na Prática** — Containers do zero ao ambiente profissional | `laboratorio-v1.0.0-rc.1` (pré-release; revisão MIT-R01) |
| [`python-na-pratica/`](python-na-pratica/) | **Python na Prática** — Automatize tarefas, integre IA e transforme dados em relatórios | `laboratorio-v1.0.0-rc.1` (pré-release; pasta + ZIP da release) |
| [`jogos-unity-csharp-na-pratica/`](jogos-unity-csharp-na-pratica/) | **Jogos com Unity e C# na Prática** — Crie três jogos 2D completos, da programação à publicação | `laboratorio-v1.0.0-rc.2` (pré-release; passos animados; passos animados; licenças L01; projetos e jogos Windows) |
| [`arquitetura-ia-na-pratica/`](arquitetura-ia-na-pratica/) | **Arquitetura de IA na Prática** / **AI Architecture in Practice** — 18 laboratórios e guias PT/EN | snapshot R04 (material complementar; Python 3.11+) |

## Como obter o laboratório de SQL

1. Abra a pasta [`sql-na-pratica/`](sql-na-pratica/) neste repositório **ou** baixe o ZIP da [release correspondente](https://github.com/rodrigosillos/tecnologia-na-pratica/releases), quando publicada.
2. Leia `sql-na-pratica/README.md` e depois `PREPARACAO-PGADMIN.md`.
3. Use PostgreSQL 18 e pgAdmin no percurso principal. Git e Docker não são obrigatórios.

Prefira a página da **release** com o ZIP versionado como endereço estável no livro. A pasta do repositório acompanha o mesmo conteúdo para consulta.

## Como obter o laboratório de Docker

1. Abra a pasta [`docker-na-pratica/`](docker-na-pratica/) neste repositório **ou** baixe o ZIP dedicado da [release Docker RC1](https://github.com/rodrigosillos/tecnologia-na-pratica/releases/tag/docker-na-pratica-laboratorio-v1.0.0-rc.1), quando publicada.
2. Leia `docker-na-pratica/LEIA_PRIMEIRO.md` (no ZIP: `Docker_na_Pratica_Laboratorios_RC1/LEIA_PRIMEIRO.md`).
3. Siga a etapa do livro correspondente; não inicie todas as pastas de uma vez.

O código e as configurações do laboratório de Docker usam MIT de escopo limitado — veja `docker-na-pratica/LICENSE` e `docker-na-pratica/LICENCA_ESCOPO.md`. Isso não altera as condições do material de SQL.

## Como obter o laboratório de Python

1. Abra a pasta [`python-na-pratica/`](python-na-pratica/) neste repositório **ou** baixe o ZIP da [release Python RC1](https://github.com/rodrigosillos/tecnologia-na-pratica/releases/tag/python-na-pratica-laboratorio-v1.0.0-rc.1).
2. Leia `python-na-pratica/README.md` e `python-na-pratica/GUIA_EXECUCAO.md`.
3. Extraia `cap02` a `cap12` lado a lado em `projetos\python-na-pratica` e siga o capítulo 2 para criar a `.venv` (Python 3.14.7).

Prefira a página da **release** com o ZIP versionado como endereço estável no livro. A pasta do repositório acompanha o mesmo conteúdo para consulta. SHA-256 do ZIP: `b9266cd1b9bc26f21ea804b772bb6591776b9412c2c6deffec5866b54b2e9d74`.

## Como obter os laboratórios de Jogos com Unity e C#

1. Abra [`jogos-unity-csharp-na-pratica/`](jogos-unity-csharp-na-pratica/) ou a [release dos três jogos](https://github.com/rodrigosillos/tecnologia-na-pratica/releases/tag/jogos-unity-csharp-laboratorio-v1.0.0-rc.2).
2. Escolha o pacote de projetos Unity ou os executáveis Windows e leia o README.
3. Use Unity 6000.3.15f1 para estudar os projetos. Abra cada jogo separadamente.

Código original sob MIT; ilustrações autorizadas para uso nos jogos dos leitores, inclusive comercialmente, com crédito. O escopo está nos arquivos de licença desse volume e não altera as condições dos demais livros.

## Como obter os laboratórios de Arquitetura de IA na Prática

1. Abra a pasta [`arquitetura-ia-na-pratica/`](arquitetura-ia-na-pratica/) neste repositório.
2. Leia [`arquitetura-ia-na-pratica/README.txt`](arquitetura-ia-na-pratica/README.txt). O índice lista o guia de cada capítulo em português e em inglês.
3. Abra um terminal dentro da pasta `laboratorio` do capítulo, siga o guia do seu idioma e execute `python -m unittest discover -s .`. Use Python 3.11 ou superior; apenas biblioteca padrão. O capítulo 3 usa HTTP em `127.0.0.1` (loopback).

Há uma implementação compartilhada entre os idiomas, com 18 laboratórios e 36 guias PT/EN. Não são dois cursos duplicados. Este volume segue a política geral de material de apoio deste repositório; não inclui concessão MIT separada (diferente de Docker e Jogos).

## O que este repositório não contém

- Manuscrito do livro (PDF/DOCX)
- Pacotes de homologação editorial (Node.js, verificador, relatórios internos)
- Senhas, bancos de dados ou resultados pessoais de estudo

## Licença de uso do material de apoio

Os arquivos deste repositório existem para acompanhar a leitura do livro correspondente. Não substituem o texto publicado nem o processo editorial de homologação.
