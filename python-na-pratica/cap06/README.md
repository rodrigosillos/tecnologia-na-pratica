# Capítulo 6 — apoio R01

**Python na Prática — Automatize tarefas, integre IA e transforme dados em relatórios**  
Rodrigo Sillos · Tecnologia na Prática

Este apoio acrescenta persistência PostgreSQL e relatórios CSV/HTML ao projeto de despesas. O manuscrito explica o percurso; `ROTEIRO_WINDOWS.md` conduz a homologação. Leia primeiro a preparação abaixo.

## Estado de verificação

PostgreSQL nativo/Windows: 66/66 aprovado. Consulte `../VERIFICACAO_RESUMO.md`. Para reproduzir a integração, use PostgreSQL real; não é necessário instalar Node ou PGlite.

## Preparação

1. Extraia `cap06` ao lado de `cap05`, em `projetos\python-na-pratica`, preservando os capítulos anteriores.
2. Use a `.venv` Python 3.14.7 já homologada.
3. Instale as dependências nesta mesma `.venv`:

```powershell
$pastaLivro = Join-Path $env:USERPROFILE 'projetos\python-na-pratica'
Set-Location -LiteralPath $pastaLivro
.\.venv\Scripts\python.exe -m pip install -r .\cap06\requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Se o projeto estiver em outro local, ajuste somente `$pastaLivro`. Não é necessário ativar a venv: os comandos selecionam seu interpretador explicitamente.

## Servidor e banco dedicados

Use PostgreSQL 18 local; a referência nativa é 18.6. O instalador para Windows está em https://www.postgresql.org/download/windows/. Psycopg não instala o servidor. Você pode reutilizar uma instalação PostgreSQL 18 existente, inclusive a do laboratório SQL; crie **outro banco**, `python_na_pratica`. Docker não é requisito.

No SQL Shell (`psql`), conecte ao banco `postgres` como administrador e execute, uma vez:

```sql
CREATE ROLE python_leitor LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;
```

Em seguida use `\password python_leitor`, informe a nova senha duas vezes e execute:

```sql
CREATE DATABASE python_na_pratica OWNER python_leitor ENCODING 'UTF8' TEMPLATE template0;
```

Saia com `\q`. Se os objetos já existirem, confira sua origem e configuração; não apague bancos ou usuários para repetir a preparação. A versão para execução pelo psql está em `sql/preparacao_admin.psql`, com interrupção no primeiro erro. Execute como arquivo apenas se ainda não tiver realizado os passos acima.

Os programas fixam host `127.0.0.1`, banco `python_na_pratica` e usuário `python_leitor`. A senha é solicitada a cada execução e não é gravada. A porta padrão é 5432. Para usar 5433, configure em **cada terminal** que executar clientes Python:

```powershell
$env:PYTHON_PRATICA_PG_PORTA = '5433'
```

Use a porta real da instalação; não mude a porta do servidor só para seguir este exemplo. O verificador nativo exige autenticação por senha e verifica que uma senha incorreta seja rejeitada.

## Primeiros comandos

```powershell
.\.venv\Scripts\python.exe .\cap06\01_conferir_conexao.py
.\.venv\Scripts\python.exe .\cap06\00_preparar_banco.py
```

`sql/esquema.sql` é um modelo lido por `00_preparar_banco.py`: contém `{esquema}` e chaves escapadas do formatador. **Não o cole diretamente no psql.** `sql/conferencias.sql` contém consultas SQL comuns, somente de leitura.

Inicie `servidor_catalogo.py` em um terminal e use outro para importar. Se o catálogo do capítulo 5 já estiver ativo na porta 8765, ele pode ser reutilizado. Os capítulos compartilham o mesmo contrato; apenas um servidor deve ocupar essa porta.

## Mapa do apoio

| Arquivo | Papel |
| --- | --- |
| `00_preparar_banco.py`, `01_conferir_conexao.py` | Preparar estrutura e conferir destino da conexão. |
| `02_importar_csv.py`, `03_reimportar_json.py` | Importar o lote e reaplicá-lo sem duplicar. |
| `04_consultar.py`, `08_consulta_parametrizada.py` | Consultar totais e buscar D002 com parâmetros. |
| `05_exportar.py` | Criar uma nova pasta de relatórios a partir do banco. |
| `06_falha_exportacao.py` | Confirmar D004 e simular uma falha no destino do relatório. |
| `07_conflito_banco.py`, `solucao_desafio.py` | Observar rollback de D005 e aplicar entrada corrigida. |
| `conexao.py`, `banco.py`, `relatorios.py`, `aplicacao.py` | Configuração, persistência, representação e coordenação das etapas. |
| `arquivos.py`, `calculos.py`, `regras.py` | Contrato de entrada preservado do capítulo 5. |
| `cliente_catalogo.py`, `contrato_catalogo.py`, `configuracao.py`, `servidor_catalogo.py` | Catálogo HTTP preservado do capítulo 5 homologado. |
| `dados/` | Sete entradas anteriores e três novas para D004, conflito e solução. |
| `verificar_capitulo.py` | Verificações locais e integração em esquema isolado. |
| `MANIFESTO_SHA256.json` | Integridade de código, SQL, dados e dependências. |

## Executar e interpretar o verificador

```powershell
.\.venv\Scripts\python.exe .\cap06\verificar_capitulo.py
$LASTEXITCODE
```

Ele pede a senha uma vez, inicia um catálogo próprio em porta disponível e cria um esquema temporário `tnp_c06_t_...`, sem usar ou apagar `tnp_cap06`. No encerramento normal remove somente o esquema criado por esta execução. Uma interrupção abrupta pode deixar esse esquema para conferência posterior.

Critério nativo desta revisão: **66/66**, `status: aprovado`, `pendentes: 0`, saída **0**. Qualquer falha retorna 1. A execução abaixo verifica apenas a parte local e retorna 2, mesmo se os 35 testes locais passarem:

```powershell
.\.venv\Scripts\python.exe .\cap06\verificar_capitulo.py --sem-banco
```

Relatórios de motores embarcados retornam 2 e mantêm pendências nativas. Não renomeie esse resultado como aprovação. O relatório JSON em `resultados/` inclui versões, casos, saídas e hashes, sem senha.

## Estados esperados no roteiro manual

| Depois de | Quantidade | Total em reais | Saída |
| --- | ---: | ---: | ---: |
| Primeira importação CSV em tabela vazia | 3 | 127.50 | 0 |
| Reimportação JSON | 3 | 127.50 | 0 |
| Falha de exportação após inserir D004 | 4 | 147.50 | 2 |
| Recuperação somente da exportação | 4 | 147.50 | 0 |
| Conflito D002, com D005 inserida antes no lote | 4 | 147.50 | 1 |
| Solução conferida na origem | 5 | 157.50 | 0 |
| Repetição da solução | 5 | 157.50 | 0 |

Esses gabaritos pressupõem a sequência em uma tabela inicialmente vazia. Se você já executou etapas, consulte o estado e registre isso; não apague dados para fazer o resultado parecer uma primeira execução. O verificador automatizado sempre cria sua própria base de teste isolada.

O relatório CSV usa vírgula e UTF-8 com BOM; valores têm ponto e duas casas. Importe com esse delimitador se sua planilha não detectar a separação. HTML é UTF-8 autossuficiente. Textos potencialmente interpretados como fórmulas recebem apóstrofo no CSV de leitura; o banco e a entrada original permanecem intactos. Não use esse relatório como substituto da origem para reimportar.

## Experimentos e limites

Faça uma cópia da pasta inteira como `cap06_experimentos` antes de editar programas ou dados. O verificador oficial deve continuar no pacote original: o manifesto detectará alterações nos arquivos. Não atualize o manifesto para esconder divergências de uma homologação.

Escopo: uma execução de aplicação por vez, servidor local, catálogo HTTP local e dados fictícios. Não há migração de esquemas personalizados, importadores concorrentes, recuperação automática de commit incerto, serviço público ou chamada de IA neste capítulo. A base confirmada será usada na integração com IA dos próximos capítulos.
