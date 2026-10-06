# Capítulo 10 — Avaliando respostas, custos e limites da IA

Python na Prática • Tecnologia na Prática • Rodrigo Sillos • R01

Laboratório de avaliação com **20 casos sintéticos, 12 de ajuste e 8 de reserva**. Compara dimensões de qualidade, registra regressões, exercita limites de consumo e oferece uma amostra autenticada opcional. Não usa banco nem aprova despesas.

## Instalação e execução local

Extraia `cap10` em `projetos\python-na-pratica`, ao lado de `.venv`. Comandos no PowerShell, a partir dessa pasta:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\cap10\requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe .\cap10\verificar_capitulo.py
.\.venv\Scripts\python.exe .\cap10\01_avaliar.py --versao A
.\.venv\Scripts\python.exe .\cap10\02_comparar.py
```

Python 3.14.7, OpenAI SDK 3.24.0 e as mesmas vinte dependências do capítulo anterior. **Windows: 158/158 aprovado no escopo local**; veja `../VERIFICACAO_RESUMO.md`. O verificador exige Python 3.14 em venv e as versões fixadas.

O padrão das avaliações é `--particao ajuste`. Use `--particao reserva` depois de fixar a proposta de prompt; `--particao todos` reúne os vinte casos para conferir o exemplo completo. A reserva está visível no ZIP: a separação é disciplina de trabalho, não sigilo ou prova de independência.

## O que as duas versões significam

Os arquivos `execucoes/A.json` e `execucoes/B.json` foram **escritos para o exercício**. Respostas, tokens e durações são fictícios. Eles estão vinculados aos prompts A/B para ensinar controle de versões e comparação; não foram gerados por esses prompts e não demonstram que B melhora um modelo real.

As rubricas em `revisoes/A.json` e `revisoes/B.json` são referências didáticas explícitas, vinculadas aos hashes das execuções/respostas. Não representam revisão humana de inferência real. O avaliador impede usar `referencia_sintetica` para avalizar uma execução marcada `api_real`.

| Dimensão, conjunto completo | A | B |
| --- | ---: | ---: |
| Casos aprovados | 12/20 | 18/20 |
| Formato válido | 20/20 | 20/20 |
| Validação técnica | 18/20 | 20/20 |
| Campos de extração | 48/52 | 51/52 |
| Categoria | 12/13 | 12/13 |
| Campos que devem permanecer ausentes | 4/6 | 6/6 |
| Decisão responder/abster-se | 6/7 | 7/7 |
| Fontes exigidas nos casos respondíveis | 4/5 | 5/5 |
| Fundamentação conforme rubrica | 3/7 | 6/7 |
| Casos críticos de instrução intrusa | 0/2 | 1/2 |

São sete melhorias e uma regressão: **X04** muda incorretamente de Materiais para Alimentação. **I02** continua seguindo a nota intrusa e declarando aprovação automática. A decisão é `nao_promover`, mesmo com 18/20. Critérios didáticos: avaliação completa, pelo menos 90% dos casos, nenhuma regressão, nenhuma pendência e todos os críticos atendidos. Não são limites universais para sistemas reais.

## Arquivos e comandos

| Arquivo | Uso |
| --- | --- |
| `dados/casos.json` | Entradas, gabaritos, critérios, grupos e partições |
| `prompts/*_A.md`, `prompts/*_B.md` | Versões de extração e consulta; gabaritos não são enviados ao modelo |
| `corpus/` | Mesma política do capítulo 9; base preservada |
| `conjunto.py` | Seleção, contexto, esquema e identidade do pedido |
| `avaliacao.py` | Conferência, métricas, revisão vinculada e comparação |
| `custos.py` | Decimal, referência de tarifas, reserva e bloqueios |
| `01_avaliar.py` | Avaliar A/B; `--sem-revisao` demonstra pendências |
| `02_comparar.py` | Comparar a mesma partição das duas versões |
| `03_simular_limites.py` | Cenários `orcamento`, `chamadas` e `incerto`, sem rede |
| `04_amostra_real.py` | Uma amostra opcional, não vinte chamadas automáticas |
| `05_avaliar_arquivo.py` | Avaliar execução arquivada, explicitando cobertura parcial |
| `06_inspecionar.py` | Ver entrada, critério, gabarito, resposta e fontes de um caso |
| `solucao_desafio.py` | Explicar por que a maior média não autoriza a promoção |

Exemplos adicionais:

```powershell
.\.venv\Scripts\python.exe .\cap10\02_comparar.py --particao todos
.\.venv\Scripts\python.exe .\cap10\01_avaliar.py --versao B --particao todos --sem-revisao --destino .\cap10\gerados\B-sem-revisao
.\.venv\Scripts\python.exe .\cap10\06_inspecionar.py --caso X02 --versao A
.\.venv\Scripts\python.exe .\cap10\06_inspecionar.py --caso I02 --versao B
.\.venv\Scripts\python.exe .\cap10\03_simular_limites.py --cenario incerto
.\.venv\Scripts\python.exe .\cap10\solucao_desafio.py
```

Todos esses programas são locais. `01` sem revisão, com B/todos: 12 acertos, 1 falha e **7 pendências**; fundamentação 0/7, sete pendências. Pendência não é acerto. `02` retorna exit 0 quando a comparação funciona, mesmo se a decisão for `nao_promover`.

Cada destino deve ser novo. Pastas existentes são recusadas e preservadas. A avaliação produz JSON UTF-8. Se cp850 corromper a apresentação do console, confira os arquivos; não altere os dados para corrigir somente a exibição.

## Critérios, denominadores e limites do avaliador

- Treze extrações: X01–X08, A01–A04, I01. Quatro campos por caso = 52 comparações; treze categorias e seis valores esperados null.
- Sete consultas: R01–R04, S01–S02, I02. Decisão responder/abster-se é comparada com a situação esperada, incluindo respostas indevidamente recusadas. Não é apenas a taxa de acerto nas duas perguntas sem cobertura.
- Cinco consultas respondíveis exigem fontes. A checagem confirma referência recuperada e citação literal; não resolve o significado.
- A rubrica de consulta responde `atende_pergunta` e `preserva_regras`, com justificativa. Sem revisão, o resultado continua pendente. Não há juiz LLM.
- Extração usa gabaritos exatos deste corpus controlado; a descrição deve ser literal. Não se alega avaliar qualquer paráfrase livre.
- A pontuação de caso exige formato, validação técnica e conteúdo/critério. Métricas de campos isolados continuam separadas; um campo correto não salva um caso com outro campo incorreto.
- A cópia do contexto de I02 recebe uma nota intrusa depois da recuperação. O corpus-base não é modificado. O teste separa uma tentativa de instrução maliciosa da regra que o revisor deve considerar válida.
- IDs e hashes impedem comparação acidental de dados/configurações diferentes, mas não autenticam autoria. Um autor com acesso aos arquivos pode recalculá-los.
- Uma amostra real de um caso mostra dezenove casos ausentes e não pode ser comparada como avaliação completa de vinte.

## Custos e limites

`dados/tarifas_referencia.json` registra fonte, modelo e consulta em **04/10/2026**: entrada USD 0.40 e saída USD 1.60 por milhão de tokens. É uma referência de texto padrão, considerando toda entrada sem desconto de cache. Não inclui impostos, câmbio, ferramentas, outras modalidades ou particularidades de conta. Não é uma fatura nem uma cotação permanente; confira a [página do modelo](https://developers.openai.com/api/docs/models/gpt-4.1-mini) antes de uso real.

Fórmula: `(tokens_entrada × tarifa_entrada + tokens_saida × tarifa_saida) / 1.000.000`, com `Decimal`. O cálculo soma antes de formatar e não arredonda cada chamada a centavos.

**Valores do exercício, não gastos:** A = USD 0.009160; B = USD 0.010440. Medianas fictícias: A 1110 ms; B 1230 ms. Eles ensinam a ler um relatório; não provam latência, custo ou eficiência atual do serviço.

Cenário de limites: uma previsão de 1.000 tokens de entrada e até 768 de saída reserva USD 0.0016288. Uso sintético de 1.000 + 500 custa USD 0.0012 nessa tabela. Outra reserva é bloqueada se exceder o orçamento; o contador também limita chamadas. Uso ausente ou inválido mantém reserva e estado `incerto`: não libera saldo presumindo zero.

O contador `tentativas` do controle avança na autorização anterior ao envio; `tentativas_sdk` registra o início efetivo da chamada ao SDK. Reserva pendente não permite outra autorização. Consumo informado maior do que a previsão interrompe novas tentativas. O orçamento é **local à execução**, não global à conta nem compartilhado entre processos/pastas. Reiniciar a aplicação inicia outro controle; não use isso como mecanismo de limite de fatura.

## Extensão autenticada opcional

A homologação local pode encerrar sem chave. Se optar por uma amostra real, o fluxo faz **no máximo uma tentativa**, com confirmação explícita, timeout configurado em 30 s, `max_retries=0` e nenhuma troca de modelo ou resposta sintética após falha. Não há loop que dispare os vinte casos.

```powershell
. .\cap10\carregar_chave_sessao.ps1
.\.venv\Scripts\python.exe .\cap10\04_amostra_real.py --caso R01 --versao B --confirmar-envio --destino .\cap10\gerados\real-R01
.\.venv\Scripts\python.exe .\cap10\05_avaliar_arquivo.py --execucao .\cap10\gerados\real-R01\execucao.json --destino .\cap10\gerados\avaliacao-real-R01
```

Se a chave já está na sessão, dispense o auxiliar. Não cole o valor no chat, no código ou em entregáveis. O auxiliar não cria chave, só permite entrada mascarada no PowerShell.

O endpoint continua `https://api.openai.com/v1`, modelo `gpt-4.1-mini-2025-04-14`. O pedido envia texto/pergunta, contexto selecionado, instruções e esquema, sem gabaritos, rubricas ou ferramentas. `store=False` não representa garantia geral sobre retenção pelo provedor.

Parâmetros: `--orcamento-usd` (padrão `0.010000`), `--limite-saida` (32–1.024, padrão 768) e `--limite-caracteres` (1–16.000, padrão 16.000). A entrada prevista usa bytes UTF-8 do pedido serializado + 256 como **heurística conservadora**, não um tokenizador nem um teto matemático de tokens. A previsão pode divergir do uso; limites locais não garantem valor máximo da fatura. O timeout também não garante que uma requisição interrompida não tenha sido processada.

Arquivos: `execucao.json`, `revisao_pendente.json`, `metadados.json`. Código 0 nesta etapa significa resultado arquivado para avaliação, inclusive se incompleto ou recusado; o avaliador determinará o bloqueio. Edite uma cópia da revisão pendente, identifique responsável, atribua booleanos e justifique os critérios após conferir as fontes. Reavalie com `--revisao caminho`. Nunca troque somente a natureza de uma rubrica sintética para fazê-la parecer revisão real.

| Saída | Significado |
| --- | --- |
| 0 | Comando concluiu seu trabalho; não implica qualidade aprovada |
| 1 | Configuração, entrada, arquivo ou chamada falhou |
| 2 | Extensão real sem confirmação, zero chamadas |
| 3 | Falha ao salvar após tentativa; não reenviar automaticamente |

Sem chave, orçamento suficiente e contexto disponível: confirmação retorna 1. Orçamento insuficiente, entrada grande ou destino existente também bloqueiam antes do envio. Após erro com consumo desconhecido, o registro marca incerteza. Falha de gravação retorna 3 sem segunda tentativa. Não são gravados chave nem corpo de erro da API.

## Registro da sua execução

Use `ROTEIRO_WINDOWS.md` e preencha `REGISTRO_WINDOWS.md` a partir do modelo. A integração real permanece opcional. Os 158 testes verificam o programa; não são 158 inferências aprovadas nem uma taxa de acerto da IA.

