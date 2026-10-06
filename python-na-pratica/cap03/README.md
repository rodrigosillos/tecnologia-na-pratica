# Python na Prática — apoio do capítulo 3 (R01)

**Capítulo:** Dados, decisões e repetições em Python.  
**Ambiente de referência:** Python 3.14.7; biblioteca padrão, sem instalações adicionais.  
**Dados:** fictícios; três despesas de 10/09/2026, total de R$ 127,50.  
**IA:** nenhuma chamada, conta ou chave necessária.

## Instalação do apoio

Extraia o ZIP e coloque `cap03` na raiz do projeto `projetos\python-na-pratica`, ao lado de `.venv` e `cap02`. Evite uma pasta `cap03\cap03`. Reutilize o ambiente virtual homologado no capítulo 2.

Na raiz do projeto, no PowerShell:

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe .\cap03\01_tipos.py
.\.venv\Scripts\python.exe .\cap03\10_resumo.py
.\.venv\Scripts\python.exe .\cap03\verificar_capitulo.py
```

Em sistemas POSIX com o ambiente equivalente, os comandos correspondentes são:

```bash
.venv/bin/python cap03/01_tipos.py
.venv/bin/python cap03/10_resumo.py
.venv/bin/python cap03/verificar_capitulo.py
```

Não é necessário ativar o ambiente. Use o interpretador da `.venv` diretamente. A criação da `.venv` continua sendo assunto do capítulo 2, não deste pacote.

## Mapa dos arquivos

| Arquivo ou pasta | Finalidade |
| --- | --- |
| `01_tipos.py` | Texto, inteiro, booleano e ausência de valor. |
| `02_conversoes.py` | Texto versus cálculo e a armadilha de `bool("False")`. |
| `03_dinheiro.py` | Decimal criado de texto, sem passagem por float. |
| `04_datas.py` | Data de calendário e intervalo com fim exclusivo. |
| `05_listas.py` | Posição, presença e acréscimo em uma lista didática. |
| `06_dicionarios.py` | Campos nomeados de uma despesa. |
| `07_condicoes.py` | Triagem simples com if, elif e else. |
| `08_repeticoes.py` | Contagem e soma acumulada. |
| `09_selecao.py` | IDs selecionados, preservando a origem. |
| `10_resumo.py` | Três despesas completas; resumo por período e categoria. |
| `desafio_base.py` | Dados e ponto de partida do desafio, sem solução. |
| `solucoes/` | Três exercícios independentes e a triagem de propostas. |
| `erros_intencionais/` | Três falhas esperadas, executadas isoladamente. |
| `verificar_capitulo.py` | Verificador auxiliar; não é conteúdo obrigatório de sintaxe. |
| `evidencias/` | Pasta para guardar os registros de sua própria execução. |
| `ROTEIRO_WINDOWS.md` | Procedimento de homologação nativa deste pacote. |
| `REGISTRO_WINDOWS_MODELO.md` | Modelo ainda não preenchido; não é evidência de aprovação. |
| `MANIFESTO_SHA256.json` | Identifica os 19 arquivos Python desta revisão. |

O verificador gera `resultados/` na execução. Os relatórios têm nome com data e hora UTC; execuções novas não sobrescrevem as anteriores. Não inclua um ambiente `.venv` dentro do pacote.

## Resultados esperados

`10_resumo.py` deve mostrar:

```text
Despesas no período: 3
Total em reais: 127.50
Categoria: Transporte
Despesas da categoria: 1
Subtotal em reais: 35.00
```

`solucoes/desafio.py` mantém as duas propostas pendentes por falta de data. Nenhuma delas é adicionada à base de despesas.

O verificador deve aprovar **36/36** verificações, com código de saída zero. Três casos aprovados correspondem à identificação de erros intencionais: `ValueError`, `KeyError` e `TypeError`. O verificador exige a linha Python 3.14 e ambiente virtual; registra a versão exata utilizada. A execução de produção foi feita em 3.14.7.

Faça os exercícios em cópias: alterar os originais ou as soluções pode mudar o resultado da verificação. Arquivos de rascunho adicionais com extensão `.py` também aparecerão no inventário de hashes do relatório. Para a homologação, prefira uma extração limpa deste pacote.

## Escopo e limites

Os arquivos são programas de estudo com entradas internas conhecidas. Eles não implementam validação completa, importação atômica, detecção de duplicidades, persistência, integração HTTP ou integração real com IA. O terceiro caminho da triagem significa encaminhar para validação completa, não autorizar uma importação.

As variações do verificador alteram cópias do código em memória; não modificam os exemplos em disco. Não há acesso à rede, instalação de dependências ou chamada a comandos de PowerShell pelo verificador. Ele executa arquivos Python locais deste pacote.

Homologação funcional Windows concluída: 36/36 em Python 3.14.7 e 19/19 hashes técnicos conferidos. Consulte `../VERIFICACAO_RESUMO.md`.

Há uma ressalva de exibição: a observação do registro manual relata acentos corrompidos no console PowerShell com página de código 850, embora a caixa de legibilidade esteja marcada. Os resultados UTF-8 do JSON estão corretos. A exibição integral do console não é considerada homologada nem corrigida nesta atualização. A ressalva acompanha a consolidação das instruções Windows e não altera a aprovação funcional dos programas.

Esta distribuição preserva os 19 arquivos Python e o manifesto técnico da revisão homologada.
