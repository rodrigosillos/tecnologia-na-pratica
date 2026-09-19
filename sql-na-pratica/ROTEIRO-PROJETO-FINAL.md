# Roteiro do projeto final de análise de despesas

Use o capítulo 12 e a base fictícia original. As soluções completas estão no livro e nos scripts 36 a 39. Tente escrever sua versão antes de abrir o arquivo de soluções. Nenhum serviço pago, ferramenta de IA ou tabela ampliada é necessário.

## Preparação

Registre banco, usuário, versão do PostgreSQL, cliente e data do ensaio. Confirme as cinco tabelas iniciais e os 12 lançamentos. Use uma instrução por vez, na mesma conexão. Encerre transações anteriores antes de começar.

## Regras a manter

- Maio por competência: início inclusivo 2026-05-01, fim exclusivo 2026-06-01.
- Liquidado no corte: data_liquidacao anterior a 2026-06-01. NULL ou data a partir de junho significa pendência nesse corte.
- Valores positivos em reais; só despesas. Identidade pelo ID, não pelo nome ou pelo valor.
- Usuários sem despesas permanecem nos resumos; listagens e rankings não inventam despesas.
- Uma linha por usuário no fechamento; por despesa no detalhe; por orçamento na tarefa 3; por usuário e categoria no ranking.
- Comparação por competência entre maio e junho; cada mês sem despesas vale zero.
- O modelo não guarda versões históricas. Os relatórios usam as datas atualmente registradas.

## O que entregar

| Tarefa | Evidência esperada |
| --- | --- |
| 1 — Fechamento | SQL, saída e conferência total = liquidado + pendente por usuário. |
| 2 — Pendências | SQL, IDs e soma que reconcilia com a tarefa 1; diagnóstico do filtro IS NULL. |
| 3 — Orçamento | SQL, saldos e reconciliação de despesas com e sem orçamento. |
| 4 — Categorias | SQL, faixas, empates preservados e denominador dos percentuais. |
| 5 — Meses | SQL, zeros explícitos, diferenças e posição do filtro em relação ao LAG. |
| 6 — Correção | Alvo, RETURNING, relatórios antes e durante o ensaio, ROLLBACK e resultados restaurados. |

Para cada tarefa, registre a pergunta, o significado de cada linha, a consulta exata, a saída, os critérios verificados e os limites. Se usou IA, registre a versão da consulta que você efetivamente testou.

## Casos adicionais para investigar

| Caso | Critério a preservar |
| --- | --- |
| Usuário sem conta ou sem despesa no mês | Resumos mantêm uma linha com zero. |
| Receita ou despesa fora do período | Não muda os totais de despesas de maio. |
| Competência em 1º de junho | Não entra em maio. |
| Liquidação em 31 de maio ou 1º de junho | Apenas a primeira está liquidada no corte. |
| Despesa do mês liquidada antes de maio | Conta como liquidada no corte, sem transformar o relatório em fluxo de caixa. |
| Duas categorias empatadas na segunda faixa | Ambas aparecem no ranking. |
| Duas despesas legítimas de mesmo valor | Ambas contribuem para a soma. |
| Orçamento apenas de outro mês | Não cobre a despesa de maio. |
| Gasto exatamente igual ao limite | Saldo zero, sem estouro. |
| Maio vazio e junho com despesas | Maio aparece como zero na comparação. |
| Estado anterior divergente na correção | Zero alterações; investigar sem remover condições. |

Faça experiências adicionais somente em uma cópia fictícia ou em transações controladas, com conferência e desfecho explícitos. Não modifique o banco de trabalho de uma empresa para reproduzir os casos.

## Ordem dos arquivos

36 prepara a sessão. 37 contém as consultas corretas das tarefas 1 a 5. 38 contém o diagnóstico intencional da tarefa 2. 39 reúne a tarefa 6, os relatórios durante a alteração e suas repetições depois do ROLLBACK. O arquivo 39 exige pausas de conferência e nunca deve ser executado inteiro.
