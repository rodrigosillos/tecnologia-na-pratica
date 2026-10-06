# Capítulo 2 — conferência Windows/PowerShell

**Estado na entrega R02:** homologação Windows recebida e conferida em 29/09/2026; 12/12 verificações aprovadas. Este roteiro permanece disponível para novas execuções.  
**Referência:** Python 3.14.7; comandos no PowerShell; editor VS Code.  
**Finalidade:** produzir evidências da instalação, do roteiro e dos exemplos no sistema principal do livro.

Use uma pasta de laboratório. O roteiro não altera políticas de execução e usa o Python pelo caminho explícito, sem exigir ativação da `.venv`.

## 1. Anote o ambiente

No PowerShell, consulte:

```powershell
$PSVersionTable.PSVersion.ToString()
[System.Environment]::OSVersion.VersionString
```

Anote também a versão do VS Code apresentada em Help/Ajuda → About/Sobre. Esses itens ficam pendentes até serem observados; não preencha com as versões do ambiente Linux.

## 2. Prepare o projeto

Instale o Python Install Manager pelo canal oficial indicado no capítulo. Abra uma nova sessão do PowerShell e execute, uma linha por vez:

```powershell
pymanager install 3.14.7
pymanager exec -V:3.14.7 --version
$pastaLivro = Join-Path $env:USERPROFILE 'projetos\python-na-pratica'
New-Item -ItemType Directory -Path $pastaLivro -Force
Set-Location -LiteralPath $pastaLivro
Get-Location
```

Extraia `cap02` do ZIP para essa raiz. Confirme que `cap02\primeiro_programa.py` existe. Preserve exercícios anteriores antes de substituir qualquer arquivo.

Crie o ambiente se ainda não houver uma `.venv` adequada ao projeto:

```powershell
pymanager exec -V:3.14.7 -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
```

No editor, abra a raiz, instale a extensão Python da Microsoft e selecione o interpretador da `.venv` com `Python: Select Interpreter`. Confira a seleção visualmente.

## 3. Execute os programas

```powershell
.\.venv\Scripts\python.exe .\cap02\primeiro_programa.py
.\.venv\Scripts\python.exe .\cap02\variacao_programa.py
.\.venv\Scripts\python.exe .\cap02\diagnostico_ambiente.py
.\.venv\Scripts\python.exe .\cap02\solucoes\desafio.py
```

Compare as quantidades com 3, 4 e 5. No diagnóstico, confirme versão, caminho do executável, pasta atual e `True`. Confira os acentos de `Versão` e `Pasta atual` sem caracteres corrompidos.

Teste também o modo interativo: inicie `.\.venv\Scripts\python.exe`, digite `print("Olá, Python!")`, depois `3 + 1` e, por último, `quit()`. A frase e o número 4 devem aparecer antes de voltar ao PowerShell.

## 4. Observe os erros intencionais

Na raiz do projeto, execute separadamente:

```powershell
.\.venv\Scripts\python.exe .\primeiro_programa.py
```

Esse arquivo não está na raiz. Espera-se erro de abertura. Em seguida, corrija o caminho para `cap02\primeiro_programa.py` e confirme a execução normal.

```powershell
.\.venv\Scripts\python.exe .\cap02\erros_intencionais\aspas_incompletas.py
.\.venv\Scripts\python.exe .\cap02\erros_intencionais\nome_incorreto.py
```

Espere `SyntaxError` no primeiro e `NameError` no segundo. Não altere os arquivos intencionais da cópia de referência.

## 5. Repita em outra sessão e gere o relatório

Feche e abra novamente o PowerShell, volte à raiz do projeto usando o comando do capítulo e repita o diagnóstico e o desafio. Execute:

```powershell
.\.venv\Scripts\python.exe .\cap02\verificar_capitulo.py
```

O resultado esperado é `Status: aprovado` e `Verificações: 12/12`, com `Sistema: Windows`. Guarde o JSON novo em `cap02\resultados`. Ele contém caminhos locais da execução para ajudar no diagnóstico.

## 6. Registro de conferência

O estado de referência está resumido em `../VERIFICACAO_RESUMO.md`. A tabela abaixo é um modelo em branco para sua execução. Preencha somente após observar o resultado.

| Item | Resultado / evidência |
| --- | --- |
| Windows e PowerShell | Pendente. |
| Instalação e seleção de Python 3.14.7 | Pendente. |
| Criação da `.venv` e caminho do pip | Pendente. |
| Seleção do interpretador no VS Code | Pendente. |
| Modo interativo e retorno ao PowerShell | Pendente. |
| Quantidades 3, 4 e 5 | Pendente. |
| Acentos legíveis | Pendente. |
| Caminho incorreto e correção | Pendente. |
| SyntaxError e NameError intencionais | Pendente. |
| Nova sessão: diagnóstico e desafio | Pendente. |
| JSON do verificador em Windows | Pendente. |

Para análise editorial, envie o relatório JSON e o registro preenchido. Se houver divergência, inclua o comando executado e a mensagem correspondente. A aprovação das 12 verificações Python não preenche automaticamente os itens de instalação, editor e terminal.
