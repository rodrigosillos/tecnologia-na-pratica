# Homologação Windows — capítulo 3, R01

**Estado em 29/09/2026:** homologação funcional concluída, 36/36 no Windows com Python 3.14.7. Resumo em `../VERIFICACAO_RESUMO.md`. Há ressalva de acentuação no console descrita no README; não se afirma correção já validada. O roteiro abaixo permanece para reprodução e não representa uma nova solicitação de homologação ao autor.

Este roteiro usa o ambiente Python 3.14.7 já homologado no capítulo 2. Não exige reinstalação, ativação de ambiente, alteração de política de execução ou acesso a IA.

1. Extraia o apoio em uma pasta temporária e coloque a pasta `cap03` na raiz `projetos\python-na-pratica`. Se já houver um rascunho de `cap03`, preserve-o em outra pasta antes de usar a extração limpa.
2. Abra o projeto no editor já configurado. Confira que o interpretador continua apontando para `.venv\Scripts\python.exe`.
3. Abra o PowerShell e execute:

```powershell
$pastaLivro = Join-Path $env:USERPROFILE 'projetos\python-na-pratica'
Set-Location -LiteralPath $pastaLivro
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe .\cap03\10_resumo.py
.\.venv\Scripts\python.exe .\cap03\solucoes\desafio.py
.\.venv\Scripts\python.exe .\cap03\verificar_capitulo.py
$LASTEXITCODE
```

Resultados esperados:

- Versão: `Python 3.14.7`.
- Resumo: três despesas, total `127.50`, Transporte com uma despesa e subtotal `35.00`.
- Desafio: P001 e P002 pendentes de data; duas pendências; nenhuma proposta importada.
- Verificador: `Status: aprovado`, `Verificações: 36/36`, `Sistema: Windows | Python: 3.14.7`.
- `$LASTEXITCODE`: `0`, consultado imediatamente após o verificador.
- Acentos de `período`, `Alimentação` e demais mensagens legíveis na sua interface. Não confunda um problema de exibição do terminal com alteração do arquivo UTF-8; registre qualquer diferença observada.

O verificador escreve um JSON em `cap03\resultados`; o caminho exato aparece na última linha. Ele compara saídas em subprocessos UTF-8, exercita variações em memória e registra os hashes dos arquivos. Não comprova visualmente a configuração do editor ou a exibição no PowerShell, por isso o registro manual acompanha o JSON.

## Retorno para fechar a homologação

Envie:

1. O JSON gerado nesta execução de `cap03` (não reutilize o relatório de `cap02`).
2. Uma cópia preenchida de `REGISTRO_WINDOWS_MODELO.md`, salva como `REGISTRO_WINDOWS.md`.

Se houver falha, preserve e envie o relatório reprovado junto da mensagem observada. Não marque o registro como aprovado nem altere os erros intencionais para contornar o resultado. Os caminhos pessoais presentes no JSON servem para conferir o interpretador; não publique o relatório bruto sem revisar esses caminhos.
