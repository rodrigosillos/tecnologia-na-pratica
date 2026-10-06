# Capítulo 8 — apoio R01

**Python na Prática — Automatize tarefas, integre IA e transforme dados em relatórios**  
Rodrigo Sillos · Tecnologia na Prática

Tema: extrair campos, sugerir categoria, conferir evidências e revisar antes de exportar um lote. Não há escrita no PostgreSQL neste capítulo.

## Estado de verificação

Parte local Windows aprovada: 95/95, Python 3.14.7, SDK 3.24.0, sem chave e sem banco. A extensão autenticada é opcional e não foi executada. Consulte `../VERIFICACAO_RESUMO.md`.

## Instalação

Extraia `cap08` ao lado de `cap07`, na raiz do projeto. Use a mesma venv:

```powershell
$pastaLivro = Join-Path $env:USERPROFILE 'projetos\python-na-pratica'
Set-Location -LiteralPath $pastaLivro
.\.venv\Scripts\python.exe -m pip install -r .\cap08\requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

As 20 dependências fixadas são idênticas às do capítulo 7. Pydantic já é parte desse conjunto. O apoio reutiliza, sem alterações, as regras de despesas e o contrato de catálogo do capítulo 6, além do cliente e da interpretação de resposta do capítulo 7. Não é necessário iniciar PostgreSQL ou o servidor HTTP.

## Prática principal: zero chamadas

Use o limite padrão para os casos fornecidos:

```powershell
Remove-Item Env:PYTHON_PRATICA_IA_MAX_SAIDA -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe .\cap08\01_preparar.py
.\.venv\Scripts\python.exe .\cap08\02_inspecionar.py
```

As três sugestões continuam pendentes de decisão. T001 não tem data; T002 contém total pago 18.50; T003 tem categoria ausente. Inspecione as fontes e formule suas decisões antes de consultar a solução preenchida.

Para executar a solução didática:

```powershell
.\.venv\Scripts\python.exe .\cap08\03_revisar.py --revisao .\cap08\revisoes\decisoes_exemplo.json
```

Esperado: saída 0; dois registros (D101/D102), um rejeitado (T003), total do lote revisado **53.50**, persistência não executada. O total 157.50 do capítulo 6 permanece independente. Saídas:

- `gerados/revisado/lote_revisado.json`: contrato de cinco campos, validado com a mesma função do capítulo 6.
- `gerados/revisado/trilha_revisao.json`: original, decisão, correções, complemento e resultado.

A data de T001 é corrigida para 2026-09-11 com a mensagem sintética cadastrada em `entradas/complementos.json`. A sugestão original permanece com data null. O nome de revisor no exemplo indica uma solução didática, não comprova revisão humana.

Para sua própria revisão, copie o modelo produzido em `gerados/reproducao/revisao_pendente.json`. Preencha revisor, ação e motivo por origem; preserve o vínculo com o pacote. Aceitar não admite correções ocultas. Corrigir exige ao menos uma alteração com trecho de evidência. Rejeitar não gera despesa. Campos ausentes ou inválidos impedem a publicação do lote final.

## Falhas e contraste sem consumo

```powershell
.\.venv\Scripts\python.exe .\cap08\03_revisar.py --revisao .\cap08\revisoes\aceite_invalido.json --destino .\cap08\gerados\aceite-invalido
.\.venv\Scripts\python.exe .\cap08\05_examinar_erros.py
.\.venv\Scripts\python.exe .\cap08\solucao_desafio.py
.\.venv\Scripts\python.exe .\cap08\verificar_capitulo.py
```

O primeiro retorna 1 e não publica a pasta final: aceitar não resolve a data ausente. Os programas 05 e desafio retornam 0 porque executam demonstrações, inclusive de sugestões incorretas. O verificador esperado retorna 0, `aprovado_local`, **95/95**, zero chamadas reais.

O contraste inclui uma categoria semanticamente inadequada e um subtotal apresentado como total. Esses casos passam pelas regras formais e continuam aguardando revisão. Um trecho literal existente não prova que ele sustente a interpretação. Não é prometida detecção automática de toda informação inventada ou de todo erro de classificação.

## Repetir preservando evidências

Uma pasta de destino existente é preservada e causa saída 1. Para nova execução, escolha outra pasta com `--destino`. Ao usar um pacote em outra pasta, informe `--pacote` nos programas 02 e 03. Não há exclusão automática de dados.

Use uma execução ativa por vez. A publicação de arquivos usa uma pasta temporária, sem garantir coordenação entre múltiplos processos ou resistência a qualquer falha de sistema.

## Extensão opcional de API

Nenhuma chave é necessária para o percurso acima. Quando houver acesso e decisão de executar a API:

1. Carregue uma chave já obtida na mesma sessão, usando o procedimento do capítulo 7 ou `. .\cap08\carregar_chave_sessao.ps1`.
2. Confira origem, prompt, esquema, acesso e cobrança. O modelo continua `gpt-4.1-mini-2025-04-14`.
3. Execute uma tentativa explícita:

```powershell
.\.venv\Scripts\python.exe .\cap08\04_extrair_real.py --origem T001 --confirmar-envio
.\.venv\Scripts\python.exe .\cap08\02_inspecionar.py --pacote .\cap08\gerados\api-real\pacote.json
```

A segunda linha apenas inspeciona o arquivo, se ele tiver sido produzido. Preencha a revisão nova gerada para essa resposta; o gabarito sintético tem outro hash e não serve como revisão automática da chamada real. Não altere apenas o hash para contornar essa verificação.

Padrões: descrição de até 3.000 caracteres; saída de 512 tokens, configurável de 32 a 1024 por `PYTHON_PRATICA_IA_MAX_SAIDA`; `store=False`, truncamento desabilitado e nenhuma ferramenta; timeout 30 segundos e zero retries. Uma execução confirmada pode consumir API. Falhas após envio não são anunciadas como custo zero.

A pasta real recebe `metadados.json` e, quando houver resposta compatível, `pacote.json` e `revisao_pendente.json`. O modo real não muda para reprodução em caso de falha. Registros simulados criados nos testes ficam em diretórios temporários e não são incluídos como inferências.

## Códigos de saída

| Situação | Exit |
| --- | ---: |
| Preparação, inspeção sem bloqueio técnico ou revisão válida | 0 |
| Erro de arquivo/contrato, decisão pendente ou destino existente | 1 |
| Inspeção de pacote com sugestão bloqueada | 2 |
| API sem confirmação | 2 |
| API confirmada sem chave | 1 |
| API recebeu sugestão sem bloqueio técnico, ainda não revisada | 0 |
| API recebeu sugestão bloqueada | 2 |
| Falha SDK/API | 1 |
| Falha ao gravar após tentativa de API | 3 |
| Verificador aprovado/reprovado | 0 / 1 |

## Arquivos centrais

| Grupo | Papel |
| --- | --- |
| `contrato_ia.py` | Pydantic e JSON Schema, campos nulos e categorias permitidas. |
| `validacao.py` | Regras e vínculos com trechos da fonte. |
| `contexto.py`, `entradas/`, `prompts/` | Origens, catálogo e pedido versionado. |
| `fluxo.py`, `revisoes/` | Reprodução, decisões e lote revisado. |
| `arquivos.py` | JSON estrito, hashes e saída em diretório novo. |
| `cliente_ia.py`, `interpretacao.py`, `execucao_real.py` | Comunicação opcional e estados de resposta. |
| `regras.py`, `contrato_catalogo.py` | Contratos reutilizados do capítulo 6. |
| `ROTEIRO_WINDOWS.md`, `REGISTRO_WINDOWS_MODELO.md` | Homologação local e extensão real opcional. |

O catálogo e os textos são pequenos e controlados. Reconhecimento monetário sem separadores de milhar, descrição literal e ausência de OCR são limites do recorte. Novos formatos exigem revisão explícita do contrato. O projeto integrado e a importação ficam para etapas posteriores.
