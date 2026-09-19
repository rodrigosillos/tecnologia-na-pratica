# Respostas do capítulo 3

## Exercício 1

O lançamento 7 pertence à conta 2. Essa conta aponta para o participante 1, Ana. Execute `laboratorio/09_exercicios_capitulo_03.sql` para conferir.

A descrição Transporte pode se repetir em várias contas e lançamentos. A identificação do participante depende dos vínculos por chaves. Zero lançamentos para uma conta significa ausência de movimento nesse recorte; consulte `contas` para verificar a existência do cadastro.

## Exercício 2

Considere cada tentativa isolada, IDs novos e os demais campos válidos.

| Tentativa | Resultado | Motivo |
| --- | --- | --- |
| Outra Conta corrente para Ana | Rejeitada | Repetiria `(usuario_id, nome)`. |
| Carteira para Bruno | Aceita | O par participante 2 e nome Carteira ainda não existe. |
| Categoria 2 com tipo receita | Rejeitada | A referência composta exige categoria e tipo compatíveis; Mercado é despesa. |
| Lançamento sem liquidação | Aceita | `data_liquidacao` permite `NULL`. |
| Outro orçamento de Ana para Mercado em maio de 2026 | Rejeitada | Repetiria participante, categoria e mês. |
| Despesa válida acima do orçamento | Aceita | O esquema não bloqueia gastos pela soma mensal. Relatórios mostram o estouro. |

`IDENTITY` gera valores quando omitidos. `PRIMARY KEY` exige identificação única e não nula. A geração automática, sozinha, não garante unicidade.
