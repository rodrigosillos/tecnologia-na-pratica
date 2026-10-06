# Capítulo 12 R01 — Projeto final

Python na Prática · Rodrigo Sillos · Tecnologia na Prática

Aplicação de terminal que integra despesas estruturadas, extração revisada, consulta documental, PostgreSQL e relatórios recuperáveis. O caminho principal é sintético, sem chave e com zero chamadas de IA.

## Começar

Extraia `cap12` ao lado dos capítulos anteriores, em `projetos\python-na-pratica`. Use a `.venv` Python 3.14.7 já homologada. Não execute arquivos internos de `extracao/` ou `consulta/` diretamente: os pontos de entrada são `app.py`, `verificar_capitulo.py`, `solucao_desafio.py` e `servidor_catalogo.py`.

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\cap12\requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe .\cap12\verificar_capitulo.py
.\.venv\Scripts\python.exe .\cap12\app.py --help
```

Esperado no modo local: **79/79**, `aprovado_local`, exit 0. O verificador neutraliza a credencial e a configuração de tamanho de saída somente dentro de seu processo; não modifica a sessão chamadora. O teste SDK usa transporte em memória, sem serviço externo.

Siga `ROTEIRO_WINDOWS.md` para o percurso completo e registre o resultado em `REGISTRO_WINDOWS.md`, usando o modelo fornecido. A extensão autenticada é opcional; sua ausência não impede a homologação local ou de banco.

## Resultado de referência

| Etapa | Lote | Retrato acumulado |
| --- | --- | --- |
| A estruturada | D001, D002, D003: 127.50 | 3 / 127.50 |
| B revisada | D101 e D102: 53.50; D103 rejeitado | 5 / 181.00 |
| C reimportação revisada | 0 novas, 2 existentes | 5 / 181.00 |
| Reexportação de A depois de B | Recibo de A | 3 / 127.50 |

T001: data `null` corrigida por complemento para `2026-09-11`. T002: total pago 18.50, não subtotal 20.00. T003: kit ambíguo, rejeitado. `decisoes_exemplo.json` contém uma revisão didática explicitamente identificada, não a assinatura de um usuário real.

## Comandos e dependências

| Comando | Banco | Catálogo | IA externa |
| --- | --- | --- | --- |
| `sugerir`, `inspecionar`, `revisar` | Não | Não | Não |
| `consultar` | Não | Não | Não |
| `preparar` | Sim | Não | Não |
| `importar`, `importar-revisado` novos | Sim | Sim | Não |
| Repetir mesma importação confirmada | Sim | Não; entrada/revisão conferidas | Não |
| `status`, `exportar` | Sim | Não | Não |
| `extrair-real` | Não | Não | Opcional, uma tentativa confirmada |
| `consultar-real` | Não | Não | Opcional; sem trechos, zero tentativas |

A nova CLI usa `importar` e `importar-revisado`; o subcomando `executar` do capítulo 11 não existe aqui. `status` sem arquivos correspondentes pode retornar 3 mesmo que a importação esteja confirmada.

## Escopo técnico

- Banco `python_na_pratica`, usuário `python_leitor`, host `127.0.0.1`, porta 5432 (configurável por `PYTHON_PRATICA_PG_PORTA`), PostgreSQL 18; registrar patch. Senha solicitada de forma oculta.
- Esquema manual `tnp_cap12`; `preparar` não limpa dados existentes. Testes criam e removem apenas `tnp_c12_t_<identificador aleatório>`.
- Importação estruturada JSON/CSV: arquivo de até 1 MiB; lote de 1 a 1.000 registros. O retrato validado também está limitado a 1.000 despesas acumuladas. Aplicação sequencial, uma execução por vez.
- Dois pacotes reutilizam contratos dos capítulos 8 e 9; seus nomes de versão originais são mantidos. As fontes, exemplos e prompts preservam a referência anteriormente aprovada.
- Despesas e recibo, incluindo proveniência, são persistidos na mesma transação. IDs assistidos D101/D102/D103 exigem revisão no fluxo da CLI. Isso não é autorização contra um usuário que modifica código ou acessa SQL diretamente.
- Exportação: CSV UTF-8 com BOM, HTML/JSON UTF-8. `proveniencia.json` explica o lote da execução, não a origem de todas as linhas do retrato acumulado. Recibos anteriores devem ser preservados.
- SHA-256 detecta divergências no contrato do laboratório; não autentica a pessoa do revisor nem substitui assinatura digital.
- Consulta lexical de documentos, sem embeddings e sem banco vetorial. P04 demonstra falha de recuperação por vocabulário; não comprova ausência de regra no documento.
- Nenhuma resposta de IA aprova reembolso ou executa SQL. Revisão de extração e revisão semântica da resposta documental continuam necessárias.

## Extensão opcional

SDK fixado em `requirements.txt`, modelo em `extracao/configuracao_ia.py`. `extrair-real` e `consultar-real` exigem `--confirmar-envio` para qualquer envio; nunca forneça segredo por argumento ou nos arquivos do pacote. Usam somente a credencial da sessão já disponível. Não é necessário obter chave para concluir o roteiro.

Uma tentativa por invocação, `max_retries=0`, orçamento estimado padrão 0.010000 USD por invocação. Arquivo `dados/tarifas_referencia.json` é referência de cálculo, não promessa de cobrança. A previsão de entrada usa bytes + margem, não um tokenizador nem limite superior garantido. Limites não são compartilhados entre processos. Antes de uso real, confira tarifas, disponibilidade do modelo e limites da conta.

A resposta real precisa de nova revisão associada ao seu pacote; não copie o gabarito sintético para aprová-la. Uma resposta com uso ausente é bloqueada e mantém a reserva incerta. Falha ao gravar arquivos após tentativa SDK retorna 3 e não provoca repetição automática.

## Verificação

Windows: 79/79 local e 99/99 PostgreSQL nativo, `integracao_nativa`, pendentes 0. Consulte `../VERIFICACAO_RESUMO.md`. A extensão autenticada permanece opcional e não foi executada.

