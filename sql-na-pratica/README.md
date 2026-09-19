# SQL na Prática — Laboratório

Material de apoio de **SQL na Prática — Do primeiro SELECT às consultas profissionais**, de **Rodrigo Sillos**, série **Tecnologia na Prática**.

**Versão 1.0.0-rc.1 · 19/09/2026 · candidata à publicação.** O pacote cobre os 12 capítulos e o guia rápido. A homologação no servidor nativo e na interface do pgAdmin ainda está pendente; veja VERSAO.md.

## Comece por aqui

1. Use esta pasta completa (clone do repositório ou ZIP extraído da release). Não separe apenas a pasta `laboratorio/`.
2. Leia **PREPARACAO-PGADMIN.md** e siga o capítulo 2 para preparar PostgreSQL 18, pgAdmin e seu banco de estudos.
3. Execute `laboratorio/00_verificar_conexao.sql`, uma instrução por vez. Confira banco, usuário, versão e UTF8.
4. Em banco vazio pertencente a `estudante_sql`, execute **01_estrutura.sql inteiro** e depois **02_dados.sql inteiro, uma única vez**.
5. Execute `04_conferencias.sql`, uma instrução por vez. As contagens devem ser 3 usuários, 4 contas, 7 categorias, 12 lançamentos e 5 orçamentos.
6. Use o **MAPA-DO-LABORATORIO.md** para localizar os arquivos do capítulo que está estudando.

Você precisa apenas de PostgreSQL e pgAdmin para o percurso principal. Git, Docker, Node.js e serviços de IA não são requisitos para o leitor. Os dados são fictícios; não conecte o laboratório a um banco de trabalho.

## Encontre o que precisa

| Arquivo ou pasta | Uso |
| --- | --- |
| PREPARACAO-PGADMIN.md | Preparar usuário, banco, conexão e primeira consulta. |
| MAPA-DO-LABORATORIO.md | Encontrar a faixa de arquivos de cada capítulo. |
| ROTEIRO-DE-EXECUCAO.md | Conferir ordem, pausas, transações e dependências. |
| laboratorio/ | 42 arquivos SQL, numerados de 00 a 41. |
| RESPOSTAS-CAPITULO-01.md a RESPOSTAS-CAPITULO-12.md | Soluções e resultados comentados por capítulo. |
| RESULTADOS-ESPERADOS.md | Conferências gerais do percurso. |
| CONFERENCIAS-GUIA-RAPIDO.md | Resultados dos blocos do guia. |
| SOLUCAO-DE-PROBLEMAS.md | Diagnosticar conexão, carga e erros SQL. |
| PROMPTS-CAPITULO-11.md | Pedidos completos para a atividade opcional com IA. |
| ROTEIRO-PROJETO-FINAL.md e arquivos REGISTRO | Registrar consultas, resultados e decisões. |
| apoio/ | Alternativa Docker opcional, ainda sem execução homologada. |
| VERSAO.md | Histórico, validações e limites desta versão. |
| MANIFESTO-SHA256.txt | Conferência de integridade dos arquivos. |

## Como executar sem perder o contexto

Nos exemplos, selecione uma instrução completa até o ponto e vírgula e confira a saída antes da próxima. **Não execute todos os arquivos em um laço**: alguns contêm pausas, erros intencionais ou decisões antes de COMMIT.

Mantenha **Auto commit ligado**. Nos erros controlados dos capítulos 3 e 9, use **Auto rollback on error desligado**, para recuperar a transação pelo comando previsto no roteiro. Os arquivos 01 e 02 já contêm suas próprias transações.

Nos capítulos 9 e 10, e nas experiências de alteração dos capítulos 11, 12 e do guia, mantenha a mesma aba e conexão. `RETURNING` mostra o resultado da alteração; não a confirma. Uma segunda execução de carga não é um modo de corrigir uma consulta.

## Antes de conferir as soluções

Descreva a pergunta, tente prever a resposta e execute sua consulta. Compare IDs, quantidade de linhas e valores. Uma consulta pode executar sem erro e responder à pergunta errada. Os arquivos de diagnóstico foram incluídos para praticar essa distinção.

Este pacote contém o apoio de execução. As explicações completas dos capítulos, o guia e o glossário estão no livro.
