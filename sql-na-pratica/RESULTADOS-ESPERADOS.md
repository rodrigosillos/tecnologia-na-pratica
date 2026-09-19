# Resultados esperados


Após a carga: usuários 3, contas 4, categorias 7, lançamentos 12 e orçamentos 5. A conferência do recorte inicial soma 480.00 e encontra uma conta sem movimento.

No capítulo 3: lançamento 7 na conta 2, pertencente a Ana; conta 4 sem lançamentos; valor convertido 12.35; lançamento 10 com competência em 2026-05-16 e liquidação em 2026-06-02; pendências nos IDs 4 e 11; limites de Mercado para Ana de 300.00 em maio e 150.00 em junho de 2026.

Datas podem aparecer com outra formatação no cliente. Os arquivos usam UTF-8 e ponto decimal SQL; a apresentação em português não altera os valores armazenados.

No capítulo 4, as três maiores despesas de Ana em maio por competência são IDs 2, 4 e 5, com valores 180.00, 120.00 e 80.00. O exercício 1 devolve IDs 2, 4, 5, 3 e 7; o exercício 2 corrigido devolve apenas o id 4. A correção parcial inclui indevidamente o id 11, de junho.

No capítulo 5, a listagem das despesas de maio com usuário e categoria contém os IDs 2, 3, 4, 5, 7, 9 e 10. A conta 4, de Carla, é a única sem qualquer movimento na base inicial. O relatório que preserva todas as contas e associa despesas de maio tem oito linhas, incluindo a conta 4 com campos do lançamento nulos. O exercício 2 corrigido associa o lançamento 2 ao limite de Ana, 300.00, e o lançamento 9 ao de Bruno, 250.00.

No capítulo 6, sete despesas de maio somam 775.00, com média por despesa de 110.71. Os totais por categoria são Mercado 380.00, Internet 240.00, Saude 80.00 e Transporte 75.00. Por usuário: Ana 455.00, Bruno 320.00 e Carla 0. O relatório de orçamento ultrapassado aponta Internet de Ana: total 120.00 e limite 100.00. No exercício 2, a contagem correta de pendências é Ana 1, Bruno 0 e Carla 0. Uma data de liquidação preenchida não significa necessariamente pagamento ocorrido em maio.

No capítulo 7, as despesas acima da média de maio são IDs 2, 4, 9 e 10. `EXISTS` encontra Ana com pendência; `NOT EXISTS` encontra Carla sem despesas. A CTE preserva os totais 455.00, 320.00 e 0 por usuário. O exercício 1 retorna IDs 3, 5, 7 e 10, totalizando 275.00 sem orçamento. No exercício 2, `EXISTS` com `COUNT(*)` seleciona incorretamente todos os usuários; a correção seleciona apenas Ana.

No capítulo 8, os totais de cada despesa de maio são 455.00 para Ana e 320.00 para Bruno. Os IDs das duas maiores despesas de cada pessoa são 2, 4, 9 e 10. Os últimos acumulados cronológicos são 455.00 e 320.00. Na comparação mensal, junho totaliza 180.00 para Ana e 200.00 para Bruno, com diferenças de -275.00 e -120.00 para maio. O exercício 1 preserva quatro despesas nas três maiores faixas de valor: IDs 9, 2, 4 e 10. O exercício 2 corrigido filtra as despesas maiores ou iguais a 100 sem reduzir o total de maio.

No capítulo 9, a inserção de transporte passa a contagem de lançamentos de 12 para 13; ROLLBACK a restaura. A exclusão do ID 7 passa a contagem para 11 e também é desfeita. No ensaio de liquidação, o ID 4 muda de data nula para 2026-05-18; ao encerrar, volta a NULL. O exercício 1 reajusta apenas o orçamento 1, de 300.00 para 330.00, e depois desfaz. No exercício 2, o segundo UPDATE da tentativa incompleta altera zero linhas: a solução atribui valor e data no mesmo comando, seguida de ROLLBACK. Ao concluir também a limpeza do arquivo 27, as linhas das cinco tabelas coincidem com a base inicial. A sequência de IDs pode avançar mesmo com ROLLBACK; não a reinicie para eliminar lacunas.

No capítulo 10, a carga contém 100000 despesas, 500 contas e 200 dias por conta. O recorte da conta 42 em maio de 2026 retorna 31 despesas, IDs 8321 a 8351, total 3379.00, antes e depois do índice. Na execução de referência, a leitura sem índice descarta 99969 linhas. O filtro com EXTRACT encontra 200 candidatas pelo índice da conta e descarta 169 pela data; sua correção usa conta e intervalo no índice. O BETWEEN incorreto inclui 1º de junho, produzindo quantidade 32 e total 3500.00. A correção restaura 31 e 3379.00. Esses nós de plano descrevem o ambiente de referência, não uma saída obrigatória em qualquer computador. Ao concluir, a base original continua com 12 lançamentos, sem alteração em suas tabelas, índices ou sequências.

No capítulo 11, a candidata inicial retorna Ana 455.00 e Bruno 320.00, mas omite Carla. A correção inclui Carla com zero e mantém o total geral 775.00, correspondente a sete despesas. SUM DISTINCT coincide com a resposta na base inicial, mas o contraexemplo de duas despesas de 180.00 produz soma comum 360.00 e soma distinta 180.00. O filtro de categoria do exercício 2 alcança IDs 4 e 10; o UPDATE revisado altera somente o ID 4 para 125.00 e mantém sua liquidação nula. Após ROLLBACK, os dois valores continuam em 120.00 e o conjunto permanece com 12 lançamentos.

No capítulo 12, o fechamento de maio totaliza 775.00, dos quais 535.00 estão liquidados e 240.00 pendentes no corte. As pendências são IDs 4 e 10; o ID 10, liquidado em 2 de junho, continua pendente no fechamento de maio. Os gastos associados a orçamentos somam 500.00 e os quatro sem orçamento somam 275.00. O orçamento 3 tem saldo -20.00. O ranking apresenta Mercado e Internet para Ana e Bruno. Junho totaliza 380.00 e a diferença junho menos maio é -395.00.

Durante a correção controlada, o total de maio passa a 780.00 e a pendência a 245.00; o liquidado continua 535.00. O orçamento 3 passa a saldo -25.00. Os demais relatórios também refletem a mudança de 5.00. Após ROLLBACK, os seis relatórios voltam aos resultados originais e a base mantém 12 lançamentos.


As soluções comentadas de cada atividade estão nos arquivos RESPOSTAS e no livro.
