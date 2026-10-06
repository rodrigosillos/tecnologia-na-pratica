# Capítulo 11 — Organizando uma execução confiável

Python na Prática · Rodrigo Sillos · Tecnologia na Prática · R01

## Objetivo e limites

Identificar uma importação confirmada, repetir apenas a exportação pendente e limitar tentativas de leitura HTTP. O relatório usa o retrato armazenado junto com a importação. Uma chamada de IA não faz parte deste capítulo: não há chave, modelo, inferência ou cobrança. As extensões autenticadas dos capítulos 7–10 continuam opcionais.

O fluxo pressupõe **uma execução ativa por vez**, um usuário do laboratório, arquivos locais e até 1000 despesas acumuladas neste esquema. Não há proteção para vários escritores, sincronização distribuída, retenção automática de recibos ou garantia contra perda física do disco. A publicação da pasta usa renomeação no mesmo diretório; não equivale a uma transação entre banco e sistema de arquivos.

O esquema `tnp_cap11` é separado de `tnp_cap06`. A base `python_na_pratica`, o usuário `python_leitor` e a senha são os preparados no capítulo 6. Não execute novamente o SQL administrativo para criar o usuário/banco. `preparar` cria somente os objetos deste capítulo e preserva dados existentes.

## Ambiente

Python 3.14.7, Psycopg 3.3.6 e Requests 2.34.2; dependências fixadas em `requirements.txt`, iguais às do capítulo 10. O SDK OpenAI continua no ambiente compartilhado do livro, mas não é usado por estes programas. PostgreSQL 18, patch registrado no resultado; o ambiente homologado anteriormente pelo autor é 18.6 em Docker local.

Na raiz `projetos\python-na-pratica`, extraia este ZIP para obter `cap11`. Os comandos a seguir partem dessa raiz:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\cap11\requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe .\cap11\verificar_capitulo.py
.\.venv\Scripts\python.exe .\cap11\01_tentativas.py --cenario recupera
.\.venv\Scripts\python.exe .\cap11\app.py --help
```

O verificador sem banco executa **80 verificações**, incluindo nove comandos e ensaios HTTP locais. Esse modo não homologa SQL, autenticação PostgreSQL ou commit.

Para o fluxo com banco, siga `ROTEIRO_WINDOWS.md`. Cada comando solicita a senha do usuário do laboratório sem exibi-la. `PYTHON_PRATICA_PG_PORTA` permite mudar somente a porta; o padrão é 5432. Host, banco e usuário ficam restritos ao laboratório. Nunca cole a senha no comando, no registro ou no chat.

## Comandos

| Comando | Efeito |
| --- | --- |
| `app.py preparar` | Cria/verifica o esquema do capítulo. |
| `app.py executar --execucao ID --entrada ARQUIVO` | Consulta recibo, importa se necessário e exporta. |
| `app.py status --execucao ID` | Consulta recibo e confere os arquivos na raiz escolhida. |
| `app.py exportar --execucao ID` | Exporta exclusivamente o retrato do recibo confirmado. |

`--destino` define a **raiz** dos relatórios; a pasta final será `RAIZ/ID`. Padrão: `cap11/gerados/relatorios`. `--logs` define a pasta dos logs; padrão: `cap11/gerados/logs`. Caminhos informados são relativos ao diretório corrente; padrões são relativos ao arquivo `app.py`.

`executar` aceita `--catalogo http://127.0.0.1:8765/categorias` e `--tentativas 1` a `5` (padrão 3). O catálogo é necessário apenas antes de uma importação nova. O mesmo ID exige os mesmos bytes do arquivo original, inclusive espaços e quebras de linha. Um novo ID pode receber outro formato equivalente; a identidade das despesas evita duplicação. Não altere o arquivo para tentar resolver uma confirmação incerta.

| Exit | Significado |
| ---: | --- |
| 0 | Comando concluído; em `preparar`, esquema pronto; em `status`, relatório conferido. |
| 1 | Entrada/contrato/vínculo bloqueado ou recibo ausente. |
| 2 | Uso incorreto dos argumentos (`argparse`). |
| 3 | Recibo confirmado; exportação ausente, incompatível ou com falha. |
| 4 | Falha de banco, arquivo ou log; estado exige consulta. Não presume rollback. |

Os exemplos independentes têm saídas próprias: erro intencional → 1; catálogo esgotado ou inválido → 1; ensaio recuperado e solução do desafio → 0. No verificador, 0 significa nenhum teste reprovado; consulte também `status`, `modo` e `pendentes`.

## Contrato do relatório

Quatro arquivos: `despesas.csv` (UTF-8 com BOM), `despesas.html` (UTF-8), `recibo.json` e `manifesto.json` (UTF-8). O recibo inclui execução, hash dos bytes de entrada, novas/existentes e retrato de **todas as despesas no esquema no instante dessa importação**. As contagens novas/existentes referem-se ao lote; quantidade/total do retrato referem-se ao acumulado.

Um destino existente só é reutilizado se nomes, bytes e tamanhos coincidirem com a renderização do recibo. Não há substituição de arquivo divergente. Escolha outra raiz e preserve a anterior para investigação. O manifesto detecta divergência; não é assinatura digital nem prova contra adulteração deliberada do banco e dos arquivos.

## Organização

- `app.py`: argumentos, configuração e códigos de saída.
- `aplicacao.py`: ordem das etapas.
- `banco.py`, `conexao.py`, `recibos.py`, `sql/esquema.sql`: importação, recibo e conferência.
- `arquivos.py`, `regras.py`: entrada e validação.
- `catalogo.py`, `contrato_catalogo.py`, `tentativas.py`: HTTP e repetição limitada.
- `exportacao.py`: CSV/HTML e publicação da pasta.
- `eventos.py`: eventos UTF-8 por tentativa.
- `servidor_catalogo.py`: servidor didático fornecido desde o capítulo 5.
- `01_tentativas.py`, `02_erro_intencional.py`, `solucao_desafio.py`: exercícios isolados.
- `verificar_capitulo.py`: verificações locais e integração opcional no comando, necessária para homologar o percurso com PostgreSQL.

A conexão do capítulo 6 mantém as restrições locais; foi alterado somente o nome da aplicação para `tnp_cap11`. As regras de despesas e o contrato/servidor do catálogo foram preservados. A integração de saídas revisadas dos capítulos de IA fica para o capítulo 12.

## Verificação

Windows: parte local 80/80 e PostgreSQL nativo 97/97, `integracao_nativa`, pendentes 0. Consulte `../VERIFICACAO_RESUMO.md` e reproduza com `ROTEIRO_WINDOWS.md` quando necessário.

