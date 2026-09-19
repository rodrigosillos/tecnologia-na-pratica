# Respostas do capítulo 11

## Consulta principal

A candidata incompleta retorna apenas Ana 455.00 e Bruno 320.00. A soma 775.00 está certa, mas falta Carla. Os filtros de lancamentos no WHERE eliminam a linha sem correspondência. Mova-os para o ON do LEFT JOIN com lancamentos. A solução preserva IDs 1, 2 e 3, com totais 455.00, 320.00 e 0. A listagem de conferência contém IDs 2, 3, 4, 5, 7, 9 e 10; competência define o mês, independentemente da liquidação.

## Exercício 1

SUM(DISTINCT valor) considera valores distintos, não IDs distintos. Na base original, a candidata coincide com a resposta correta porque cada usuário tem valores diferentes entre suas despesas de maio. O SELECT com VALUES cria somente duas linhas de consulta, com IDs diferentes e valor 180.00. Resultado: quantidade 2, total 360.00, total_distinto 180.00. Não insere dados. A solução usa SUM(l.valor), preservando as condições e o agrupamento por id e nome. Veja a instrução completa no arquivo 35.

## Exercício 2

categoria_id = 4 encontra IDs 4 e 10; seria amplo demais para corrigir somente o lançamento 4. O SELECT restrito encontra ID 4, conta 1, valor 120.00 e liquidação nula. Se não encontrar, pare e investigue.

Na mesma conexão, execute BEGIN, depois o UPDATE restrito. RETURNING deve mostrar uma linha: id 4, valor_anterior 120.00 e valor_novo 125.00. Confira IDs 4 e 10: somente o 4 mudou de valor; suas datas de liquidação não mudaram. Execute ROLLBACK separadamente e confira novamente: ambos valem 120.00. A contagem permanece em 12. Nenhuma alteração deve ser confirmada neste exercício.

Se um comando falhar e a transação ficar interrompida, execute ROLLBACK na mesma conexão antes de reiniciar. Zero linhas afetadas não é erro SQL, mas não atende ao resultado esperado. Não retire condições para forçar uma alteração. A sintaxe old/new no RETURNING exige PostgreSQL 18 neste percurso.

## Como registrar uma revisão

Conserve a pergunta, o SQL exato, as regras, os casos de teste e a saída observada. Uma explicação convincente não comprova execução; um total geral correto não comprova a presença de todos os usuários. Revise também qualquer versão posterior da consulta. Os exemplos são didáticos e não representam uma avaliação de um serviço ou modelo específico.
