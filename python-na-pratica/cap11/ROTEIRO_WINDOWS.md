# Homologação Windows — capítulo 11 R01

Execute uma aplicação por vez. Parta da raiz `projetos\python-na-pratica`. Não há chamada de IA em nenhum passo. Mantenha o PostgreSQL 18 do capítulo 6 disponível em `127.0.0.1:5432`, banco `python_na_pratica`, usuário `python_leitor`. Se a porta for outra, defina `$env:PYTHON_PRATICA_PG_PORTA` nesta sessão. Senha será solicitada de forma oculta pelo Python.

## 1. Ambiente e verificações locais

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r .\cap11\requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe .\cap11\verificar_capitulo.py
$LASTEXITCODE
```

Esperado: `aprovado_local`, **80/80**, saída 0. O relatório JSON registra sistema, Python e hashes. Se o verificador retornar 0 com status complementar ou pendente em outro modo, leia a pendência; não marque a integração como aprovada.

## 2. Integração nativa em esquema temporário

```powershell
.\.venv\Scripts\python.exe .\cap11\verificar_capitulo.py --com-banco
$LASTEXITCODE
```

Esperado no PostgreSQL nativo: **97/97**, `status: aprovado`, `modo: integracao_nativa`, pendentes 0, saída 0. O verificador cria um esquema `tnp_c11_t_` aleatório e apaga **apenas esse esquema de teste** ao terminar. Não apaga o `tnp_cap06` nem o `tnp_cap11`. Confere importação, deduplicação, rollback, recibo, retrato preservado, exportação, confirmação perdida simulada, restrições e rejeição de senha incorreta. Registre o patch real do PostgreSQL.

Se a senha incorreta for aceita, confira a autenticação local configurada no servidor; não desative esse teste. A simulação de confirmação perdida com commit real não é uma queda física da rede PostgreSQL.

## 3. Tentativas e erro intencional, sem banco

```powershell
.\.venv\Scripts\python.exe .\cap11\01_tentativas.py --cenario recupera
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap11\01_tentativas.py --cenario esgota
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap11\01_tentativas.py --cenario contrato
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap11\02_erro_intencional.py
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap11\solucao_desafio.py
$LASTEXITCODE
```

Esperado, respectivamente: 3 tentativas/exit 0; 3/exit 1; 1/exit 1; erro detectado/exit 1; decisões importar/exportar/conferir/consultar/exit 0. Esperas do caso recuperado: 0.2 e 0.4 segundos. Servidor de ensaio sobe e fecha automaticamente em loopback; ele não é o servidor do próximo passo.

## 4. Preparação e primeira importação

Em um segundo PowerShell, inicie o catálogo (se o servidor do capítulo 5/6 já estiver aberto nessa porta, reutilize-o):

```powershell
.\.venv\Scripts\python.exe .\cap11\servidor_catalogo.py
```

No primeiro PowerShell:

```powershell
.\.venv\Scripts\python.exe .\cap11\app.py preparar
.\.venv\Scripts\python.exe .\cap11\app.py executar --execucao windows-11-a --entrada .\cap11\dados\validas.json
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap11\app.py status --execucao windows-11-a
$LASTEXITCODE
```

Primeira execução em esquema novo: 3 registros / 127.50, exportação criada, saídas 0. Arquivos em `cap11/gerados/relatorios/windows-11-a`. No `recibo.json`, novas 3, existentes 0. IDs e resultados abaixo presumem primeira passagem deste roteiro. Em uma repetição, preserve as evidências e registre o estado anterior: não apague o banco para obter o gabarito.

## 5. Falha de exportação após commit

Crie um **arquivo** onde deveria haver uma pasta. `New-Item` sem `-Force` preserva um caminho que já exista; se falhar por existência, use outro nome em todo o passo.

```powershell
New-Item -ItemType Directory -Path .\cap11\gerados -ErrorAction SilentlyContinue
New-Item -ItemType File -Path .\cap11\gerados\bloqueio-w11 -Value 'bloqueio didatico'
.\.venv\Scripts\python.exe .\cap11\app.py executar --execucao windows-11-b --entrada .\cap11\dados\quarta_despesa.json --destino .\cap11\gerados\bloqueio-w11
$LASTEXITCODE
```

Esperado: importação confirmada, retrato 4 / 147.50, exportação pendente, **exit 3**. O arquivo de bloqueio continua intacto.

Pare o servidor do catálogo com Ctrl+C. Recupere apenas a exportação, mantendo o banco disponível:

```powershell
.\.venv\Scripts\python.exe .\cap11\app.py exportar --execucao windows-11-b
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap11\app.py status --execucao windows-11-b
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap11\app.py exportar --execucao windows-11-a --destino .\cap11\gerados\retrato-antigo
$LASTEXITCODE
```

Esperado: B 4 / 147.50; A **3 / 127.50**, mesmo depois de D004. Todos exit 0. Catálogo desligado não impede essas exportações. Nenhuma chamada de IA é feita. Não há nova importação.

## 6. Reutilização e vínculo de entrada

```powershell
$antes = (Get-FileHash .\cap11\gerados\relatorios\windows-11-b\despesas.csv -Algorithm SHA256).Hash
.\.venv\Scripts\python.exe .\cap11\app.py exportar --execucao windows-11-b
$LASTEXITCODE
$depois = (Get-FileHash .\cap11\gerados\relatorios\windows-11-b\despesas.csv -Algorithm SHA256).Hash
$antes -eq $depois
.\.venv\Scripts\python.exe .\cap11\app.py executar --execucao windows-11-a --entrada .\cap11\dados\validas.json
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap11\app.py executar --execucao windows-11-a --entrada .\cap11\dados\quarta_despesa.json
$LASTEXITCODE
```

Esperado: reutilizada/exit 0, hash `True`; A original reutilizada/exit 0 sem catálogo; A com outro arquivo bloqueada/exit 1. A senha do banco continua necessária.

## 7. Destino divergente, sem apagar arquivos

```powershell
New-Item -ItemType Directory -Path .\cap11\gerados\divergente-w11\windows-11-b
New-Item -ItemType File -Path .\cap11\gerados\divergente-w11\windows-11-b\meu-arquivo.md -Value 'preservar'
.\.venv\Scripts\python.exe .\cap11\app.py exportar --execucao windows-11-b --destino .\cap11\gerados\divergente-w11
$LASTEXITCODE
Get-Content .\cap11\gerados\divergente-w11\windows-11-b\meu-arquivo.md
```

Esperado: exit 3; arquivo preservado. Não há comando de sobrescrita.

## 8. Conflito e rollback

Reinicie o catálogo no segundo terminal. No primeiro:

```powershell
.\.venv\Scripts\python.exe .\cap11\app.py executar --execucao windows-11-conflito --entrada .\cap11\dados\conflito_banco.json
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap11\app.py status --execucao windows-11-conflito
$LASTEXITCODE
```

Esperado: execução bloqueada/exit 1 e recibo ausente/exit 1. D005 deve estar ausente; D002 continua 35.00. No Query Tool do banco do laboratório, execute separadamente:

```sql
SELECT id, valor FROM tnp_cap11.despesas ORDER BY id;
SELECT count(*), sum(valor) FROM tnp_cap11.despesas;
SELECT id, novas, existentes FROM tnp_cap11.execucoes ORDER BY id;
```

Na primeira passagem: 4 despesas / 147.50; recibos apenas `windows-11-a` e `windows-11-b`. O verificador já confere essas propriedades em esquema separado.

## 9. Evidências e encerramento

Abra CSV e HTML, confira acentos, quantidade e total; examine os logs JSONL. Console cp850 pode exibir acentos incorretos mesmo com arquivos UTF-8 corretos. Essa ressalva deve ser registrada, sem alterar codificação dos dados para contorná-la.

Copie o JSON do verificador **nativo aprovado** para `cap11/evidencias/relatorio-windows-python314.json`. Preencha `REGISTRO_WINDOWS_MODELO.md` como `REGISTRO_WINDOWS.md`. Inclua os hashes, resultados manuais e eventuais diferenças. Não inclua senha, ambiente virtual ou dados privados. A chamada autenticada de IA continua opcional e fora deste capítulo.
