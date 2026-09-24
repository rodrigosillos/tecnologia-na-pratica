# Leia primeiro

## Extração do ZIP dedicado

Se você baixou o anexo `docker-na-pratica-laboratorio-v1.0.0-rc.1.zip`, a pasta raiz após a extração é `Docker_na_Pratica_Laboratorios_RC1/`. Continue a leitura neste arquivo, dentro dessa pasta. Os arquivos ocultos (`.env`, `.dockerignore`, `.gitignore`) fazem parte dos exemplos.

## Execute a etapa do livro, não todas as pastas

Extraia o ZIP em uma pasta nova. No Windows, prefira um caminho curto e sem vírgulas, como `C:\TNP\Docker`. Confira extensões e arquivos ocultos. Os arquivos `.env`, `.dockerignore` e `.gitignore` fazem parte dos exemplos; não descarte arquivos apenas porque começam com ponto.

A partir do capítulo 4, use os arquivos da pasta correspondente à etapa estudada. Capítulos 4–6 trabalham dentro de `laboratorio/catalogo-estudos`; capítulos 7–10 operam um nível acima, em `laboratorio`. Cada README informa o local. A pasta geral deste ZIP não é um contexto de build.

As fontes iniciais do capítulo 4 mostram Edição 1. A referência de Edição 2 é somente apoio ao experimento. O exercício 1.2 deve ser encerrado e seus temas restaurados antes do capítulo 5. A versão final 1.6 não substitui essas etapas.

## Pré-condições

O livro usa containers Linux e um Docker Engine local acessível pela CLI. Docker Compose e BuildKit aparecem quando o capítulo os introduz. No Windows, a execução de referência utilizou PowerShell e contexto desktop-linux. Docker Desktop deve estar ativo. Não é necessário instalar Node.js, Nginx ou Python no host para o percurso Docker.

Internet é necessária para obter as imagens base que ainda não estão locais. Este ZIP contém fontes, não um cache de imagens. Tags de base podem passar a apontar para outro conteúdo; registre os IDs e a plataforma efetivamente usados. As versões do ambiente de referência não são requisitos de instalação exata.

## Não confunda nova pasta com novos recursos

As pastas não isolam containers, projetos, redes ou volumes. Os comandos preservam os nomes didáticos do livro, incluindo `tnp-catalogo`, `catalogo-web` e `tnp-catalogo-dados`. Confira existência, contexto e propriedade antes de operar. Se pertencerem a outro trabalho, não os remova: use um ambiente separado ou nomes conscientemente ajustados em toda a sequência.

O volume externo dos capítulos finais deve conter as anotações produzidas anteriormente. Sua ausência exige investigar contexto, nome e recuperação. Não crie um volume vazio para esconder uma retomada incorreta. O volume de aceite do capítulo 10 é outro recurso, criado explicitamente somente na etapa de teste.

## Fontes, dados e exemplos

Os arquivos `temas.json` são conteúdo inicial empacotado. Os arquivos `dados-host/anotacoes.json` incluídos a partir do capítulo 6 contêm apenas a frase fictícia do livro; não são backups das suas anotações. O programa cria seu arquivo inicial vazio durante o build, conforme o Dockerfile. Preserve seus volumes e backups fora desta distribuição.

Os `.env` fornecidos contêm apenas configurações didáticas. Não acrescente senhas nem substitua o exemplo de segredo fictício por uma credencial real. O arquivo `segredo-ficticio.txt` mantém o nome usado no capítulo; o valor não concede acesso a serviço algum.

Alguns `.gitignore` dos exemplos ignoram os `.env` de trabalho. Ao preparar um repositório, não presuma que `git add` incluiu todos os arquivos do ZIP. A release anexada deve ser conferida pelo manifesto e conter os modelos de ambiente listados.

## Comandos e alterações com efeito destrutivo

Os arquivos `TRECHOS_E_COMANDOS.md` não são scripts. Preservam alternativas, saídas, trechos parciais, modelos e operações que devem falhar. Consulte a seção indicada, substitua os marcadores apenas com valores reais e execute uma etapa por vez. Não cole um Dockerfile inteiro no terminal.

Antes de remover ou recriar, confirme o objeto, a necessidade e a forma de preservar os dados. Não use limpeza global, `prune`, remoção forçada ou ampliação indiscriminada de permissões para contornar resultados diferentes. O pacote não inclui um executor automático nem um script de limpeza.

## Evidência e verificação

Compreender → observar → decidir → executar → verificar. Ao concluir, compare o que realmente existe com o estado esperado da etapa. `healthy` não comprova todas as rotas nem o conteúdo dos dados; confira o caminho que o livro pede. Preserve registros relevantes sem publicar credenciais ou anotações pessoais.
