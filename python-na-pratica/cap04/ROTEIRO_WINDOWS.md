# Homologação Windows — capítulo 4, R01

**Estado em 29/09/2026:** homologação funcional concluída pelo autor, 113/113 em Windows com Python 3.14.7. O resumo está em `../VERIFICACAO_RESUMO.md`. A ressalva de acentuação do console permanece registrada. Este roteiro é mantido para reprodução e não representa pedido de repetição da homologação já encerrada.

Reutilize a `.venv` Python 3.14.7 dos capítulos 2 e 3. Não exige reinstalação, dependências novas, conta de IA ou mudança permanente de configuração do sistema.

## Execução

1. Extraia a pasta `cap04` ao lado de `.venv`. Preserve eventuais rascunhos em outra pasta e use uma extração limpa para esta conferência.
2. Confira no editor o interpretador `.venv\Scripts\python.exe`.
3. No PowerShell:

```powershell
$pastaLivro = Join-Path $env:USERPROFILE 'projetos\python-na-pratica'
Set-Location -LiteralPath $pastaLivro
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe .\cap04\07_resumo_csv.py
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap04\08_resumo_json.py
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap04\09_lote_invalido.py
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap04\solucao_desafio.py
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap04\verificar_capitulo.py
$LASTEXITCODE
```

## Resultados esperados

| Programa | Saída relevante | Código |
| --- | --- | ---: |
| `07_resumo_csv.py` | 3 despesas únicas; 0 repetições; 127.50; nenhuma gravação. | 0 |
| `08_resumo_json.py` | Mesmo resultado da entrada CSV. | 0 |
| `09_lote_invalido.py` | Lote bloqueado; data no registro 2; valor no registro 3; nenhum total parcial. | 1 |
| `solucao_desafio.py` | Lote bloqueado; conflito de D002 no registro 4; nenhum total parcial. | 1 |
| `verificar_capitulo.py` | Aprovado 113/113; Windows; Python 3.14.7. | 0 |

As saídas com código 1 acima são intencionais. Não modifique dados ou regras para eliminá-las.

O verificador cria um JSON novo em `cap04\resultados`; o caminho é mostrado no fim. Não reutilize relatórios do capítulo 3. Os subprocessos do verificador usam UTF-8 explicitamente; isso não comprova a apresentação visual de todo console.

## Observação da acentuação

O registro do capítulo 3 relatou caracteres corrompidos no console, embora o JSON estivesse correto. Registre neste capítulo o comportamento realmente observado. Se persistir, marque a aprovação funcional separadamente e mantenha a ressalva visual. Não substitua o arquivo original nem o salve com outra codificação para disfarçar o problema.

O roteiro não altera a página de código do terminal nem promete corrigir a causa sem diagnóstico. Uma eventual mudança futura de configuração terá sua própria conferência.

## Retorno

Envie o relatório JSON novo e `REGISTRO_WINDOWS.md` preenchido a partir do modelo. Se houver falha inesperada, preserve o JSON e a mensagem. Não é necessário repetir a instalação do Python ou a homologação dos capítulos anteriores.
