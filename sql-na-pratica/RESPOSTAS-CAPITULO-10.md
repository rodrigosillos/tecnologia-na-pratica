# Respostas e conferências — Capítulo 10

Use a mesma aba e conexão do Query Tool durante toda a experiência. Ative o autocommit, encerre transações anteriores e execute uma instrução por vez, selecionando até o ponto e vírgula. Não execute todos os arquivos em um laço: você precisa observar os planos antes de alterar a experiência.

## Sequência

1. `30_capitulo_10_carga.sql`: cria uma tabela temporária com 100 mil despesas, 500 contas e 200 dias; coleta estatísticas. O DROP inicial reinicia essa tabela e seus índices na sessão.
2. `31_capitulo_10_planos.sql`: confere a consulta, observa os planos antes do índice, cria o índice e compara a mesma consulta depois. O CREATE INDEX deve ser executado uma vez.
3. `32_exercicios_capitulo_10.sql`: compara filtro por expressão com intervalo e diagnostica o limite superior inclusivo incorreto.
4. `33_capitulo_10_limpeza.sql`: remove a tabela temporária, incluindo seu índice, e confere os 12 lançamentos originais.

Se a sessão terminar, a tabela temporária desaparece. Prepare a carga novamente na nova conexão. Não execute a carga de novo no meio da comparação, porque ela remove o índice anterior. As contas sintéticas de 1 a 500 não correspondem às contas do modelo original.

## Resultados que devem coincidir

| Conferência | Esperado |
| --- | --- |
| Carga | 100000 linhas e 500 contas; 200 dias de 2026-01-01 a 2026-07-19. |
| Consulta principal | Conta 42, maio de 2026: 31 linhas, IDs 8321 a 8351. |
| Soma da consulta principal | 3379.00, antes e depois do índice. |
| Cinco primeiros valores | IDs 8321 a 8325: 121.00, 122.00, 123.00, 124.00 e 94.00. |
| Erro com BETWEEN | 32 linhas e 3500.00; inclui indevidamente 8352, de 2026-06-01, no valor 121.00. |
| Base original | 12 lançamentos; as cinco tabelas permanecem com suas linhas originais. |

## Exercício 1

A consulta com EXTRACT filtra ano e mês e, por isso, mantém a resposta correta. Na execução de referência, Index Cond usou somente conta_id = 42, encontrando as 200 linhas dessa conta. O Filter de datas descartou 169. A condição direta por intervalo permitiu restringir o índice a conta e datas, encontrando 31 linhas. A solução está no bloco ex1_solucao do arquivo 32.

Não conclua que qualquer função sempre impede qualquer uso de índice: o índice foi utilizado para a conta. Observe quais condições restringem a busca. Estimativas e tipos de plano podem variar com estatísticas, configuração e ambiente.

## Exercício 2

BETWEEN inclui ambos os extremos. Maio deve incluir 2026-05-01 e excluir 2026-06-01. A correção usa >= no limite inferior e < no superior, restaurando quantidade 31 e total 3379.00. A solução e seu EXPLAIN estão nos blocos finais do arquivo 32.

O Aggregate desse resumo devolve uma linha, enquanto a leitura de despesas que o alimenta devolve 31. Não confunda essas quantidades com a quantidade de linhas examinadas antes dos filtros. Um índice não corrige uma fronteira de datas errada.

## Como avaliar a comparação

O capítulo registra observações de PostgreSQL 18.3 incorporado ao PGlite 0.5.8. Esse ambiente não é um benchmark de instalação nativa. Não use seus milissegundos como meta. Compare a mesma consulta e os mesmos dados, registre o plano, preserve o resultado e repita as execuções sem misturar a primeira execução com as seguintes aquecidas.

Use REGISTRO-COMPARACAO-CAPITULO-10.md para suas observações. Em uma tabela temporária, local identifica buffers de tabela/índice temporários; temp read/written refere-se a arquivos temporários de trabalho. Contagens dos nós superiores incluem seus filhos; não some todos os nós. ANALYZE tabela coleta estatísticas; EXPLAIN ANALYZE executa a instrução. Todos os comandos medidos aqui são SELECTs.
