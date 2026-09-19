# Capítulo 7 — Respostas do laboratório

Use a base inicial, com despesas pela competência de maio de 2026. Os valores usam ponto decimal, como no resultado SQL. As soluções executáveis estão em `laboratorio/22_exercicios_capitulo_07.sql`.

## Exercício 1 — Despesas sem orçamento

A CTE mantém uma linha por despesa. `NOT EXISTS` verifica a ausência de orçamento para a combinação de usuário, categoria e mês.

| id | usuario_id | categoria_id | valor |
| --- | --- | --- | --- |
| 3 | 1 | 3 | 45.00 |
| 5 | 1 | 5 | 80.00 |
| 7 | 1 | 3 | 30.00 |
| 10 | 2 | 4 | 120.00 |

São quatro despesas, com total de 275.00: 155.00 de Ana e 120.00 de Bruno. Internet de Ana não aparece: existe orçamento, embora o limite seja menor que o gasto. Ausência de orçamento e ultrapassagem de limite são perguntas diferentes.

## Exercício 2 — EXISTS com COUNT

A consulta incorreta devolve Ana, Bruno e Carla. Sem `GROUP BY`, `COUNT(*)` produz uma linha mesmo quando a contagem é zero. `EXISTS` testa a existência dessa linha, não se seu conteúdo é maior que zero.

A correção usa `SELECT 1`, mantendo a correlação por usuário e os filtros de tipo, mês e liquidação. O resultado é somente Ana, id 1. A pendência de Bruno pertence a junho; sua despesa de Internet de maio já tem liquidação preenchida.

## Outros resultados para conferir

- Despesas acima da média de maio: IDs 2, 4, 9 e 10. A comparação usa a média sem arredondamento, 775 dividido por 7.
- Resumo com total maior que 400: Ana, 455.00.
- Usuários sem despesas em maio: Carla, id 3.
- `99 NOT IN (1, NULL)` resulta em `NULL`; `1 NOT IN (1, NULL)` resulta em falso.
- Totais preservando todos os usuários: Ana 455.00, Bruno 320.00 e Carla 0.
- Orçamento excedido: Internet de Ana, total 120.00 e limite 100.00.
- A view contém despesas de todos os meses. A consulta de maio retorna usuário 1 com 455.00 e usuário 2 com 320.00.

Crie a view uma única vez com `laboratorio/21_view_capitulo_07.sql`. Para consultá-la novamente, selecione somente o `SELECT`. A definição fica no banco; as CTEs dos outros exemplos valem apenas dentro de cada instrução.
