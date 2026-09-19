# Respostas do projeto final

Base original, PostgreSQL 18. Período de competência: 2026-05-01 inclusive a 2026-06-01 exclusive. Liquidação no corte: data anterior a 2026-06-01. Data nula ou a partir de junho representa pendência no corte. São classificações pelas datas registradas, não reconstrução de um histórico de versões do banco.

## Tarefa 1

Por usuário, total / liquidado / pendente: Ana (1) 455.00 / 335.00 / 120.00; Bruno (2) 320.00 / 200.00 / 120.00; Carla (3) 0 / 0 / 0. Totais: 775.00 / 535.00 / 240.00. Cada total deve ser igual a liquidado mais pendente.

## Tarefa 2

Pendências: lançamento 4, Ana, 120.00, liquidação NULL; lançamento 10, Bruno, 120.00, liquidação 2026-06-02. A consulta diagnóstica do arquivo 38 usa apenas IS NULL e omite indevidamente o lançamento 10. A solução está no arquivo 37, com OR agrupado e recorte por competência.

## Tarefa 3

Orçamento / limite / realizado / saldo: 1 / 300.00 / 180.00 / 120.00; 3 / 100.00 / 120.00 / -20.00; 4 / 250.00 / 200.00 / 50.00; 5 / 100.00 / 0 / 100.00. O orçamento 2 é de junho e fica fora. Realizado associado a orçamentos: 500.00. Despesas sem orçamento: IDs 3, 5, 7 e 10, total 275.00. Reconciliação: 500.00 + 275.00 = 775.00. Ausência de orçamento não equivale a limite zero.

## Tarefa 4

Usuário / categoria / total / faixa / percentual: 1 / 2 / 180.00 / 1 / 39.56; 1 / 4 / 120.00 / 2 / 26.37; 2 / 2 / 200.00 / 1 / 62.50; 2 / 4 / 120.00 / 2 / 37.50. DENSE_RANK preserva empates. A soma por janela usa todas as categorias antes de filtrar faixa <= 2. Não espere 100% na soma das categorias exibidas quando outras ficam fora do ranking.

## Tarefa 5

Usuário / maio / junho / diferença: 1 / 455.00 / 180.00 / -275.00; 2 / 320.00 / 200.00 / -120.00; 3 / 0 / 0 / 0. Junho totaliza 380.00; diferença geral -395.00. A grade de usuários e meses preserva ausências. LAG vê maio antes de a consulta externa filtrar junho.

## Tarefa 6

O SELECT prévio deve encontrar exatamente o ID 4, conta 1, tipo despesa, valor 120.00 e liquidação nula. Caso contrário, pare e investigue. Execute BEGIN e depois o UPDATE restrito. RETURNING deve mostrar uma linha, id 4, antes 120.00, depois 125.00. Zero linhas afetadas não atende ao ensaio.

Durante a transação, os totais de Ana são 460.00 / 335.00 / 125.00. A pendência do ID 4 é 125.00. O orçamento 3 passa a realizado 125.00 e saldo -25.00. Internet de Ana passa a 125.00 e 27.17%; Mercado permanece em 180.00 e passa a 39.13%. Maio de Ana torna-se 460.00, junho permanece em 180.00 e a diferença é -280.00. Os números de Bruno e Carla permanecem iguais. Total geral de maio: 780.00; liquidado 535.00; pendente 245.00. Realizado dos orçamentos 505.00 mais despesas sem orçamento 275.00 recompõem 780.00.

Depois de conferir, execute ROLLBACK na mesma conexão e repita os relatórios. Todos devem voltar aos resultados anteriores e a contagem deve permanecer em 12. O arquivo 39 inclui todas essas consultas em sequência, para executar uma instrução por vez. Não execute o arquivo inteiro nem substitua ROLLBACK por COMMIT. Se a transação ficar interrompida por erro, execute ROLLBACK separadamente antes de reiniciar.
