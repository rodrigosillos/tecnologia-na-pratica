# Respostas e conferências — Capítulo 9

Use a base fictícia original: 3 usuários, 4 contas, 7 categorias, 12 lançamentos e 5 orçamentos. Se uma conferência divergir, pare e investigue. Não ajuste filtros para forçar uma alteração sobre dados diferentes.

## Como executar

Abra o Query Tool no banco de estudos com `estudante_sql`. Use a mesma aba e conexão durante cada experiência. Ative Auto commit e desative Auto rollback on error para reproduzir o erro controlado. Trabalhe com um bloco numerado por vez; dentro dele, execute uma instrução até o ponto e vírgula por vez, na ordem. Confira cada saída. Finalize cada transação antes de começar outra.

Os arquivos 26 e 29 encerram todos os ensaios com ROLLBACK. O arquivo 28 provoca dois erros e depois recupera a sessão. O arquivo 27 confirma uma inserção e uma exclusão de limpeza, ambas restritas ao usuário de teste 900001. Não execute esses arquivos inteiros sem as pausas de conferência.

## Resultados dos exemplos

| Etapa | Resultado esperado |
| --- | --- |
| INSERT | Uma linha, conta 2, valor 18.50; ID fornecido por RETURNING. Contagem passa de 12 para 13. |
| ROLLBACK da inserção | Contagem volta a 12. O ID consumido não volta para a sequência. |
| UPDATE | ID 4: data de liquidação passa de NULL para 2026-05-18. ROLLBACK restaura NULL. |
| DELETE | ID 7 e valor 30.00 retornados; contagem 11. ROLLBACK recupera a linha e a contagem 12. |
| COMMIT | Usuário 900001, nome Teste do capitulo 9, persiste depois da confirmação. |
| Limpeza | DELETE pelo ID e nome esperado retorna a única linha de teste; COMMIT confirma a remoção. |
| SAVEPOINT | CHECK falha com 23514; SELECT seguinte falha com 25P02. ROLLBACK TO recupera a sessão e conserva a liquidação anterior ao ponto de retorno. |
| ROLLBACK final | ID 4 volta a valor 120.00 e liquidação NULL. |

Se o ID 900001 já existir na consulta prévia, não execute a inserção nem a limpeza automaticamente. Descubra a origem do registro. Em caso de divergência no retorno da exclusão de limpeza, use ROLLBACK, não COMMIT.

## Exercício 1 — Reajuste específico

A chave de negócio reúne usuário 1, categoria 2 e maio de 2026. O estado inicial esperado é limite 300.00. O reajuste usa `valor_limite * 1.10`, produzindo 330.00 apenas no orçamento de ID 1. Os orçamentos de ID 2 (Ana, junho) e ID 4 (Bruno, maio) permanecem 150.00 e 250.00.

Confira o RETURNING, consulte os demais orçamentos de Mercado e execute ROLLBACK. Não basta filtrar pela categoria: isso atingiria pessoas e meses diferentes. A solução completa, com a consulta prévia, está nos quatro primeiros blocos de `laboratorio/29_exercicios_capitulo_09.sql`.

## Exercício 2 — Zero linhas não é erro

O primeiro UPDATE troca 120.00 por 110.00. O segundo ainda exige 120.00 no WHERE; por isso não encontra a linha. Ele altera zero registros, sem violar uma restrição. A transação permanece válida, com valor 110.00 e liquidação NULL. Confirmá-la gravaria um estado que não cumpre toda a intenção da operação.

Execute ROLLBACK antes de tentar a correção. A solução usa um único UPDATE para atribuir valor 110.00 e liquidação 2026-05-18, exigindo no WHERE o estado inicial 120.00 e NULL. Confira exatamente uma linha e desfaça o ensaio. Os blocos restantes do arquivo 29 incluem tentativa incompleta, diagnóstico, ROLLBACK e solução.

## Conferência final

Ao concluir a limpeza do arquivo 27 e os ROLLBACKs dos outros arquivos, as linhas das cinco tabelas devem coincidir com a base inicial. A sequência de lançamentos pode ter avançado: lacunas de IDs são esperadas. Não a reinicie para eliminar essas lacunas.

RETURNING não é confirmação. RELEASE SAVEPOINT não é COMMIT. Um ROLLBACK posterior não desfaz uma transação já confirmada. Recuperar a sessão após erro não significa que a regra de negócio foi atendida: confira os dados e a quantidade de linhas afetadas.
