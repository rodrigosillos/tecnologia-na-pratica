# Docker na Prática — laboratórios do leitor

**Containers do zero ao ambiente profissional**  
Rodrigo Sillos · Série Tecnologia na Prática  
**RC1 — pacote candidato para a primeira edição; base editorial R02; revisão de distribuição MIT-R01.**

Comece por [LEIA_PRIMEIRO.md](LEIA_PRIMEIRO.md) e pelo [mapa dos capítulos](MAPA_DOS_CAPITULOS.md). As dez pastas acompanham a progressão do livro; não são dez aplicações independentes para iniciar simultaneamente.

## Localize sua etapa

| Etapa | Material |
|---|---|
| 1–3 | Imagens oficiais, observação e trechos dos exercícios; sem aplicação própria. |
| 4 | Primeiro Dockerfile, Edição 1 e referência de Edição 2. |
| 5 | Configuração externa, imagem 1.3. |
| 6 | Persistência, imagem 1.4 e guarda de origem de bind mount da R02. |
| 7 | Catálogo preservado e entrada Nginx 1.0. |
| 8 | Migração para Docker Compose mantendo o volume original. |
| 9 | Multi-stage, imagem 1.5 e controles de execução. |
| 10 | Imagem 1.6, aceite separado e retorno 1.5. |

Consulte também [Guia rápido: trechos](guia-rapido/TRECHOS_E_COMANDOS.md) e [Referências por capítulo](REFERENCIAS.md).

## O que este arquivo distribui

Fontes, Dockerfiles, configurações, exemplos fictícios e instruções. **Não inclui** o ebook, as imagens Docker já construídas, resultados privados, logs de homologação, executores internos ou dados reais. Não é um instalador de um clique: os comandos pertencem às situações e pré-condições do livro.

O manifesto identifica os bytes desta distribuição. Ele não prova autoria, segurança ou funcionamento em qualquer ambiente. Leia [VALIDACAO_E_LIMITES.md](VALIDACAO_E_LIMITES.md) para distinguir conservação dos arquivos e execução de referência.

## Como obter o pacote

- Nesta pasta do repositório: [docker-na-pratica/](.)  
- Ou o ZIP dedicado da release (anexo editorial, não o “Source code” automático do GitHub):  
  [docker-na-pratica-laboratorio-v1.0.0-rc.1.zip](https://github.com/rodrigosillos/tecnologia-na-pratica/releases/download/docker-na-pratica-laboratorio-v1.0.0-rc.1/docker-na-pratica-laboratorio-v1.0.0-rc.1.zip)

Após extrair o ZIP, a pasta raiz é `Docker_na_Pratica_Laboratorios_RC1/`. Abra primeiro `Docker_na_Pratica_Laboratorios_RC1/LEIA_PRIMEIRO.md`.

Não use `releases/latest` neste repositório: há mais de um livro e a release “mais recente” pode ser de outro material.

## Licença do código e das configurações

O código e as configurações originais do laboratório de Docker estão sob a [licença MIT](LICENSE). O escopo exato — lista de caminhos e limites — está em [LICENCA_ESCOPO.md](LICENCA_ESCOPO.md).

Esta concessão **não** licencia o texto do livro, a capa, a identidade da série, o material de SQL nem componentes de terceiros (Docker, Node.js, Nginx, imagens base). Consulte o escopo antes de redistribuir.
