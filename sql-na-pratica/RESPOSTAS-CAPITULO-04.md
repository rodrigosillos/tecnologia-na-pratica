# Respostas do capítulo 4

Use a base inicial dos arquivos 01 e 02. Execute as soluções de `laboratorio/12_exercicios_capitulo_04.sql` uma de cada vez, na conexão de estudos.

## Exercício 1

A pergunta inclui todas as despesas das contas 1 e 2 por competência em maio de 2026. Não pede apenas despesas pagas. A solução usa `CASE` para exibir a situação e um intervalo com início incluído e próximo mês excluído.

| Ordem | id | descricao | valor | situacao |
| --- | --- | --- | --- | --- |
| 1 | 2 | Mercado | 180.00 | liquidado |
| 2 | 4 | Internet | 120.00 | pendente |
| 3 | 5 | Farmacia | 80.00 | liquidado |
| 4 | 3 | Transporte | 45.00 | liquidado |
| 5 | 7 | Transporte | 30.00 | liquidado |

Internet permanece porque não existe um filtro que exija liquidação. O id 6 pertence a Ana, mas fica de fora por ter competência em junho. `ORDER BY valor DESC, id ASC` torna explícita a regra para valores iguais.

## Exercício 2

Há dois problemas independentes: `= NULL` não testa ausência, e `BETWEEN` inclui o limite superior, 2026-06-01. A solução usa `IS NULL`, `>= DATE '2026-05-01'` e `< DATE '2026-06-01'`.

| Versão | IDs retornados | Interpretação |
| --- | --- | --- |
| Original incorreta | Nenhum | A comparação com NULL não é verdadeira. |
| Correção apenas de NULL | 4 e 11 | O primeiro dia de junho continua incluído. |
| Correção completa | 4 | Internet, 120.00, pendente em maio por competência. |

As versões erradas executam sem erro SQL. Elas estão identificadas em `laboratorio/11_diagnosticos_capitulo_04.sql` para estudo, não como soluções. O lançamento 11, Mercado de 200.00, pertence a junho e revela a falha na correção parcial.
