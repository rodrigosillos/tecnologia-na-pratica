# Respostas — Capítulo 6

Base inicial do livro; despesas por competência de maio de 2026.

### Exercício 1

```sql
SELECT u.id,
       u.nome AS usuario,
       cat.nome AS categoria,
       SUM(l.valor) AS total
FROM lancamentos AS l
JOIN contas AS c ON c.id = l.conta_id
JOIN usuarios AS u ON u.id = c.usuario_id
JOIN categorias AS cat
    ON cat.id = l.categoria_id
   AND cat.tipo = l.tipo
WHERE l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id, u.nome, cat.id, cat.nome
HAVING SUM(l.valor) >= 100
ORDER BY u.id, cat.id;
```

| id | usuario | categoria | total |
| --- | --- | --- | --- |
| 1 | Ana | Mercado | 180.00 |
| 1 | Ana | Internet | 120.00 |
| 2 | Bruno | Mercado | 200.00 |
| 2 | Bruno | Internet | 120.00 |

A linha representa um par entre usuário e categoria. Agrupar somente por categoria juntaria gastos de pessoas diferentes. O WHERE seleciona o período e o tipo de lançamento; HAVING aplica o mínimo ao total de cada par. Os IDs no agrupamento evitam confundir pessoas que tenham o mesmo nome.

### Exercício 2

```sql
SELECT u.id,
       u.nome AS usuario,
       COUNT(l.id) FILTER (
           WHERE l.data_liquidacao IS NULL
       ) AS pendencias
FROM usuarios AS u
LEFT JOIN contas AS c ON c.usuario_id = u.id
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
   AND l.tipo = 'despesa'
   AND l.data_competencia >= DATE '2026-05-01'
   AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id, u.nome
ORDER BY u.id;
```

| id | usuario | pendencias |
| --- | --- | --- |
| 1 | Ana | 1 |
| 2 | Bruno | 0 |
| 3 | Carla | 0 |

Na consulta incorreta, a linha preservada para Carla tem l.data_liquidacao nula, passa pelo FILTER e é contada por COUNT(*). O problema não está na condição de pendência de um lançamento real; está em contar uma linha que não contém lançamento.

COUNT(l.id) conta apenas correspondências reais, nas quais o identificador é preenchido. O FILTER continua selecionando lançamentos sem liquidação, e Carla continua presente com zero. Se ela tivesse várias contas vazias, a correção ainda funcionaria.

