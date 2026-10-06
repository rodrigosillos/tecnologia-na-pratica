# Roteiro Windows — capítulo 9 R01

**Obrigatório neste escopo: fluxo local. Extensão autenticada: opcional.**

Abra o PowerShell em `projetos\python-na-pratica`; mantenha apenas uma execução ativa. A pasta `cap09` deve estar ao lado de `.venv`. Para uma repetição do roteiro, escolha outras pastas de saída. Não apague evidências anteriores para forçar sucesso.

## 1. Ambiente

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r .\cap09\requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe .\cap09\verificar_capitulo.py
$LASTEXITCODE
```

Esperado: Python 3.14.7 no ambiente já homologado; `pip check` sem conflitos; verificador `aprovado_local`, **110/110**, falhas 0, chamadas reais 0 e exit 0. O verificador não usa a chave da sessão e não usa banco. Não presuma execução autenticada a partir dos testes do SDK.

Copie o relatório cujo caminho aparece na saída para `cap09\evidencias\relatorio-windows-python314.json` e anote o caminho original. Leia o JSON em UTF-8 se o console cp850 corromper a apresentação dos acentos.

## 2. Recuperação

```powershell
.\.venv\Scripts\python.exe .\cap09\01_buscar.py --caso P01
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap09\01_buscar.py --caso P03
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap09\01_buscar.py --caso P04
$LASTEXITCODE
```

Esperado: todos exit 0. P01: POL-002, 7 pontos; P03: POL-001, 2 pontos, sem regra por quilômetro; P04: nenhum trecho. Confirme no documento que a regra de alimentação existe, embora “almoço” não a tenha recuperado.

## 3. Reprodução dos cinco casos

```powershell
.\.venv\Scripts\python.exe .\cap09\02_reproduzir.py --caso P01 --destino .\cap09\gerados\windows-P01
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap09\02_reproduzir.py --caso P02 --destino .\cap09\gerados\windows-P02
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap09\02_reproduzir.py --caso P03 --destino .\cap09\gerados\windows-P03
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap09\02_reproduzir.py --caso P04 --destino .\cap09\gerados\windows-P04
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap09\02_reproduzir.py --caso P05 --destino .\cap09\gerados\windows-P05
$LASTEXITCODE
```

Todos exit 0, zero chamadas reais. P01/P02/P05: `aguarda_revisao`; P03: `abstencao_proposta`; P04: `abstencao_local`. As pastas devem conter `pacote.json` e `analise.json`.

## 4. Conferência do significado

```powershell
.\.venv\Scripts\python.exe .\cap09\03_conferir.py --pacote .\cap09\gerados\windows-P01\pacote.json
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap09\05_examinar_limites.py
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap09\solucao_desafio.py
$LASTEXITCODE
```

Todos exit 0. Confira R$ 60,00 **por pessoa por dia**, soma diária, comprovante e finalidade profissional em P01. Confira “cinco dias úteis após a atividade”, sem inventar calendário, em P02. P05 não autoriza IA a aprovar despesas.

São onze contrastes: **nove bloqueados e dois aguardando revisão**. `unidade_alterada` e `condicao_invertida` não são bloqueados pela conferência literal: devem ser rejeitados por significado. A solução explica essa diferença. Não registre esses dois como respostas corretas do modelo.

## 5. Preservação da pasta existente

```powershell
$hashAntesCap09 = (Get-FileHash .\cap09\gerados\windows-P01\pacote.json -Algorithm SHA256).Hash
.\.venv\Scripts\python.exe .\cap09\02_reproduzir.py --caso P01 --destino .\cap09\gerados\windows-P01
$LASTEXITCODE
$hashDepoisCap09 = (Get-FileHash .\cap09\gerados\windows-P01\pacote.json -Algorithm SHA256).Hash
$hashAntesCap09 -eq $hashDepoisCap09
```

Esperado: exit 1, mensagem de destino existente e comparação `True`.

## 6. Bloqueios antes da extensão autenticada

Sem confirmação, é seguro executar mesmo que exista chave na sessão:

```powershell
.\.venv\Scripts\python.exe .\cap09\04_consultar_real.py
$LASTEXITCODE
```

Esperado: exit 2, nenhuma chamada. O teste seguinte **só deve ser feito se a chave estiver ausente**; o bloco verifica isso sem imprimir seu conteúdo:

```powershell
if ([string]::IsNullOrEmpty($env:OPENAI_API_KEY)) {
    .\.venv\Scripts\python.exe .\cap09\04_consultar_real.py --confirmar-envio --destino .\cap09\gerados\windows-sem-chave
    $LASTEXITCODE
} else {
    Write-Output 'Chave presente; teste manual sem chave não executado. O verificador já cobre esse bloqueio.'
}
```

Sem chave: exit 1, pasta não criada. Não remova ou copie a chave para executar esse teste. Se estiver presente, registre “não aplicável; coberto pelo verificador”.

## 7. Fechamento local

Preencha `REGISTRO_WINDOWS.md` a partir do modelo. Confirme 110/110, saídas, fontes, abstenções, preservação e zero operações no banco. A extensão autenticada pode ser registrada como **não executada — opcional**. O capítulo pode ser homologado nesse escopo.

## 8. Extensão autenticada opcional

Só se o leitor decidir executá-la, siga o README: reveja `01_buscar.py --caso P01`, carregue a chave por entrada mascarada se necessário e faça uma consulta com `--confirmar-envio` em pasta nova. Não é necessário executar todos os casos reais.

Guarde metadados, pacote e análise. Confira se há resposta concluída, fontes corretas, unidade por pessoa/dia, condições e uso. Registre variações, abstenção ou bloqueio; não invente texto esperado nem copie uma resposta sintética como evidência de inferência. Não compartilhe chaves. Se a gravação falhar depois da tentativa, não repita automaticamente.
