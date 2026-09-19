# Capítulo 1 — Respostas comentadas

## Exercício 1

Os três registros retornados somam 480.00, mas isso não permite afirmar que Ana **pagou** esse valor **nesse mês**. A consulta seleciona despesas registradas e não exige data de liquidação preenchida. O lançamento de Internet, ID 4, está pendente. Também não existe filtro de mês: o ID 2 tem competência em maio e o ID 6 em junho.

O resultado sustenta a afirmação de que os lançamentos selecionados somam 480.00. Para responder quanto foi pago em um mês, precisaríamos definir o mês e filtrar a data de liquidação.

## Exercício 2

```sql
SET search_path TO sql_pratica;

SELECT id, descricao, valor
FROM lancamentos
WHERE conta_id = 1
  AND tipo = 'despesa'
  AND valor >= 180
ORDER BY id;
```

O resultado contém **IDs 2 e 6**, ambos de 180.00. Os dois devem permanecer porque representam lançamentos distintos, mesmo tendo a mesma descrição e o mesmo valor.
