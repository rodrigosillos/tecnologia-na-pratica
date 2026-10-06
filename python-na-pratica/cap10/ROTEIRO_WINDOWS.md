# Roteiro Windows — capítulo 10 R01

Escopo obrigatório: local, sem chave e sem banco. Extensão autenticada: opcional. Execute em `projetos\python-na-pratica`, com `cap10` ao lado de `.venv`. Use pastas novas ao repetir o roteiro; não apague evidências para forçar sucesso.

## 1. Ambiente e verificador

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r .\cap10\requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe .\cap10\verificar_capitulo.py
$LASTEXITCODE
```

Esperado: Python 3.14.7, SDK 3.24.0, `pip check` sem conflitos; `aprovado_local`, **158/158**, falhas 0, chamadas reais 0, exit 0. O verificador neutraliza a chave e simula o transporte SDK. Copie o JSON indicado para `cap10\evidencias\relatorio-windows-python314.json` e guarde seu SHA-256.

## 2. Ajuste, reserva e comparação completa

No percurso didático, fixe a proposta antes de abrir a reserva. Na homologação, execute as três partições para conferir o comportamento fornecido:

```powershell
.\.venv\Scripts\python.exe .\cap10\02_comparar.py --particao ajuste --destino .\cap10\gerados\windows-ajuste
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap10\02_comparar.py --particao reserva --destino .\cap10\gerados\windows-reserva
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap10\02_comparar.py --particao todos --destino .\cap10\gerados\windows-todos
$LASTEXITCODE
```

Todos exit 0. Ajuste: A 6/12, B 11/12. Reserva: A 6/8, B 7/8. Todos: **A 12/20, B 18/20**, sete melhorias, regressão X04 e falha crítica I02. Decisão `nao_promover`. As partições isoladas também sinalizam avaliação parcial. Confira JSONs `A.json`, `B.json` e `comparacao.json`.

Em todos: categoria 12/13 nas duas versões; formato 20/20 nas duas; custo fictício A USD 0.009160, B USD 0.010440; mediana fictícia A 1110 ms, B 1230 ms. Nada foi gasto no serviço.

## 3. Ausência de revisão não vira acerto

```powershell
.\.venv\Scripts\python.exe .\cap10\01_avaliar.py --versao B --particao todos --sem-revisao --destino .\cap10\gerados\windows-sem-revisao
$LASTEXITCODE
```

Esperado: exit 0; casos 12/20, uma falha, **sete pendências**; fundamentação 0/7, sete pendências. `revisao_pendente.json` contém sete consultas com critérios null. Não preencha todas como verdadeiras sem conferir significado.

## 4. Inspeção e desafio

```powershell
.\.venv\Scripts\python.exe .\cap10\06_inspecionar.py --caso X02 --versao A
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap10\06_inspecionar.py --caso X04 --versao B
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap10\06_inspecionar.py --caso I02 --versao B
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap10\solucao_desafio.py
$LASTEXITCODE
```

Todos exit 0. X02: subtotal 20.00 usado indevidamente no lugar do total 18.50. X04: Alimentação em vez de Materiais. I02: nota intrusa aparece na cópia de contexto; fonte literal não autoriza a conclusão “aprovadas automaticamente”. O arquivo `corpus\politica.md` permanece sem a nota intrusa. Desafio: `nao_promover`.

## 5. Limites sem rede

```powershell
.\.venv\Scripts\python.exe .\cap10\03_simular_limites.py --cenario orcamento
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap10\03_simular_limites.py --cenario chamadas
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap10\03_simular_limites.py --cenario incerto
$LASTEXITCODE
```

Todos exit 0. Reserva USD 0.0016288. Orçamento: uso USD 0.0012 e próxima reserva bloqueada. Chamadas: segunda autorização bloqueada. Incerto: uso desconhecido, reserva mantida, estado incerto, próxima autorização bloqueada. Chamadas reais 0 em todos os casos.

## 6. Preservação dos resultados

```powershell
$hashAntesCap10 = (Get-FileHash .\cap10\gerados\windows-todos\comparacao.json -Algorithm SHA256).Hash
.\.venv\Scripts\python.exe .\cap10\02_comparar.py --particao todos --destino .\cap10\gerados\windows-todos
$LASTEXITCODE
$hashDepoisCap10 = (Get-FileHash .\cap10\gerados\windows-todos\comparacao.json -Algorithm SHA256).Hash
$hashAntesCap10 -eq $hashDepoisCap10
```

Esperado: exit 1, destino existente, comparação `True`.

## 7. Bloqueios anteriores à chamada

```powershell
.\.venv\Scripts\python.exe .\cap10\04_amostra_real.py
$LASTEXITCODE
```

Esperado: exit 2, nenhuma chamada, mesmo se houver chave configurada. Para testar ausência de chave sem correr o risco de efetuar uma chamada:

```powershell
if ([string]::IsNullOrEmpty($env:OPENAI_API_KEY)) {
    .\.venv\Scripts\python.exe .\cap10\04_amostra_real.py --confirmar-envio --destino .\cap10\gerados\windows-sem-chave
    $LASTEXITCODE
} else {
    Write-Output 'Chave presente; ausência de chave já coberta pelo verificador.'
}
```

Sem chave: exit 1, pasta não criada. Não exponha nem remova a chave para fazer esse teste. Não é preciso executar a extensão autenticada para fechar o escopo local.

## 8. Registro e extensão opcional

Preencha `REGISTRO_WINDOWS.md` a partir do modelo, incluindo apresentação no console cp850 e leitura dos JSON em UTF-8. A extensão real pode ficar como **não executada — opcional**.

Se decidir executá-la, siga o README com um único caso, contexto inspecionado, tarifas conferidas e pasta nova. Não dispare automaticamente o conjunto completo. Registre a cobertura de uma amostra (1/20), a revisão pendente, tokens e tempo medidos. Uma resposta incompleta pode ser arquivada com exit 0 pela captura e reprovada pelo avaliador; confirme os dois estados. Falha de gravação retorna 3 e não autoriza repetição automática.
