# Guia de execução

## Percurso principal

1. Prepare a raiz e a `.venv` com o capítulo 2.
2. Leia o README da etapa. Quando houver `requirements.txt`, instale esse arquivo na `.venv` e execute `pip check` com o mesmo interpretador.
3. Execute os exemplos na ordem do capítulo. Confira o resultado e `$LASTEXITCODE` imediatamente após cada comando no PowerShell.
4. Use `ROTEIRO_WINDOWS.md` para a sequência manual e o verificador. Os casos de falha intencional têm saídas esperadas próprias.
5. Preserve os arquivos produzidos e registre o estado real. Não copie uma evidência antiga como se fosse de sua execução.

O capítulo 1 não exige código. As pastas dos demais capítulos são independentes durante a execução; reutilizam conceitos e cópias de componentes, sem depender de importar arquivos da pasta anterior.

## Serviços por etapa

| Etapa | Serviço usado |
| --- | --- |
| 2–4 | Sem API externa ou banco. |
| 5 | Catálogo HTTP local nos exemplos de integração. |
| 6 | PostgreSQL e catálogo para importar; consultar e exportar dispensam o catálogo. |
| 7–10 | Percurso sintético sem chave e sem banco. API autenticada opcional. |
| 11 | PostgreSQL e catálogo na importação; recuperação usa recibo persistido. Sem chamada de IA. |
| 12 | Parte de sugestões e consulta sintética sem banco; persistência com PostgreSQL, catálogo na importação. API de IA opcional. |

Inicie somente uma instância do catálogo na porta indicada. Siga a configuração de conexão de cada capítulo. O verificador pode abrir seu próprio servidor ou esquema de teste; não confunda esse ambiente controlado com a sequência manual.

## Ler um relatório

Confira juntos `status`, aprovados/total, falhas, modo e pendentes. Em alguns capítulos, uma execução apenas local é válida mas não cobre o banco. No capítulo 6, `--sem-banco` testa a parte local e retorna 2; o fechamento de integração exige o modo nativo. Nos capítulos 11 e 12, use `--com-banco` para conferir a integração PostgreSQL depois da passagem local.

A ausência de uma chamada real não invalida o fechamento local de IA. O campo `integracao_real: pendente` do capítulo 7 registra essa ausência. Se escolher a extensão autenticada, siga sua seção específica, inspecione o contexto, registre o resultado e revise seu conteúdo.

## Evitar mistura de execuções

Mantenha uma cópia intacta do apoio para comparação. Os hashes registram bytes de referência: modificar um exercício pode invalidar deliberadamente essa comparação. Use outra cópia para sua solução.

Não apague pastas anteriores para fazer um comando passar. Nos fluxos que exigem pasta nova, escolha outro nome e atualize os comandos dependentes. Os modelos de registro ajudam a anotar a ligação entre entrada, revisão, execução e saída.

Os exemplos são sequenciais. Aguarde uma operação terminar antes de iniciar a próxima no mesmo conjunto de arquivos ou banco.
