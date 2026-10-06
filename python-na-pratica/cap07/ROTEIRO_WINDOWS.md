# Homologação Windows — capítulo 7 R01

Use Python 3.14.7 e as dependências fixadas. A execução local e a integração real são verificações distintas. O fechamento local exige o roteiro sem credencial. A chamada autenticada e sua revisão são uma extensão opcional, registrada separadamente.

## 1. Preparação e parte local

Extraia `cap07` ao lado dos capítulos anteriores. Na raiz `projetos\python-na-pratica`:

```powershell
.\.venv\Scripts\python.exe --version
$PSVersionTable.PSVersion
chcp
.\.venv\Scripts\python.exe -m pip install -r .\cap07\requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe .\cap07\verificar_capitulo.py
$LASTEXITCODE
```

Esperado: **101/101, `aprovado_local`, zero falhas, chamadas reais zero, saída 0**. A mensagem `integração real: pendente` está correta nesta etapa. O verificador substitui o transporte HTTP por respostas sintéticas e não usa a chave do leitor.

Copie o JSON recém-gerado para `cap07/evidencias/relatorio-windows-python314.json`, preservando o original. O nome contém data/hora UTC; use o caminho impresso, não um relatório antigo.

## 2. Roteiro manual sem credencial

Se houver uma chave na sessão e você quiser preservá-la, abra um novo terminal sem carregá-la para estes testes. Não imprima o ambiente ou a chave.

Execute cada programa na raiz do projeto com `.\.venv\Scripts\python.exe .\cap07\NOME.py`, acrescentando os argumentos indicados. Confira `$LASTEXITCODE` imediatamente depois de cada programa.

| Programa/argumentos | Resultado esperado | Exit |
| --- | --- | ---: |
| `01_inspecionar_contexto.py` | Mostra modelo, instruções, descrição, limite 256; nenhuma chamada. | 0 |
| `02_reproduzir.py` | Origem sintética, concluída; valor 35,00 e data ausente; tokens fictícios 210/65/275. | 0 |
| `02_reproduzir.py --caso incompleta` | Incompleta; não libera texto parcial. | 2 |
| `02_reproduzir.py --caso recusada` | Recusada; nenhuma sugestão aceita. | 2 |
| `02_reproduzir.py --caso sem_texto` | Sem texto utilizável. | 2 |
| `02_reproduzir.py --caso sem_uso` | Uso ausente; não declara consumo zero. | 2 |
| `03_chamada_real.py` | API real desativada; não envia mesmo se houver chave. | 2 |
| `03_chamada_real.py --confirmar-envio`, sem chave | `OPENAI_API_KEY não configurada nesta sessão`; não envia. | 1 |
| `04_comparar_respostas.py` | Dois estados concluídos; segunda resposta inventa 10/09/2026. | 0 |
| `solucao_desafio.py` | Incomplete, trecho parcial True, aceitação False, texto None. | 0 |

Teste o limite sem fazer chamada:

```powershell
$env:PYTHON_PRATICA_IA_MAX_SAIDA = '128'
.\.venv\Scripts\python.exe .\cap07\01_inspecionar_contexto.py
Remove-Item Env:PYTHON_PRATICA_IA_MAX_SAIDA -ErrorAction SilentlyContinue
```

O programa deve mostrar 128. A remoção restaura 256 para a chamada de referência a seguir.

## 3. Extensão opcional: uma chamada real de referência

Se não for executar esta extensão, registre “não executada — opcional” e conclua o registro local da seção 5. A conferência da seção 4 aplica-se somente a uma chamada efetivamente realizada.

Confira o texto em `entradas/descricao.md`, as instruções e as condições de acesso/cobrança do projeto OpenAI. O snapshot é `gpt-4.1-mini-2025-04-14`. Se não estiver disponível para a conta, registre a indisponibilidade; não troque silenciosamente o modelo e declare aprovação desta revisão.

Carregue uma chave já obtida por fluxo seguro:

```powershell
. .\cap07\carregar_chave_sessao.ps1
.\.venv\Scripts\python.exe .\cap07\01_inspecionar_contexto.py
```

Esperado: chave presente, valor não exibido. Não altere globalmente a política de execução se o script for bloqueado; use o procedimento permitido no seu ambiente. Registre o resultado do script PowerShell, que não foi executado no ambiente Linux editorial.

Para autorizar a tentativa:

```powershell
.\.venv\Scripts\python.exe .\cap07\03_chamada_real.py --confirmar-envio
$LASTEXITCODE
```

Esperado para a referência: resposta concluída com texto para revisão, uso válido, exit 0 e um JSON novo em `gerados/`. A frase e as contagens de tokens reais não têm gabarito fixo. Se ocorrer recusa, interrupção ou erro, preserve a evidência e registre a pendência. Não provoque várias chamadas pagas para testar erros: esses caminhos já têm testes sintéticos.

No JSON, confira:

- `modo: api_real`, `origem: execucao_sdk`, SDK 3.24.0, snapshot solicitado e devolvido.
- `tentativas_sdk: 1`, `max_retries: 0`; entrada/instruções correspondentes ao pacote.
- Estado da resposta, identificador do provedor e tokens informados.
- `revisao_do_conteudo: pendente`: preencher o registro manual, sem editar a resposta capturada.
- Ausência da chave e de cabeçalhos de autenticação. Não compartilhe arquivos de configuração de credenciais.

## 4. Conferência sem segunda chamada

Use o caminho real impresso:

```powershell
.\.venv\Scripts\python.exe .\cap07\conferir_chamada_real.py '.\cap07\gerados\chamada-real-SEU-ARQUIVO.json'
$LASTEXITCODE
```

Esperado: registro consistente, chamadas realizadas por esta conferência zero, exit 0. A ferramenta não comprova a origem de um JSON manualmente fabricado nem a correção do texto. A evidência deve ser o arquivo produzido pela chamada observada.

Faça a revisão semântica: o valor 35,00 foi preservado? A data foi indicada como ausente? Houve invenção de nome, local, data ou aprovação da despesa? Registre uma conclusão e o motivo. Uma falha semântica não apaga o sucesso de transporte, mas impede encerrar o aceite editorial da resposta de referência sem analisar o ajuste necessário.

Não precisa reexecutar a importação do capítulo 6: nenhum programa do capítulo 7 consulta ou modifica o banco. Os dados confirmados continuam sendo responsabilidade daquele percurso.

## 5. Encerramento e registros a conservar

```powershell
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
```

Preencha `REGISTRO_WINDOWS_MODELO.md` e salve a cópia como `REGISTRO_WINDOWS.md`. Conserve:

1. O JSON local `relatorio-windows-python314.json`.
2. Se executar a extensão opcional: o JSON da chamada real, conferido e sem chave, como `evidencias/chamada-real-referencia.json` (preserve também o original).
3. O registro manual da parte local e da legibilidade dos arquivos UTF-8. Inclua revisão do conteúdo real somente se a chamada tiver sido executada.

Critério de fechamento local: 101/101, roteiro sem credencial conferido e registro manual preenchido. A extensão autenticada pode ficar “não executada — opcional”. Quando executada, exige resposta registrada, conferência e revisão do conteúdo; seus resultados não devem ser presumidos a partir dos testes locais. Mantenha a ressalva cp850 separada da codificação dos arquivos.
