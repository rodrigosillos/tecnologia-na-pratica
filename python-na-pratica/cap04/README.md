# Python na Prática — apoio do capítulo 4 (R01)

**Funções, arquivos e validação** · Rodrigo Sillos · Tecnologia na Prática.

Python de referência: **3.14.7**, em ambiente virtual. Apenas biblioteca padrão. Dados fictícios, sem rede, credenciais, banco de dados ou chamadas de IA.

## Preparação e execução

Coloque `cap04` na raiz `projetos\python-na-pratica`, ao lado de `.venv` e das pastas dos capítulos anteriores. Reutilize o ambiente já homologado; não é necessário ativá-lo ou instalar bibliotecas.

No PowerShell, a partir dessa raiz:

```powershell
.\.venv\Scripts\python.exe .\cap04\01_funcoes.py
.\.venv\Scripts\python.exe .\cap04\07_resumo_csv.py
.\.venv\Scripts\python.exe .\cap04\08_resumo_json.py
.\.venv\Scripts\python.exe .\cap04\10_primeiro_teste.py
.\.venv\Scripts\python.exe .\cap04\verificar_capitulo.py
$LASTEXITCODE
```

Equivalentes POSIX, com `.venv` preparada:

```bash
.venv/bin/python cap04/07_resumo_csv.py
.venv/bin/python cap04/08_resumo_json.py
.venv/bin/python cap04/verificar_capitulo.py
```

Produção executada no Linux com Python 3.14.7. **Homologação funcional Windows concluída em 29/09/2026: 113/113, zero falhas.** O autor executou os novos scripts na mesma `.venv`, e os 26 hashes coincidem com o pacote entregue. A ressalva visual de acentuação no console permanece aberta; o JSON UTF-8 está correto.

## Ordem de estudo

| Arquivo | Objetivo |
| --- | --- |
| `01_funcoes.py` | Parâmetro, chamada, acumulador local e retorno. |
| `02_objetos.py` | Instância, método e checagem de tipo. |
| `03_importacao_escopo.py` | Importação da função de outro módulo; escopo. |
| `04_tratar_erro.py` | Regra que levanta ValueError e tratamento explícito. |
| `05_ler_csv.py` | Observação de leitura CSV da base conhecida, sem validação completa. |
| `06_ler_json.py` | Observação de leitura JSON da base conhecida, sem validação completa. |
| `07_resumo_csv.py` | Aplicação com leitura e validação completas deste capítulo. |
| `08_resumo_json.py` | Mesmo percurso com entrada JSON. |
| `09_lote_invalido.py` | Bloqueio do lote por data impossível e valor com vírgula. |
| `10_primeiro_teste.py` | Duas expectativas explicadas no texto. |
| `solucao_exercicio_02.py` | Repetição idêntica não aumenta o total. |
| `solucao_exercicio_03.py` | Valor JSON numérico rejeitado; dinheiro deve chegar como texto. |
| `solucao_desafio.py` | Mesmo ID com valor diferente bloqueia o lote. |

Módulos usados pela aplicação: `calculos.py`, `regras.py`, `arquivos.py` e `aplicacao.py`. Não os execute esperando uma interface: definem funções para os programas numerados. Não renomeie módulos próprios para `csv.py`, `json.py` ou `decimal.py`.

## Dados e gabaritos

| Entrada | Resultado da aplicação |
| --- | --- |
| `dados/validas.csv` e `dados/validas.json` | 3 únicas, 0 repetições, 127.50; código zero. |
| `dados/invalidas.csv` | Erros nos registros 2 e 3; lote bloqueado; código 1. |
| `dados/repetidas.json` | 3 únicas, 1 repetição, 127.50; código zero. |
| `dados/valor_numerico.json` | Erro no campo valor do registro 1; código 1. |
| `dados/desafio.json` | Conflito no registro 4 (D002); lote bloqueado; código 1. |
| `dados/descricao_com_virgula.csv` | A primeira descrição é um campo único, entre aspas no CSV. |

O cabeçalho CSV é `id,data,descricao,categoria,valor`, nessa ordem, com separador vírgula. Leitura UTF-8, aceitando BOM inicial. No JSON, a raiz é uma lista e a ordem das chaves não importa. Chaves repetidas são rejeitadas.

## Contrato da etapa

- Campos exatos: `id`, `data`, `descricao`, `categoria`, `valor`; todos obrigatórios, sem campos extras.
- ID: `D` seguido por 3 a 8 algarismos ASCII.
- Data: texto `AAAA-MM-DD`, calendário válido.
- Descrição: texto não vazio, até 120 caracteres, sem espaços nas extremidades.
- Categoria: texto exato `Alimentação`, `Transporte` ou `Materiais`.
- Valor: **texto**, 1 a 7 algarismos ASCII, ponto e 2 casas; positivo, até `9999999.99`. Zeros à esquerda aceitos. Não há arredondamento para aceitar entradas.
- Tamanho máximo: 1 MiB por arquivo; 1.000 registros por lote, contando repetições.
- Lotes vazios estruturados são aceitos; arquivo sem conteúdo é rejeitado. Linhas fisicamente vazias no CSV são ignoradas pelo leitor.
- Igualdade de duplicatas é comparada após normalização de data e valor, incluindo os demais campos.
- Um erro bloqueia a devolução de despesas do lote; o primeiro erro de cada registro é informado. Posições são de registros lógicos, não necessariamente de linhas físicas do CSV.

## Verificador e evidências

Resultado esperado: **113/113**, código zero. Os casos incluem valores válidos e inválidos, datas, estrutura dos registros, repetição idêntica e conflito, CSV com aspas/BOM/CRLF, JSON malformado ou ambíguo, fronteiras de tamanho, arquivo ausente e preservação das fontes e dados.

O verificador executa programas locais, usa arquivos temporários para os casos adicionais e gera um novo relatório em `resultados/`. Registra hashes de **19 arquivos Python e 7 arquivos de dados**, 26 no total. O inventário também pode listar rascunhos `.py` acrescentados pelo leitor; para homologar, use uma extração limpa.

Windows: 113/113 aprovado. Consulte `../VERIFICACAO_RESUMO.md`. `MANIFESTO_SHA256.json` identifica os arquivos técnicos desta revisão.

Os programas `09_lote_invalido.py`, `solucao_exercicio_03.py` e `solucao_desafio.py` terminam com código 1 **por decisão esperada**. O arquivo `erros_intencionais/data_impossivel.py` mostra uma exceção não tratada. Esses casos não devem ser alterados para terminar com zero. O verificador distingue rejeição correta de falha inesperada.

## Windows e acentuação

O roteiro e o modelo permanecem para reprodução. Não é necessária nova execução pelo autor para fechar a homologação funcional, já concluída com as evidências recebidas. A ressalva de acentos observada no console do capítulo 3 permanece registrada: ela não foi declarada corrigida. A visualização do terminal deve ser descrita honestamente, separada da aprovação funcional e do conteúdo UTF-8 do JSON. Não marque a legibilidade como aprovada se ainda houver caracteres corrompidos.

## Limites

Nenhuma despesa é gravada. A proteção do lote é uma etapa de validação em memória, não uma transação de banco. Não há verificação de ID contra importações anteriores, catálogo HTTP, exportação CSV/HTML de despesas confirmadas ou integração de IA. Esses comportamentos pertencem a capítulos posteriores.

As entradas originais são abertas para leitura. Faça exercícios em cópias. Para o controle negativo explicado no capítulo, copie **a pasta inteira** e altere o módulo de cálculos apenas nessa cópia; execute o teste da mesma pasta.
