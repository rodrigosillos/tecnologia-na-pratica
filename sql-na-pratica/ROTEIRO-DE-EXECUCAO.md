# Roteiro de execução

Leia primeiro PREPARACAO-PGADMIN.md. Execute os exemplos conforme as pausas abaixo.

## Onde encontrar cada atividade

| Arquivo | Finalidade |
| --- | --- |
| `laboratorio/00_verificar_conexao.sql` | Conferir a conexão antes de trabalhar. |
| `laboratorio/01_estrutura.sql` | Criar as cinco tabelas num banco de estudos vazio. |
| `laboratorio/02_dados.sql` | Carregar a base fictícia inicial. |
| `laboratorio/03_capitulo_01.sql` | Consultas do capítulo 1. |
| `laboratorio/04_conferencias.sql` | Contagens e totais para verificar a base. |
| `laboratorio/05_capitulo_02.sql` | Exemplos do capítulo 2. |
| `laboratorio/06_exercicios_capitulo_02.sql` | Soluções SQL do capítulo 2. |
| `laboratorio/07_capitulo_03.sql` | Consultas do capítulo 3. |
| `laboratorio/08_erro_controlado_capitulo_03.sql` | Demonstração com erro intencional, executada em três blocos separados. |
| `laboratorio/09_exercicios_capitulo_03.sql` | Solução SQL do exercício 1 do capítulo 3. |
| `RESPOSTAS-CAPITULO-03.md` | Raciocínio das respostas dos dois exercícios. |
| `laboratorio/10_capitulo_04.sql` | Filtros, ordenação, expressões, datas, CASE e COALESCE. |
| `laboratorio/11_diagnosticos_capitulo_04.sql` | Consultas intencionalmente incorretas e correções para comparar resultados. |
| `laboratorio/12_exercicios_capitulo_04.sql` | Soluções dos dois exercícios do capítulo 4. |
| `RESPOSTAS-CAPITULO-04.md` | Resultados esperados e explicações das soluções. |
| `laboratorio/13_capitulo_05.sql` | JOINs, cardinalidade, preservação de contas e associação de orçamentos. |
| `laboratorio/14_diagnosticos_capitulo_05.sql` | Consultas intencionalmente incorretas para analisar perdas e multiplicação de linhas. |
| `laboratorio/15_exercicios_capitulo_05.sql` | Soluções dos dois exercícios do capítulo 5. |
| `RESPOSTAS-CAPITULO-05.md` | Resultados e raciocínio das soluções do capítulo 5. |
| `laboratorio/16_capitulo_06.sql` | Agregações, grupos, filtros, ausências, pendências e orçamentos. |
| `laboratorio/17_diagnosticos_capitulo_06.sql` | Filtro antes da soma, soma distinta e contagem indevida após LEFT JOIN. |
| `laboratorio/18_exercicios_capitulo_06.sql` | Soluções dos dois exercícios do capítulo 6. |
| `RESPOSTAS-CAPITULO-06.md` | Resultados esperados e explicações das soluções do capítulo 6. |
| `laboratorio/19_capitulo_07.sql` | Subconsultas, EXISTS, CTEs e comparação com orçamentos. |
| `laboratorio/20_diagnosticos_capitulo_07.sql` | Correlação ausente, NOT IN e EXISTS com COUNT. |
| `laboratorio/21_view_capitulo_07.sql` | Criar uma view uma vez e consultar suas despesas por mês. |
| `laboratorio/22_exercicios_capitulo_07.sql` | Soluções dos dois exercícios do capítulo 7. |
| `RESPOSTAS-CAPITULO-07.md` | Resultados esperados e explicações das soluções do capítulo 7. |
| `laboratorio/23_capitulo_08.sql` | Totais por janela, percentuais, rankings, acumulados e comparação mensal. |
| `laboratorio/24_diagnosticos_capitulo_08.sql` | Empates desfeitos, limite global e filtros que mudam a entrada da janela. |
| `laboratorio/25_exercicios_capitulo_08.sql` | Soluções dos dois exercícios do capítulo 8. |
| `RESPOSTAS-CAPITULO-08.md` | Resultados esperados e explicações das soluções do capítulo 8. |
| `laboratorio/26_capitulo_09_transacoes.sql` | Ensaios de INSERT, UPDATE e DELETE, com RETURNING e ROLLBACK. |
| `laboratorio/27_capitulo_09_commit.sql` | Inserção confirmada de usuário de teste e exclusão de limpeza, com pausas para conferência. |
| `laboratorio/28_capitulo_09_savepoint.sql` | Erros intencionais de CHECK e transação interrompida; recuperação com savepoint. |
| `laboratorio/29_exercicios_capitulo_09.sql` | Soluções dos dois exercícios, incluindo UPDATE que altera zero linhas sem erro. |
| `RESPOSTAS-CAPITULO-09.md` | Resultados, instruções e explicações das soluções do capítulo 9. |
| `laboratorio/30_capitulo_10_carga.sql` | Gerar 100 mil despesas sintéticas em tabela temporária e coletar estatísticas. |
| `laboratorio/31_capitulo_10_planos.sql` | Conferir o resultado e comparar planos antes e depois de um índice composto. |
| `laboratorio/32_exercicios_capitulo_10.sql` | Diagnósticos de EXTRACT e BETWEEN, com soluções dos dois exercícios. |
| `laboratorio/33_capitulo_10_limpeza.sql` | Remover a tabela temporária e seu índice e conferir a base original. |
| `RESPOSTAS-CAPITULO-10.md` | Resultados, raciocínio e limites de interpretação dos planos do capítulo 10. |
| `REGISTRO-COMPARACAO-CAPITULO-10.md` | Ficha para registrar planos, contagens, buffers e tempos da sua execução. |
| `laboratorio/34_capitulo_11_revisao.sql` | Diagnosticar a ausência de um usuário, rastrear despesas e conferir uma consulta revisada. |
| `laboratorio/35_exercicios_capitulo_11.sql` | Contraexemplo de SUM DISTINCT e ensaio de alteração restrita com ROLLBACK. |
| `PROMPTS-CAPITULO-11.md` | Pedidos completos para adaptar, com contexto fictício, critérios e devolutivas. |
| `RESPOSTAS-CAPITULO-11.md` | Resultados esperados e soluções comentadas dos dois exercícios. |
| `REGISTRO-REVISAO-CAPITULO-11.md` | Ficha para registrar a pergunta, o SQL, os testes e a decisão. |
| `laboratorio/36_capitulo_12_preparacao.sql` | Identificar a conexão e conferir a base original. |
| `laboratorio/37_capitulo_12_relatorios.sql` | Seis consultas corretas que resolvem as tarefas 1 a 5. |
| `laboratorio/38_capitulo_12_diagnostico.sql` | Investigar uma consulta com erro lógico intencional, somente de leitura. |
| `laboratorio/39_capitulo_12_correcao.sql` | Executar a tarefa 6, repetir relatórios e desfazer a alteração com ROLLBACK. |
| `RESPOSTAS-CAPITULO-12.md` | Soluções comentadas e critérios de conferência das seis tarefas. |
| `ROTEIRO-PROJETO-FINAL.md` | Ficha para registrar perguntas, consultas, resultados e verificações. |
| `laboratorio/40_guia_consultas.sql` | Leituras do guia rápido e EXPLAIN ANALYZE de um SELECT. |
| `laboratorio/41_guia_alteracao.sql` | Prévia, alteração restrita, RETURNING e ROLLBACK. |
| `CONFERENCIAS-GUIA-RAPIDO.md` | Resultados esperados de cada bloco do guia. |
| `MAPA-DO-LABORATORIO.md` | Localização dos arquivos e dependências por capítulo. |
| `apoio/` | Alternativa opcional com Docker para quem já o utiliza. |

Os scripts dos capítulos 4 a 8 definem `DateStyle` como ISO, YMD na sessão para reproduzir a apresentação textual das datas. Os arquivos 11, 14, 17, 20 e 24 contêm erros de lógica, sem falhas de sintaxe: consultas que executam, mas respondem à pergunta errada.

Não execute o arquivo 08 inteiro nem faça um laço que execute todos os arquivos SQL. Seu segundo bloco deve falhar com SQLSTATE 23505. Execute o `ROLLBACK` do terceiro bloco separadamente, na mesma conexão, para recuperar a sessão.

No capítulo 7, execute `19_capitulo_07.sql`, `20_diagnosticos_capitulo_07.sql` e as soluções do arquivo 22 uma instrução por vez. No arquivo 21, execute `CREATE VIEW` uma única vez; depois selecione apenas o `SELECT` para repetir a consulta. A criação adiciona uma definição ao schema, sem alterar os lançamentos. Uma segunda criação com o mesmo nome retorna erro 42P07. Se estiver dentro de uma transação que ficou interrompida, execute `ROLLBACK;` antes de continuar.

No capítulo 8, os arquivos 23, 24 e 25 apenas consultam os dados e não dependem da view do capítulo 7. Selecione cada instrução inteira, incluindo o WITH quando houver. O arquivo 24 contém erros de lógica intencionais; ele não é uma coleção de consultas corretas para copiar em relatórios.

## Execução do capítulo 9

Os arquivos 26 a 29 alteram dados do laboratório. Use a mesma aba e conexão em cada experiência. Trabalhe com um bloco numerado por vez; dentro dele, selecione e execute uma instrução até o ponto e vírgula por vez, na ordem, conferindo a saída. Não execute um arquivo inteiro nem todos os scripts em um laço.

Para reproduzir os erros controlados, use Auto commit ativado e Auto rollback on error desativado no Query Tool. BEGIN e o desfecho explícito controlam a transação. Finalize cada transação antes de iniciar a próxima; se o estado divergir do esperado, pare e investigue, usando ROLLBACK quando houver transação aberta.

O arquivo 27 é a única experiência deste capítulo que confirma alterações. O ID 900001 deve estar ausente antes de começar. Confira o ID e o nome retornados antes de cada COMMIT. O arquivo inclui a limpeza restrita ao usuário temporário, também confirmada. Não remova automaticamente um ID que já existia antes da experiência.

O arquivo 28 deve falhar com SQLSTATE 23514 e depois 25P02, em execuções separadas. Use ROLLBACK TO na mesma conexão para recuperar a sessão; o ROLLBACK final restaura os dados originais. Os arquivos 26 e 29 terminam todos os ensaios com ROLLBACK. RETURNING não confirma alterações.

## Execução do capítulo 10

Encerre as transações do capítulo anterior. Use a mesma aba e conexão, com autocommit ativado, durante todo o experimento. Execute uma instrução por vez dos arquivos 30, 31, 32 e 33, nessa ordem, conferindo as saídas. Não refaça a carga no meio da comparação: isso remove o índice e reinicia o conjunto temporário.

A carga usa `pg_temp.despesas_teste`, com 100 mil linhas e 500 contas sintéticas. Essa tabela é separada das cinco tabelas do projeto; os identificadores não representam as contas da base original. Não faça JOIN entre esses conjuntos. A tabela temporária e seu índice pertencem à sessão atual. Ao abrir outra conexão, prepare a carga novamente nela.

Todos os EXPLAIN ANALYZE deste capítulo executam SELECTs. O arquivo 31 cria o índice entre as duas medições; o 32 contém uma consulta intencionalmente incorreta com BETWEEN. Registre o resultado correto antes de comparar desempenho. O arquivo 33 encerra a experiência removendo somente a tabela temporária e seu índice.

Use a ficha REGISTRO-COMPARACAO-CAPITULO-10.md para anotar o que observar no seu ambiente. Planos e tempos podem variar. O capítulo não estabelece meta fixa de milissegundos nem obriga o planejador a escolher um índice.

## Execução do capítulo 11

Use a base original, com 12 lançamentos, após encerrar as transações anteriores. O capítulo não depende da tabela temporária ampliada do capítulo 10. Execute uma instrução por vez dos arquivos 34 e 35, nessa ordem, com autocommit ativado, mantendo a mesma aba e conexão.

O arquivo 34 apresenta uma candidata intencionalmente incompleta, a listagem que permite conferir as despesas e a correção. O arquivo 35 contém outra candidata, com SUM DISTINCT, e um contraexemplo com VALUES que não insere dados. A parte de alteração do arquivo 35 deve começar somente após a prévia encontrar o ID 4, conta 1, valor 120.00 e data de liquidação nula. Execute BEGIN, UPDATE, conferência e ROLLBACK separadamente. Não execute o arquivo inteiro nem troque ROLLBACK por COMMIT.

O RETURNING esperado tem uma linha, ID 4, valor anterior 120.00 e novo 125.00. Se a prévia ou o retorno divergir, pare e investigue. Se houver transação aberta ou interrompida, execute ROLLBACK na mesma conexão antes de reiniciar. Zero linhas afetadas não comprova que a correção foi realizada.

As consultas candidatas são exemplos didáticos, não respostas garantidas de uma ferramenta. Usar um serviço de IA é opcional. O pacote fornece os prompts e todas as consultas; não envie credenciais ou dados reais para reproduzir a atividade.

## Execução do capítulo 12

Use a base original, com 12 lançamentos, após encerrar transações anteriores. Nenhuma tarefa depende da tabela ampliada do capítulo 10 ou da view do capítulo 7. Mantenha a mesma aba e conexão, com autocommit ativado, e execute uma instrução completa por vez.

O arquivo 36 prepara a sessão. O arquivo 37 reúne as seis consultas corretas das tarefas 1 a 5: fechamento, pendências, orçamento, despesas sem orçamento, ranking e comparação mensal. O arquivo 38 contém o diagnóstico de leitura da tarefa 2; sua resposta incompleta é intencional. Leia os critérios e tente sua solução antes de consultar o arquivo 37.

O período principal usa competência de maio de 2026. No corte de encerramento de 31 de maio, liquidação nula ou a partir de 1º de junho indica pendência. A atividade usa datas registradas na amostra; não reconstrói o histórico de edições do banco e não é um relatório de fluxo de caixa.

O arquivo 39 reúne a tarefa 6. Registre os resultados originais. Antes de BEGIN, a prévia deve encontrar somente ID 4, conta 1, despesa de 120.00 com liquidação nula. O UPDATE altera seu valor para 125.00; RETURNING deve mostrar exatamente uma linha, com os valores anterior e novo. Se o alvo ou o retorno divergir, pare e investigue. Zero alterações não comprova a correção.

Com a transação aberta, repita os seis relatórios na mesma conexão, compare seus resultados e execute ROLLBACK. Repita os relatórios após desfazer e confirme a restauração da base. O arquivo contém todas essas consultas, na ordem. Não execute o arquivo inteiro de uma vez e não substitua ROLLBACK por COMMIT. Se ocorrer erro dentro da transação, execute ROLLBACK separadamente na mesma conexão antes de reiniciar.

O roteiro permite registrar seu trabalho. As soluções estão completas no livro e neste pacote. Usar uma ferramenta de IA é opcional.

## Execução do guia rápido

Use a base original, com 12 lançamentos, após encerrar transações anteriores. Execute o arquivo 40 uma instrução por vez. Ele prepara a sessão e reúne as consultas; o último bloco executa EXPLAIN ANALYZE sobre um SELECT. O guia não depende da view do capítulo 7 ou da tabela ampliada do capítulo 10.

O arquivo 41 contém um ensaio de alteração. Mantenha a mesma aba e conexão com autocommit ativado. A prévia deve encontrar uma linha: ID 4, conta 1, valor 120.00 e data nula. Se divergir, pare e investigue. Execute BEGIN e UPDATE separadamente. RETURNING deve mostrar somente ID 4, antes 120.00 e depois 125.00. Encerre com ROLLBACK e confira a restauração. Se ocorrer erro, execute ROLLBACK separadamente na mesma conexão. Não execute o arquivo inteiro nem substitua seu desfecho por COMMIT.

CONFERENCIAS-GUIA-RAPIDO.md registra as respostas. MAPA-DO-LABORATORIO.md ajuda a localizar os arquivos de todos os capítulos. As explicações do guia e os 49 verbetes do glossário fazem parte do livro; este pacote reúne apenas o apoio de execução.

