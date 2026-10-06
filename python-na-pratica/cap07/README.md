# Capítulo 7 — apoio R01

**Python na Prática — Automatize tarefas, integre IA e transforme dados em relatórios**  
Rodrigo Sillos · Tecnologia na Prática

Tema: conectar Python a um modelo, escolher o contexto e interpretar estado, texto, uso e falhas. As respostas são material para revisão. Este capítulo não grava sugestões no PostgreSQL.

## Estado de verificação

Parte local Windows aprovada: 101/101, Python 3.14.7, SDK 3.24.0, zero chamadas reais. Os casos são sintéticos. A extensão autenticada é opcional e não foi executada; a ausência de chave não impede o fechamento local. Consulte `../VERIFICACAO_RESUMO.md`.

## Instalação

Extraia `cap07` na raiz do projeto, ao lado de `cap06`, preservando os capítulos anteriores. Na mesma venv:

```powershell
$pastaLivro = Join-Path $env:USERPROFILE 'projetos\python-na-pratica'
Set-Location -LiteralPath $pastaLivro
.\.venv\Scripts\python.exe -m pip install -r .\cap07\requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

O conjunto fixa OpenAI 3.24.0 e mantém as dependências anteriores. Os pacotes binários para Windows x64/Python 3.14 foram localizados; isso não substitui a instalação e execução no seu computador. Não é necessário iniciar PostgreSQL ou o catálogo para os programas deste capítulo.

Escolhas do percurso principal: OpenAI Responses API; snapshot `gpt-4.1-mini-2025-04-14`; contexto de uma única descrição sintética; entrada de até 3.000 caracteres; saída padrão 256 tokens, configurável de 32 a 512; `store=False`; ferramentas vazias; uma tentativa de SDK por execução; `max_retries=0`; timeout de comunicação 30 segundos. Não há troca automática de modelo nem fallback silencioso para reprodução.

## Sequência sem chamadas pagas

```powershell
.\.venv\Scripts\python.exe .\cap07\01_inspecionar_contexto.py
.\.venv\Scripts\python.exe .\cap07\02_reproduzir.py
.\.venv\Scripts\python.exe .\cap07\02_reproduzir.py --caso incompleta
.\.venv\Scripts\python.exe .\cap07\02_reproduzir.py --caso recusada
.\.venv\Scripts\python.exe .\cap07\04_comparar_respostas.py
.\.venv\Scripts\python.exe .\cap07\solucao_desafio.py
.\.venv\Scripts\python.exe .\cap07\verificar_capitulo.py
```

Casos disponíveis: `concluida`, `incompleta`, `recusada`, `sem_texto`, `sem_uso`, `data_inventada`. Os identificadores e tokens nesses arquivos são fictícios. A reprodução informa essa origem e não usa credencial.

O verificador esperado apresenta **101/101**, `status: aprovado_local`, saída **0** e `integracao_real: pendente`. Esse campo registra que a extensão autenticada não foi executada; não invalida a aprovação local. Seus subprocessos são capturados como UTF-8. Registre separadamente a aparência do console cp850.

## Chamada real: extensão opcional e escolha explícita

Leia o contexto e confira acesso/cobrança no projeto do provedor. Use uma chave já obtida pelo fluxo seguro da plataforma. Para carregá-la apenas na sessão, com entrada oculta:

```powershell
. .\cap07\carregar_chave_sessao.ps1
.\.venv\Scripts\python.exe .\cap07\01_inspecionar_contexto.py
```

Se a política do ambiente bloquear o script, siga o procedimento permitido pela sua organização para configurar `OPENAI_API_KEY`. Não é necessário alterar globalmente a política de execução. Não envie a chave junto das evidências.

O programa abaixo só envia quando a opção de confirmação estiver presente:

```powershell
.\.venv\Scripts\python.exe .\cap07\03_chamada_real.py --confirmar-envio
$LASTEXITCODE
```

Ele faz uma tentativa. Possíveis falhas de comunicação não são anunciadas como consumo zero. Cada nova execução confirmada pode representar novo consumo. A chave nunca é parte do prompt.

O arquivo de registro aparece em `gerados/chamada-real-...json`. Confirme esse arquivo sem refazer a inferência:

```powershell
.\.venv\Scripts\python.exe .\cap07\conferir_chamada_real.py '.\cap07\gerados\chamada-real-SEU-ARQUIVO.json'
```

Use o nome real impresso pelo programa e o mesmo limite de saída empregado na chamada. O conferidor valida consistência, não autenticidade de um arquivo arbitrariamente alterado nem qualidade semântica. Conserve a evidência da execução e preencha o registro manual.

Ao terminar:

```powershell
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
```

A remoção afeta essa sessão, não revoga a chave no provedor. O script de carga não cria arquivo de segredo. `gerados` contém somente o pedido sintético e os campos necessários à conferência da resposta, sem cabeçalhos de autenticação.

## Interpretação das saídas

| Programa/situação | Exit | Significado |
| --- | ---: | --- |
| Reprodução concluída | 0 | Caso técnico concluído; conteúdo ainda exige conferência. |
| Reprodução incompleta/recusada/sem texto/sem uso | 2 | Pendência esperada do caso. |
| Modo real sem `--confirmar-envio` | 2 | Nenhum envio autorizado pelo comando. |
| Modo real sem chave válida na configuração | 1 | Nenhuma chamada iniciada. |
| Modo real com texto concluído e uso válido | 0 | Resposta recebida; revisão humana pendente. |
| Modo real com resposta incompleta/recusada | 2 | Resposta registrada, tarefa assistida pendente. |
| Modo real com falha do SDK/API | 1 | Diagnóstico registrado; consumo pode depender do que ocorreu no provedor. |
| Falha ao salvar depois da tentativa | 3 | Não reenviar automaticamente para recuperar o arquivo. |
| Verificador local aprovado | 0 | Testes locais aprovados; não fecha a integração real. |

## Organização

| Arquivo/pasta | Finalidade |
| --- | --- |
| `configuracao_ia.py` | Modelo, limites, endpoint e leitura da chave por ambiente. |
| `contexto.py`, `prompts/`, `entradas/` | Construção do pedido e identificação por hash. |
| `cliente_ia.py` | SDK e diagnóstico sem corpo bruto de erros. |
| `interpretacao.py` | Estados, mensagens, recusa, texto e uso. |
| `reproducao.py`, `casos/` | Reprodução dos seis casos sintéticos. |
| `execucao_real.py` | Execução explícita e registro UTF-8. |
| `01_...` a `04_...`, `solucao_desafio.py` | Práticas do capítulo. |
| `verificar_capitulo.py` | Testes locais e integração simulada com SDK. |
| `conferir_chamada_real.py` | Conferência de registro já produzido, sem novo envio. |
| `ROTEIRO_WINDOWS.md`, `REGISTRO_WINDOWS_MODELO.md` | Homologação e registro do autor. |

Para experimentar com código, duplique a pasta inteira como `cap07_experimentos`. Mantenha o pacote original para homologação. Alterações no prompt/entrada invalidam o vínculo dos casos gravados; não atualize hashes só para ocultar a divergência. Crie novos casos identificados quando mudar o experimento.

No capítulo 8, a saída passará a ter campos estruturados e revisão explícita. RAG, avaliação sistemática e recuperação com tentativas limitadas pertencem às etapas seguintes do plano.
