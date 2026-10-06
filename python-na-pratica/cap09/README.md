# Capítulo 9 — RAG: consultando documentos com fontes

Python na Prática • Tecnologia na Prática • Rodrigo Sillos • R01

Laboratório de consulta a **dois documentos fictícios em Markdown, seis seções**. Busca textual local, contexto visível, resposta estruturada e conferência das referências. Não importa despesas, não consulta banco e não aprova pagamentos.

## Ambiente e instalação

Extraia `cap09` dentro de `projetos\python-na-pratica`, ao lado de `.venv`. Os comandos abaixo partem dessa pasta do projeto, no PowerShell. Não é necessário executar servidores dos capítulos anteriores.

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\cap09\requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe .\cap09\verificar_capitulo.py
```

Dependências iguais às do capítulo 8: Python 3.14.7, OpenAI SDK 3.24.0 e as mesmas vinte versões fixadas. O verificador exige Python 3.14 em uma venv e confere as dependências. Verificação Windows: **110/110 aprovada no escopo local**; veja `../VERIFICACAO_RESUMO.md`. O suporte não contém ambiente virtual.

## Percurso principal: reprodução sintética

```powershell
.\.venv\Scripts\python.exe .\cap09\01_buscar.py --caso P01
.\.venv\Scripts\python.exe .\cap09\02_reproduzir.py --caso P01
.\.venv\Scripts\python.exe .\cap09\03_conferir.py
.\.venv\Scripts\python.exe .\cap09\05_examinar_limites.py
.\.venv\Scripts\python.exe .\cap09\solucao_desafio.py
```

A reprodução não executa um modelo, não usa rede nem lê a chave da sessão. Os textos, IDs de respostas e contagens de tokens dos casos são **sintéticos**, criados para estudar o fluxo. O verificador testa o SDK com transporte HTTP simulado; isso não equivale a uma chamada autenticada.

| Caso | Recuperação padrão | Resultado da reprodução |
| --- | --- | --- |
| P01 — limite de alimentação | POL-002, 7 pontos | `aguarda_revisao`; R$ 60,00 por pessoa por dia e condições |
| P02 — prazo de envio | PROC-001, 7; POL-001, 5 | `aguarda_revisao`; cinco dias úteis, sem calendário definido |
| P03 — quilometragem | POL-001, 2 | `abstencao_proposta`; coincidência de palavras não responde |
| P04 — almoço | Nenhum | `abstencao_local`; falha de vocabulário, sem chamada |
| P05 — aprovação pelo assistente | POL-004, 7 | `aguarda_revisao`; responsabilidade de decisão humana |

Use `--caso P02` etc. e `--destino .\cap09\gerados\P02` ao reproduzir outros casos. Uma pasta existente é sempre recusada para preservar seus arquivos. O destino padrão de `02_reproduzir.py` continua `gerados/reproducao-P01`, mesmo se você mudar apenas `--caso`.

Uma pergunta própria pode ser usada em `01_buscar.py --pergunta "texto"` ou na extensão autenticada. A reprodução aceita somente os cinco casos fornecidos; não simula uma inferência para perguntas novas.

## Arquivos e responsabilidades

| Arquivo | Responsabilidade |
| --- | --- |
| `corpus/catalogo.json`, `corpus/*.md` | Versão, títulos, seções e IDs estáveis; material fictício |
| `documentos.py` | Ler apenas documentos catalogados; separar seções e conferir limites |
| `busca.py` | Normalizar termos, pontuar e selecionar seções inteiras |
| `contexto.py`, `prompts/consulta.md` | Separar instruções dos dados; montar pedido limitado |
| `contrato_ia.py`, `validacao.py` | Conferir esquema, estado, IDs recuperados e citações literais |
| `fluxo.py` | Vincular corpus/pergunta/configuração, reproduzir e conferir pacote |
| `01_buscar.py` | Mostrar trechos antes de consultar o modelo |
| `02_reproduzir.py`, `03_conferir.py` | Produzir caso sintético e conferir fontes completas |
| `04_consultar_real.py`, `execucao_real.py` | Extensão opcional, no máximo uma tentativa por execução |
| `05_examinar_limites.py`, `solucao_desafio.py` | Nove bloqueios técnicos e dois erros de significado que exigem revisão |
| `cliente_ia.py`, `interpretacao.py` | Mesmo transporte e interpretação do capítulo anterior |
| `arquivos.py` | JSON estrito, hashes e saída em nova pasta |
| `MANIFESTO_SHA256.json` | Hashes dos arquivos técnicos, sem resultados de execução |
| `evidencias/` | Pasta para guardar os registros de sua própria execução. |

`pacote.json` guarda pergunta, trechos completos, pontuações, versão/hash do corpus, identidade do pedido e resposta. `analise.json` é um diagnóstico derivado, nunca um atestado de correção. `03_conferir.py` recalcula esse diagnóstico em vez de confiar nele.

## Regras e limites

- Pontuação: três pontos por termo distinto da pergunta no título da seção, mais um por termo distinto no corpo. Mínimo 2, até 3 seções por padrão. Empates por ID.
- Normalização: caixa, acentos, pontuação e uma lista curta de palavras comuns. Não há tradução de sinônimos, expansão automática de siglas ou lematização.
- Pergunta: até 500 caracteres. Corpo recuperado: até 6.000 caracteres; metadados e instruções ficam fora dessa contagem. Caracteres não são tokens.
- Corpus: até 12 documentos, 50 seções, 3.000 caracteres por seção, 30.000 de conteúdo. Arquivos de até 50.000 bytes. Preambulos antes de `## [ID]` não são recuperados: coloque as regras nas seções.
- IDs precisam ser únicos. Editar texto conserva a identidade lógica da seção, mas deve mudar a versão do corpus e seus hashes. Alterações no conteúdo indexado, na pergunta, no prompt ou na configuração invalidam a reprodução vinculada.
- Hashes detectam divergência; não autenticam autor nem impedem alguém de recalculá-los. Preserve as evidências de origem.
- Citação literal e ID válido não provam que a afirmação é sustentada. Os dois exemplos semanticamente errados ficam `aguarda_revisao` e devem ser rejeitados pelo leitor.
- Abstenção local significa falta de trechos selecionados. Abstenção proposta pelo modelo também requer conferência da busca. Nenhuma delas prova, sozinha, que o documento completo não contém a resposta.
- Documentos são dados não confiáveis. Não há ferramentas, SQL, execução de comandos ou busca de arquivos indicada pelo modelo. A separação do prompt não garante imunidade a instruções maliciosas.
- Uma execução ativa por vez. A gravação usa pasta temporária e renomeação; não é um protocolo de concorrência, durabilidade em queda de energia ou coordenação entre processos.

## Extensão autenticada — opcional

Sem chave, conclua o roteiro local e registre **não executada — opcional**. Não é necessário cadastrar uma chave para homologar o capítulo localmente.

Se optar pela extensão, a API pode gerar cobrança própria. Veja as condições atuais na conta do provedor. Nunca cole uma chave no chat, no manuscrito ou no ZIP. Se a chave já está configurada na sessão, não precisa carregá-la outra vez. O auxiliar PowerShell permite entrada mascarada:

```powershell
. .\cap09\carregar_chave_sessao.ps1
.\.venv\Scripts\python.exe .\cap09\01_buscar.py --caso P01
.\.venv\Scripts\python.exe .\cap09\04_consultar_real.py --caso P01 --confirmar-envio --destino .\cap09\gerados\api-P01
.\.venv\Scripts\python.exe .\cap09\03_conferir.py --pacote .\cap09\gerados\api-P01\pacote.json
```

Envio: pergunta, versão e trechos selecionados, instruções e esquema. Não são enviados o banco, a chave como conteúdo do prompt ou os outros capítulos. A chave autentica a requisição HTTPS. O endpoint é fixo `https://api.openai.com/v1`, modelo `gpt-4.1-mini-2025-04-14`. `store=False` é um parâmetro da API, não uma promessa geral sobre retenção do provedor.

O programa exige confirmação, faz no máximo uma tentativa ao SDK, timeout configurado em 30 segundos, `max_retries=0`, sem troca automática de modelo nem reprodução após falha. Saída padrão: 768 tokens, configurável por `PYTHON_PRATICA_IA_MAX_SAIDA` entre 32 e 1.024. Esse limite não é teto absoluto de fatura. Use o padrão ao reproduzir os casos vinculados; alterá-lo invalida essas fixtures.

Antes da tentativa, destino existente é bloqueado. Uma busca sem trechos se abstém localmente, com zero tentativas, mesmo no modo real confirmado. Falha ao salvar depois da tentativa retorna 3 e não dispara nova chamada. Se a comunicação falhar, processamento/consumo podem ser incertos.

| Saída | Significado |
| --- | --- |
| 0 | Etapa executada; resposta ainda pode exigir revisão ou representar abstenção |
| 1 | Entrada, configuração, arquivo ou serviço com falha |
| 2 | API sem confirmação; ou resposta recebida tecnicamente bloqueada |
| 3 | Não foi possível salvar o registro da extensão real; confira tentativas e não reenvie automaticamente |

`metadados.json` registra tentativas, duração, SDK/modelo, hash do pedido e uso quando disponível. Corpos de erro e chave não são registrados. No modo simulado, valores de tokens não medem custo real. No caso de resposta de serviço bloqueada, confira os arquivos salvos; não apresente a saída como concluída.

## Registro da sua execução

Use `ROTEIRO_WINDOWS.md` e preencha uma cópia de `REGISTRO_WINDOWS_MODELO.md` como `REGISTRO_WINDOWS.md`. Preserve o JSON recém-gerado na pasta `evidencias/`. A extensão autenticada permanece opcional.

