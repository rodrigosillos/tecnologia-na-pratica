# Python na Prática — apoio do capítulo 2, R02

Este pacote acompanha **Preparando o ambiente e executando os primeiros programas**. Esta pasta contém os exemplos da etapa e integra o laboratório reunido do livro.

## Preparação

Extraia a pasta `cap02` dentro da raiz do projeto `python-na-pratica`. O caminho do primeiro exemplo deve terminar em `python-na-pratica/cap02/primeiro_programa.py`.

A pasta `.venv` deve ser criada na raiz do projeto, ao lado de `cap02`. Ela não é distribuída no ZIP. Use o capítulo para instalar e selecionar Python 3.14.7.

## Execução no Windows/PowerShell

Na raiz do projeto, depois de instalar o Python Install Manager:

```powershell
pymanager install 3.14.7
pymanager exec -V:3.14.7 -m venv .venv
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
.\.venv\Scripts\python.exe .\cap02\primeiro_programa.py
.\.venv\Scripts\python.exe .\cap02\variacao_programa.py
.\.venv\Scripts\python.exe .\cap02\diagnostico_ambiente.py
.\.venv\Scripts\python.exe .\cap02\solucoes\desafio.py
```

O diagnóstico deve indicar o Python da `.venv`, versão 3.14.7, pasta atual igual à raiz do projeto e `Ambiente virtual: True`.

## Equivalentes Linux/macOS

Com Python 3.14 instalado e o comando `python3.14` disponível, na raiz do projeto:

```bash
python3.14 -m venv .venv
./.venv/bin/python --version
./.venv/bin/python -m pip --version
./.venv/bin/python ./cap02/primeiro_programa.py
./.venv/bin/python ./cap02/variacao_programa.py
./.venv/bin/python ./cap02/diagnostico_ambiente.py
./.venv/bin/python ./cap02/solucoes/desafio.py
```

Linux foi executado nesta entrega com Python 3.14.7. macOS não foi executado. Se o comando inicial não for encontrado, configure o Python 3.14 para seu sistema e confirme a versão; não substitua silenciosamente por outro Python.

## Gabaritos

| Arquivo | Quantidade prevista |
| --- | ---: |
| `primeiro_programa.py` | 3 |
| `variacao_programa.py` | 4 |
| `solucoes/desafio.py` | 5 |

Nos três programas, a primeira linha é `Assistente de despesas`, a segunda é `Registros previstos: N`, com a quantidade correspondente, e a terceira é `IA: nenhuma chamada executada`.

Esses programas exibem mensagens e uma expressão aritmética. Ainda não leem registros, gravam despesas ou chamam IA.

## Verificador

No Windows:

```powershell
.\.venv\Scripts\python.exe .\cap02\verificar_capitulo.py
```

No Linux/macOS:

```bash
./.venv/bin/python ./cap02/verificar_capitulo.py
```

O utilitário confere 12 condições e cria um arquivo novo em `cap02/resultados/`. O nome inclui data e hora. Nenhum resultado anterior é sobrescrito. Ele cria e remove uma pasta temporária para o ensaio de caminho incorreto; não instala pacotes ou executa comandos de PowerShell.

Exige a linha 3.14 e um ambiente virtual com pip. Registra o patch realmente usado; o patch de referência desta revisão é 3.14.7. Os subprocessos de verificação usam saída UTF-8 explicitamente, de modo que essa captura não substitui a conferência visual dos acentos no terminal Windows.

Os arquivos em `erros_intencionais` devem falhar. O verificador aprova o caso quando observa o tipo de erro e o código de saída esperados. Não corrija esses arquivos na cópia de referência.

Se personalizar um exemplo, preserve sua versão e execute a comparação do gabarito em uma cópia intacta. O verificador compara as saídas; uma divergência intencional do exercício não significa necessariamente um defeito em sua solução.

## Conferência Windows

Windows: 12/12 verificações aprovadas com Python 3.14.7. Siga `ROTEIRO_WINDOWS.md` para reproduzir a conferência. O resumo de homologação está em `../VERIFICACAO_RESUMO.md`. Não há dependências de banco ou chamadas a serviços de IA nesta etapa.

