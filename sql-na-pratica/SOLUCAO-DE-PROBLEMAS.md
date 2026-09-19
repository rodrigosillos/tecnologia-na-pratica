# Solução de problemas

Leia a primeira mensagem de erro. Um problema de conexão acontece antes de o servidor executar o SQL; uma falha de consulta não significa que você precise reinstalar o PostgreSQL.

| Situação | O que conferir | Próxima ação |
| --- | --- | --- |
| Conexão recusada | Servidor iniciado, host e porta | Confira o serviço do PostgreSQL e a porta anotada na instalação. O pgAdmin aberto não comprova que o servidor esteja ativo. |
| Senha rejeitada | Usuário e senha daquela conexão | Use a senha de `estudante_sql` na conexão de estudos. A senha administrativa é outra. |
| Banco ou usuário diferente | Execute `00_verificar_conexao.sql` | Abra a conexão de estudos correta antes de carregar arquivos. |
| Tabela não encontrada | Banco, schema e carga | Tente `SELECT COUNT(*) FROM sql_pratica.lancamentos;`. Se o nome completo funcionar, execute `SET search_path TO sql_pratica;`. |
| Acesso negado | `current_user` e proprietário dos objetos | O usuário de estudos deve ser dono do banco e executar 01 e 02. Preserve uma carga feita por outro usuário; prepare um banco de estudos vazio conforme o roteiro. |
| Schema já existe | Carga anterior ou execução parcial | Pare, confira o que já está criado e encerre a transação com `ROLLBACK` se estiver interrompida. Não apague a base para repetir o arquivo. |
| Chave repetida na carga | Arquivo 02 já executado | Não recarregue os mesmos IDs. Confira as contagens e os resultados. |
| SQLSTATE 23505 no arquivo 08 | Segundo INSERT da experiência | É o erro de unicidade esperado. Execute o `ROLLBACK` indicado, separadamente na mesma conexão. |
| SQLSTATE 23514 e depois 25P02 no arquivo 28 | Restrição e transação interrompida | São erros esperados nesse roteiro. Execute `ROLLBACK TO SAVEPOINT antes_valor;` e os passos seguintes na mesma conexão. |
| SQLSTATE 25P02 fora da experiência | O erro anterior na transação | Execute `ROLLBACK;` separadamente e investigue a causa. Repetir apenas o SELECT não recupera a transação. |
| View já existe | Arquivo 21 executado novamente | Para consultar de novo, selecione somente o SELECT. O CREATE VIEW é executado uma vez. |
| Tabela de desempenho não encontrada | Sessão em que o arquivo 30 foi executado | Use a mesma conexão nos arquivos 30 a 33. Se a sessão foi encerrada, reinicie a experiência nela desde o arquivo 30. |
| UPDATE retorna zero linhas | Prévia e estado atual do registro | Pare e investigue. Zero linhas não comprova que a alteração desejada aconteceu. |
| Planos ou tempos diferentes | Versão, estatísticas, máquina e carga | Compare primeiro os registros e totais. Não há um tempo fixo ou um plano universal esperado. |

## Quando recomeçar a base

Se você mudou a base e quer retornar ao conjunto inicial, crie **outro banco vazio de estudos**, pertencente a `estudante_sql`, e execute 01 e 02 nele. Preserve o banco anterior enquanto precisar dos seus exercícios. Este pacote não fornece um comando de exclusão geral.

## Lacunas nos identificadores

Uma sequência pode avançar mesmo quando o INSERT é desfeito por `ROLLBACK`. Os registros voltarem ao estado inicial não significa que o próximo identificador voltará ao número anterior. Não reinicie sequências para eliminar lacunas.

## Se ainda houver divergência

Registre a versão, o arquivo e o bloco executado, a consulta completa, a mensagem e o resultado. Confira também se continuou na mesma aba e conexão. Não inclua senhas ou dados de outro banco em capturas de tela.
