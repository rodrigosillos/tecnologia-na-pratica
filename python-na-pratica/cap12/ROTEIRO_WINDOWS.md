# Homologação Windows — capítulo 12 R01

Execute os comandos a partir de `projetos\python-na-pratica`, um de cada vez. Use Python 3.14.7 e a `.venv` já existente. Este roteiro não precisa de chave OpenAI e não faz chamadas de IA. PostgreSQL 18 disponível no banco `python_na_pratica`, usuário `python_leitor`, host `127.0.0.1`; porta padrão 5432. Registre o patch efetivamente utilizado. Se a porta for outra, ajuste `PYTHON_PRATICA_PG_PORTA` apenas nesta sessão. A senha será solicitada de forma oculta.

Pastas e IDs abaixo pressupõem primeira passagem. Se um caminho já existir, preserve-o e escolha um nome novo em todos os comandos dependentes; não use `-Force` para substituir evidências. O esquema `tnp_cap12` começa vazio na primeira preparação, mas `preparar` não limpa um esquema existente. O verificador usa um esquema independente.

## 1. Dependências e testes locais

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r .\cap12\requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe .\cap12\verificar_capitulo.py
$LASTEXITCODE
```

Esperado: Python 3.14.7, dependências consistentes, **79/79**, `aprovado_local`, falhas 0, pendentes 0, exit 0, chamadas reais 0. Copie o JSON indicado para `cap12/evidencias/relatorio-windows-local-python314.json`.

## 2. Banco nativo

```powershell
.\.venv\Scripts\python.exe .\cap12\verificar_capitulo.py --com-banco
$LASTEXITCODE
```

Esperado: **99/99**, `aprovado`, `integracao_nativa`, falhas 0, pendentes 0, exit 0. Não classifique um teste como nativo apenas por haver uma porta TCP; confira a identificação do motor no JSON. O Docker oficial PostgreSQL usado nos capítulos anteriores é adequado para esta etapa.

O teste cria um esquema `tnp_c12_t_` aleatório e apaga somente esse esquema ao terminar. Confere a transação integrada, repetição, revisão, exportação recuperável, três restrições SQL e autenticação por senha incorreta. Se uma senha errada for aceita, investigue a configuração de autenticação, sem remover o teste. Não é necessário apagar dados dos capítulos anteriores.

Copie esse JSON para `cap12/evidencias/relatorio-windows-python314.json`.

## 3. Sugestões e revisão, sem banco

```powershell
.\.venv\Scripts\python.exe .\cap12\app.py sugerir --destino .\cap12\gerados\w12-sugestoes
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py inspecionar --pacote .\cap12\gerados\w12-sugestoes\pacote.json
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py revisar --pacote .\cap12\gerados\w12-sugestoes\pacote.json --revisao .\cap12\gerados\w12-sugestoes\revisao_pendente.json --destino .\cap12\gerados\w12-revisao
$LASTEXITCODE
Test-Path .\cap12\gerados\w12-revisao
```

Esperado: sugerir 0, inspecionar 0; T001 data pendente, T002 total 18.50, T003 categoria pendente. Revisão pendente: **exit 1** e `Test-Path` **False**.

Leia os originais e `extracao/revisoes/decisoes_exemplo.json`. Para reproduzir as decisões didáticas fornecidas:

```powershell
.\.venv\Scripts\python.exe .\cap12\app.py revisar --pacote .\cap12\gerados\w12-sugestoes\pacote.json --revisao .\cap12\extracao\revisoes\decisoes_exemplo.json --destino .\cap12\gerados\w12-revisao
$LASTEXITCODE
```

Esperado: **2 registros / 53.50**, 1 rejeitado, banco não utilizado, exit 0. Abra `trilha.json`: original T001 data null, final `2026-09-11`, complemento `mensagem_T001`; T002 aceito, T003 rejeitado. Esse revisor é um exemplo rotulado, não uma evidência de autoria pessoal.

## 4. Catálogo, preparação e execução A

No segundo terminal, na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe .\cap12\servidor_catalogo.py
```

Reutilize o catálogo anterior se ele já ocupa a porta 8765. No primeiro terminal:

```powershell
.\.venv\Scripts\python.exe .\cap12\app.py preparar
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py importar --execucao windows-12-a --entrada .\cap12\dados\validas.json
$LASTEXITCODE
```

Esperado: preparação 0; A **3 / 127.50**, 3 novas, 0 existentes, exportação criada, exit 0. Cinco arquivos em `cap12/gerados/relatorios/windows-12-a`, proveniência estruturada. Esquemas anteriores preservados.

## 5. Revisão pendente bloqueia B

```powershell
.\.venv\Scripts\python.exe .\cap12\app.py importar-revisado --execucao windows-12-b --pacote .\cap12\gerados\w12-sugestoes\pacote.json --revisao .\cap12\gerados\w12-sugestoes\revisao_pendente.json
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py status --execucao windows-12-b
$LASTEXITCODE
```

Esperado: bloqueio 1; recibo ausente 1. Banco permanece com 3 / 127.50. O programa pede senha para os comandos de banco, mesmo quando uma revisão será bloqueada.

## 6. B confirmada com exportação pendente

Crie um arquivo onde deveria haver uma pasta; não use `-Force`:

```powershell
New-Item -ItemType File -Path .\cap12\gerados\bloqueio-w12 -Value 'preservar'
.\.venv\Scripts\python.exe .\cap12\app.py importar-revisado --execucao windows-12-b --pacote .\cap12\gerados\w12-sugestoes\pacote.json --revisao .\cap12\extracao\revisoes\decisoes_exemplo.json --destino .\cap12\gerados\bloqueio-w12
$LASTEXITCODE
```

Esperado: importação confirmada, **5 / 181.00**, origem revisada, exportação pendente, **exit 3**. Arquivo de bloqueio preservado. Duas despesas novas e proveniência confirmadas no mesmo recibo.

## 7. Recuperar sem catálogo e sem IA

Pare somente o catálogo no segundo terminal com Ctrl+C. Mantenha PostgreSQL disponível.

```powershell
.\.venv\Scripts\python.exe .\cap12\app.py exportar --execucao windows-12-b
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py status --execucao windows-12-b
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py exportar --execucao windows-12-a --destino .\cap12\gerados\retrato-antigo-w12
$LASTEXITCODE
```

Esperado: B **5 / 181.00**, A **3 / 127.50**, todas saídas 0. Sem nova importação. O código automatizado também impede o acesso ao pacote de revisão, ao catálogo e à IA durante a recuperação.

Abra `despesas.csv`, `despesas.html`, `recibo.json`, `proveniencia.json`, `manifesto.json` da execução B. São cinco arquivos; D103 não aparece no relatório. A proveniência explica D101/D102 e a rejeição de D103. Confira a data corrigida e o complemento. Preserve o recibo A para explicar as três despesas iniciais.

Reexportar deve preservar bytes:

```powershell
$antes = (Get-FileHash .\cap12\gerados\relatorios\windows-12-b\proveniencia.json -Algorithm SHA256).Hash
.\.venv\Scripts\python.exe .\cap12\app.py exportar --execucao windows-12-b
$LASTEXITCODE
$depois = (Get-FileHash .\cap12\gerados\relatorios\windows-12-b\proveniencia.json -Algorithm SHA256).Hash
$antes -eq $depois
```

Esperado: reutilizada, 0, True. Um destino divergente é preservado, não substituído; esse caso é conferido automaticamente.

## 8. Reimportação e rollback

Reinicie o catálogo no segundo terminal. No primeiro:

```powershell
.\.venv\Scripts\python.exe .\cap12\app.py importar-revisado --execucao windows-12-c --pacote .\cap12\gerados\w12-sugestoes\pacote.json --revisao .\cap12\extracao\revisoes\decisoes_exemplo.json
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py importar --execucao windows-12-conflito --entrada .\cap12\dados\conflito_banco.json
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py status --execucao windows-12-conflito
$LASTEXITCODE
```

Esperado: C 0, cinco despesas / 181.00, recibo com **0 novas e 2 existentes**. Conflito 1 e recibo ausente 1. No Query Tool do banco de estudos, execute separadamente:

```sql
SELECT id, valor FROM tnp_cap12.despesas ORDER BY id;
SELECT count(*), sum(valor) FROM tnp_cap12.despesas;
SELECT id, novas, existentes FROM tnp_cap12.execucoes ORDER BY id;
```

Esperado na primeira passagem: D001 12.50; D002 35.00; D003 80.00; D101 35.00; D102 18.50; total 5 / 181.00; recibos A, B, C. D005 e D103 ausentes. Uma repetição com outra revisão sob o mesmo ID é bloqueada pelo verificador.

## 9. Consulta documental e falhas sintéticas

```powershell
.\.venv\Scripts\python.exe .\cap12\app.py consultar --caso P01 --destino .\cap12\gerados\w12-p01
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py consultar --caso P03 --destino .\cap12\gerados\w12-p03
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py consultar --caso P04 --destino .\cap12\gerados\w12-p04
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py sugerir --cenario incompleta --destino .\cap12\gerados\w12-incompleta
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py sugerir --cenario recusa --destino .\cap12\gerados\w12-recusa
$LASTEXITCODE
```

Esperado: P01 `aguarda_revisao` / fonte POL-002 / 7 pontos, P03 `abstencao_proposta`, P04 `abstencao_local`; saídas 0. Incompleta e recusa: T002 bloqueada, saídas 1. Não há escrita no banco. O teste automatizado confirma que aceitar um envelope bloqueado não libera o lote.

Leia P01: 60.00 por pessoa **por dia**, sem trocar por refeição; comprovante e finalidade continuam exigidos. P04 é um limite da busca lexical, não uma garantia de inexistência da regra. Nenhuma consulta aprova ou paga despesas.

## 10. Desafio e guardas da extensão real

```powershell
.\.venv\Scripts\python.exe .\cap12\solucao_desafio.py
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap12\app.py extrair-real --origem T002 --destino .\cap12\gerados\w12-api
$LASTEXITCODE
```

Esperado: apenas D003 destacado, 0; extensão sem confirmação 2, zero chamadas. Se **não houver chave na sessão**, execute também:

```powershell
.\.venv\Scripts\python.exe .\cap12\app.py extrair-real --origem T002 --destino .\cap12\gerados\w12-api --confirmar-envio
$LASTEXITCODE
```

Esperado sem chave: configuração bloqueada, 1, zero chamadas, pasta não criada. Se houver chave, não execute esse comando como teste sem envio: o verificador já testa a ausência de credencial sem usar a sessão real. A chamada autenticada e a revisão de seu conteúdo continuam opcionais e devem ter registro separado quando realizadas.

## 11. Registro

Preencha `REGISTRO_WINDOWS_MODELO.md` como `REGISTRO_WINDOWS.md`, com versões, caminhos, hashes e resultados manuais. Registre a ressalva de console cp850 se aparecer; confirme UTF-8 dos arquivos no editor, CSV/HTML legíveis. Não inclua credenciais ou dados privados.

Critério de fechamento deste escopo: local 79/79, nativo 99/99, pendentes 0 no modo nativo, roteiro manual conferido. Zero chamadas de IA é um resultado válido; a extensão autenticada não impede esse fechamento.
