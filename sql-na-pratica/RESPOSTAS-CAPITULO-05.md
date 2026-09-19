# Respostas do capítulo 5

SQL na Prática — Relacionando tabelas sem distorcer resultados.

Use a base inicial e a preparação de sessão dos arquivos 13 a 15. As soluções abaixo também estão no capítulo. No exercício 1, a pergunta é quais contas não tiveram qualquer movimento por competência em maio de 2026. No exercício 2, é preciso corrigir a associação das despesas 2 e 9 aos orçamentos de seus respectivos titulares para maio.

### Exercício 1

```sql
SELECT c.id AS conta,
       u.nome AS usuario
FROM contas AS c
INNER JOIN usuarios AS u
    ON u.id = c.usuario_id
LEFT JOIN lancamentos AS l
    ON l.conta_id = c.id
   AND l.data_competencia >= DATE '2026-05-01'
   AND l.data_competencia < DATE '2026-06-01'
WHERE l.id IS NULL
ORDER BY c.id;
```

A base inicial devolve conta 4, usuário Carla. O intervalo no ON limita as correspondências aos movimentos de maio. Uma conta com movimentos somente fora desse mês fica sem par no recorte e passa pelo teste l.id IS NULL.

Não filtramos l.tipo, pois o exercício considera qualquer movimento. A conta 2 não aparece: ela tem a despesa 7 e a receita 12 em maio. O campo data_liquidacao não participa da decisão, já que pendência e ausência são situações diferentes.

### Exercício 2

```sql
SELECT l.id,
       l.valor,
       o.usuario_id AS titular,
       o.valor_limite AS limite
FROM lancamentos AS l
INNER JOIN contas AS c
    ON c.id = l.conta_id
LEFT JOIN orcamentos AS o
    ON o.categoria_id = l.categoria_id
   AND o.usuario_id = c.usuario_id
   AND o.mes_referencia = DATE '2026-05-01'
WHERE l.id IN (2, 9)
  AND l.tipo = 'despesa'
  AND l.data_competencia >= DATE '2026-05-01'
  AND l.data_competencia < DATE '2026-06-01'
ORDER BY l.id, o.usuario_id;
```

| id | valor | titular | limite |
| --- | --- | --- | --- |
| 2 | 180.00 | 1 | 300.00 |
| 9 | 200.00 | 2 | 250.00 |

Faltava exigir que o titular do orçamento fosse o titular da conta. Sem essa condição, cada despesa encontrava tanto o limite de Ana quanto o de Bruno para a mesma categoria e mês.

Mantivemos a comparação no ON do LEFT JOIN. Se não houver orçamento para uma despesa, ela continua na saída, com titular e limite nulos. O alias titular deste exemplo identifica o titular do orçamento encontrado; o titular da conta continua conhecido por c.usuario_id.

DISTINCT sobre id e valor esconderia os pares excedentes, pois deixaria de exibir o lado do orçamento. A consulta voltaria a mostrar duas linhas, mas continuaria sem associar corretamente os limites 300.00 e 250.00. Corrigir o relacionamento exige completar a condição e conferir os campos relacionados.

Confira se consegue explicar as repetições da conta 2, a diferença entre ausência de movimento e pendência e o risco de somar um limite mensal em cada despesa. No capítulo 6, transformaremos movimentos em relatórios com totais confiáveis.
