# Conferências do guia rápido

Use a base original, com 12 lançamentos, e siga o guia no livro. O arquivo 40 reúne as leituras; o 41 contém a alteração controlada. Execute uma instrução por vez, na mesma conexão. Não execute o arquivo 41 inteiro nem troque seu ROLLBACK por COMMIT.

| Bloco | Resultado esperado na base original |
| --- | --- |
| preparacao | Usuário estudante_sql; banco de estudos sql_na_pratica; 12 lançamentos. |
| filtro | IDs 9, 2, 4, nessa ordem; valores 200.00, 180.00, 120.00. |
| sem_liquidacao | ID 4, valor 120.00. |
| pendencias_corte | IDs 4 e 10, ambos 120.00; total 240.00. |
| classificacao | ID 2 Liquidada no corte; IDs 4 e 10 Pendente no corte. |
| resumo | Usuário 1: 5 despesas, 455.00; usuário 2: 2, 320.00; usuário 3: 0, 0. |
| grupos | Categoria 2: 380.00; categoria 4: 240.00. |
| ausencia | ID 3, Carla. |
| cte | Usuário 1, total 455.00. |
| acumulado | IDs 2, 3, 7, 4, 5; acumulados 180.00, 225.00, 255.00, 375.00, 455.00. |
| plano | Plano da leitura de sete despesas; formato, tempos e operações podem variar. |
| alvo | Uma linha: ID 4, conta 1, 120.00 e data nula. |
| alteracao | Uma linha afetada: ID 4, antes 120.00 e depois 125.00. |
| desfazer | ID 4 novamente com 120.00 e data nula; 12 lançamentos ao final. |

Pendência no corte inclui a despesa liquidada em 2 de junho. A consulta por IS NULL faz uma pergunta diferente e não é um substituto para o fechamento. O total do resumo é 775.00; alterar temporariamente ID 4 para 125.00 muda o total para 780.00, e ROLLBACK restaura os valores originais.

Se a prévia divergir, não execute a alteração. Se RETURNING não mostrar exatamente uma linha, desfaça na mesma conexão e investigue. Se a transação entrar em erro, execute ROLLBACK separadamente. Autocommit não impede uma transação explícita iniciada por BEGIN.
