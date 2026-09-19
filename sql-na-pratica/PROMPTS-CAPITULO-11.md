# Prompts do capítulo 11

Use somente dados e estrutura fictícios do laboratório. Não envie credenciais nem dados reais. Nenhuma ferramenta ou assinatura de IA é obrigatória. As saídas variam; execute e confira cada consulta candidata antes de aceitá-la.

## Pedido principal

Ambiente: PostgreSQL 18, schema sql_pratica, dados inteiramente fictícios. A sessão usa search_path com esse schema. Quero somente uma consulta de leitura; não execute comandos.

Estrutura relevante: usuarios(id, nome); contas(id, usuario_id); lancamentos(id, conta_id, tipo, valor, data_competencia, data_liquidacao). Os campos id são chaves primárias. contas.usuario_id referencia usuarios.id; lancamentos.conta_id referencia contas.id. Um usuário pode ter várias contas ou nenhuma. Nomes de usuários podem se repetir.

Regras: valor é NUMERIC(12,2), positivo e em reais. tipo distingue receita de despesa. data_competencia é obrigatória; data_liquidacao é opcional. Não há pagamentos parciais neste modelo.

Pergunta: total de despesas de maio de 2026 por competência, por usuário. Quero todos os usuários, inclusive os que não têm despesas no período, com total zero. Cada despesa deve contribuir uma vez. Despesas com o mesmo valor continuam sendo despesas diferentes. A liquidação não muda sua participação neste relatório.

Saída: id, nome e total, uma linha por usuário, ordenada por id. Explique brevemente a escolha dos relacionamentos, filtros e agrupamento. Informe suas suposições e proponha casos de teste. Se faltar uma regra necessária, pergunte antes de completar a consulta. Use apenas os nomes de tabelas e colunas informados.

## Devolutiva baseada no erro observado

A consulta retornou Ana 455.00 e Bruno 320.00, mas omitiu Carla. O relatório exige todos os usuários, incluindo quem não tem despesas. Explique o efeito do WHERE sobre as linhas sem correspondência e proponha uma correção que preserve os filtros de tipo e competência. Não altere o esquema.

## Pedido de casos que possam revelar uma falha

Considere o esquema e a pergunta já informados. Proponha casos válidos em que esta consulta poderia produzir uma resposta incorreta. Inclua duas despesas diferentes com valores iguais, dois usuários de mesmo nome, usuário sem conta e datas nas fronteiras do período. Para cada caso, explique a resposta esperada a partir da regra, sem presumir que o resultado da própria consulta está correto. Não execute nem modifique o banco.

## Revisão da alteração do exercício 2

No laboratório PostgreSQL 18, preciso corrigir somente o lançamento de id 4 e conta_id 1, tipo despesa, de valor 120.00 para 125.00. data_liquidacao deve continuar NULL. Primeiro proponha um SELECT para conferir o alvo. Depois proponha um ensaio com BEGIN, UPDATE que confira o estado anterior, RETURNING e ROLLBACK. O retorno esperado tem exatamente uma linha. Explique como agir se nenhuma linha for afetada. Não execute comandos, não inclua COMMIT e não remova condições para forçar uma alteração. O banco contém apenas dados fictícios.
