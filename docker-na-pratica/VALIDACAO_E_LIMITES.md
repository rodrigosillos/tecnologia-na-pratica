# Validação e limites

## Origem dos arquivos

Este pacote reúne as fontes dos laboratórios dos capítulos 4 a 10, sem reescrever a aplicação, os Dockerfiles, Nginx ou Compose. Nos capítulos 1 a 3, há apoio de consulta aos exercícios, não uma aplicação adicional. Os trechos de código foram extraídos do manuscrito consolidado R02, incluindo a guarda PowerShell do Capítulo 6.

As notas de estado foram ajustadas somente onde mencionavam pendências históricas da preparação ou próximas entregas editoriais. Os nomes, imagens, volumes, portas, formatos e estados esperados foram preservados. Os textos de abertura e os README de distribuição são novos; não alteram o runtime.

## Execução de referência já realizada

O autor executou os quatro blocos no Windows/Docker Desktop com containers Linux/amd64 em 23/09/2026, UTC−03:00. Foram registrados Docker Desktop 4.88.1, Engine 29.7.2, Compose 5.4.0 e PowerShell 5.1.26100.9549. As imagens consultadas retornaram Node.js v24.21.0. Isso descreve a execução observada, não as versões mínimas exigidas nem as versões mais recentes disponíveis.

Os blocos cobriram o conjunto final, as versões intermediárias, a migração manual para Compose, persistência, cópia/restauração, retorno, rede, falhas de configuração, controles e experimentos complementares. Os executores usaram nomes isolados e dados fictícios; não significa que todo comando literal foi digitado em todos os shells. O histórico de uma interrupção e sua retomada não foi reclassificado como uma execução única.

No Windows observado, uma origem de bind mount inexistente foi aceita e passou a existir. A R02 exige verificar pasta e arquivo antes da montagem e depois conferir a origem efetiva e os dados. Uma lista vazia não comprova recuperação de anotações.

## O que não se pode concluir

Não se afirma validação de todas as plataformas, arquiteturas, VPNs ou drivers; recuperação a frio em outro Engine; análise Scout/CVEs; teste de carga, saturação ou rotação prolongada; auditoria completa de segurança; escrita concorrente no JSON. O teste de segredo usou valor fictício e caminhos específicos. O save/load ocorreu no mesmo Engine, com conteúdo já presente.

## Empacotamento RC1

A preparação desta RC1 verificou arquivos, continuidade, código copiado, estrutura e integridade. Nenhuma nova execução em Docker/PowerShell foi realizada nesta etapa de distribuição. A reembalagem não é outra rodada de homologação nem uma liberação automática da publicação.
