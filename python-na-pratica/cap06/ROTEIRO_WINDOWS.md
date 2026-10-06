# Homologação Windows — capítulo 6 R01

Execute na raiz `projetos\python-na-pratica`, com Python 3.14.7 e PostgreSQL 18 nativo. Use o README para preparar dependências, usuário, banco e porta. Preencha `REGISTRO_WINDOWS_MODELO.md`, salvando uma cópia como `REGISTRO_WINDOWS.md`. Não inclua senha, endereço pessoal ou string de conexão com credenciais.

## 1. Ambiente e integridade

```powershell
.\.venv\Scripts\python.exe --version
$PSVersionTable.PSVersion
chcp
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe .\cap06\01_conferir_conexao.py
$LASTEXITCODE
.\.venv\Scripts\python.exe .\cap06\00_preparar_banco.py
$LASTEXITCODE
```

Anote a versão real do servidor, a porta e a codificação do console. A referência é PostgreSQL 18.6; registre qualquer diferença de patch. Não altere globalmente a configuração do terminal para ocultar a ressalva cp850 do capítulo 5.

## 2. Verificador nativo independente

```powershell
.\.venv\Scripts\python.exe .\cap06\verificar_capitulo.py
$LASTEXITCODE
```

**Esperado: 66/66, nenhuma falha ou pendência, modo `integracao_nativa`, status `aprovado`, saída 0.** Confira em `postgresql` a versão observada, usuário, banco e remoção do esquema temporário. O verificador inicia sua própria API, portanto não exige servidor de catálogo manual nesta etapa.

Copie o JSON cujo caminho foi impresso para `cap06/evidencias/relatorio-windows-python314.json`, preservando também o original. Não copie um JSON antigo só porque ele tem o nome esperado. Se houver falhas, registre nome, tipo e mensagem; não modifique o status manualmente.

## 3. Sequência manual de programas

O gabarito abaixo parte de `tnp_cap06.despesas` vazio. O verificador não modifica esse esquema. Se já houver dados de experiências anteriores, registre o estado e considere esse fato nas contagens de novas/existentes. Não há comando de limpeza automática neste roteiro.

Em um terminal, na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe .\cap06\servidor_catalogo.py
```

Mantenha-o aberto. Se o servidor do capítulo 5 estiver em execução, reutilize-o. No segundo terminal execute cada linha da tabela como no exemplo, conferindo `$LASTEXITCODE` imediatamente depois do programa e antes de outro comando nativo:

```powershell
.\.venv\Scripts\python.exe .\cap06\02_importar_csv.py
$LASTEXITCODE
```

| Ordem | Programa | Mensagem ou estado esperado | Exit |
| ---: | --- | --- | ---: |
| 1 | `02_importar_csv.py` | Importação confirmada; novas 3, existentes 0, repetições 0. | 0 |
| 2 | `04_consultar.py` | 3; 127.50. Alimentação 12.50, Materiais 80.00, Transporte 35.00; uma em cada categoria. | 0 |
| 3 | `08_consulta_parametrizada.py` | Corrida para visitar cliente; 35.00. | 0 |
| 4 | `03_reimportar_json.py` | Novas 0, existentes 3; consulta permanece 3 / 127.50. | 0 |
| 5 | `00_preparar_banco.py` | Estrutura preservada; consulta permanece 3 / 127.50. | 0 |
| 6 | `05_exportar.py` | Pasta nova com CSV, HTML e estado.json; total 127.50. | 0 |
| 7 | `06_falha_exportacao.py` | Novas 1; exportação pendente; importação permanece confirmada. | 2 |
| 8 | `04_consultar.py` | 4 / 147.50. | 0 |
| 9 | `05_exportar.py` | Nova exportação concluída, total 147.50; anterior preservada. | 0 |
| 10 | `07_conflito_banco.py` | Lote não confirmado: conflito com despesa já gravada: D002. | 1 |
| 11 | `04_consultar.py` | 4 / 147.50; D005 não ficou gravada. | 0 |
| 12 | `solucao_desafio.py` | Novas 1, existentes 1. | 0 |
| 13 | `04_consultar.py` | 5 / 157.50. | 0 |
| 14 | `solucao_desafio.py` novamente | Novas 0, existentes 2; consulta permanece 5 / 157.50. | 0 |
| 15 | `05_exportar.py` | Relatório final 5 / 157.50, com os anteriores preservados. | 0 |

Confira D005 no CSV final e sua ausência no relatório de 147.50. Isso acrescenta uma conferência observável do rollback às mensagens de erro.

## 4. Exercício de repetição dentro do arquivo

Copie a pasta inteira para `cap06_experimentos`, sem editar `cap06`. Na cópia de `03_reimportar_json.py`, troque somente `validas.json` por `repetidas.json`. Execute o programa da cópia usando a mesma venv. Esperado: novas 0, existentes 3, repetições na entrada 1, saída 0. O banco mantém o total que já tinha antes do exercício, inclusive D004/D005 se você completou o roteiro.

Não execute o verificador oficial sobre a cópia alterada: a conferência de integridade acusaria a modificação corretamente.

## 5. Catálogo desligado

Encerre o servidor de catálogo com Ctrl+C e execute:

```powershell
.\.venv\Scripts\python.exe .\cap06\02_importar_csv.py
$LASTEXITCODE
```

Esperado: saída 1 e `Lote não confirmado: API: falha de comunicação HTTP`. A conexão recusada e ConnectTimeout são tratados como falha de comunicação. Consulte com `04_consultar.py`: o banco continua 5 / 157.50 após a sequência completa. Consultar e exportar não dependem do catálogo; execute `05_exportar.py` para confirmar a recuperação independente.

## 6. Apresentação e evidências

- Abra o HTML final: cinco despesas, total 157.50 e categorias Alimentação 12.50, Materiais 110.00, Transporte 35.00.
- Confira acentos em Café, Alimentação e escritório, descrição completa, cabeçalhos e ausência de cortes. Teste janela larga e estreita; a tabela pode rolar horizontalmente.
- Importe o CSV com vírgula e UTF-8: cinco linhas e valores com duas casas.
- Abra o JSON da exportação e o do verificador como UTF-8. Se o console tiver acentos corrompidos, registre separadamente; não classifique automaticamente os arquivos UTF-8 como corrompidos.
- Preencha o registro com versão, resultados, caminhos e ressalvas. Só conclua homologação quando o verificador nativo e o roteiro manual estiverem conferidos.

Envie o relatório nativo e `REGISTRO_WINDOWS.md`. Se houver alteração de código, envie também o ZIP atualizado e seu SHA-256, registrando o motivo e repetindo as verificações afetadas.
