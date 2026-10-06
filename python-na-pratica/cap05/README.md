# Python na Prática — capítulo 5, apoio R01

**Integrando APIs e entendendo as respostas**  
Autor: Rodrigo Sillos · Coleção Tecnologia na Prática  
Base: Python 3.14.7. Estado: execução Linux documentada; homologação funcional Windows concluída (99/99), com ressalva de acentos no console.

Este pacote é independente das pastas dos capítulos anteriores. As despesas são fictícias. Há tráfego HTTP real entre processos locais; as respostas do servidor são sintéticas e controladas. Não há inferência de IA, chamada paga ou gravação de despesas. O verificador escreve somente seus relatórios em `resultados/`.

## Instalação no Windows

Extraia `cap05` para a raiz de `projetos\python-na-pratica`, ao lado de `.venv`. Preserve `cap04`. Não copie uma `.venv` de outro computador.

No PowerShell:

```powershell
$pastaLivro = Join-Path $env:USERPROFILE 'projetos\python-na-pratica'
Set-Location -LiteralPath $pastaLivro
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -r .\cap05\requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Confira Python 3.14.7 e instalação sem erro. `pip check` deve mostrar `No broken requirements found.` A instalação usa internet; a prática não exige conexão externa. A instalação altera somente a `.venv` indicada. O ZIP não contém dependências instaladas nem a própria `.venv`.

| Pacote | Versão fixada |
| --- | --- |
| requests | 2.34.2 |
| certifi | 2026.7.22 |
| charset-normalizer | 3.5.1 |
| idna | 3.20 |
| urllib3 | 2.8.0 |

Essas são as versões exercitadas nesta entrega, não uma promessa de que serão as mais recentes em outra data. O verificador registra a versão real de cada pacote e rejeita divergência deste conjunto homologado. Mudanças de versão exigem nova verificação; não ignore conflitos da instalação.

## Dois terminais

No primeiro terminal, na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe .\cap05\servidor_catalogo.py
```

Deixe-o aberto; deve informar `API local em http://127.0.0.1:8765`.

No segundo terminal, execute novamente os comandos que definem `$pastaLivro` e entram na raiz. Então:

```powershell
.\.venv\Scripts\python.exe .\cap05\01_observar_resposta.py
.\.venv\Scripts\python.exe .\cap05\02_validar_contrato.py
.\.venv\Scripts\python.exe .\cap05\03_consultar_catalogo.py
.\.venv\Scripts\python.exe .\cap05\04_resumo_csv.py
.\.venv\Scripts\python.exe .\cap05\05_resumo_json.py
```

As saídas esperadas estão no capítulo e no roteiro Windows. CSV e JSON: 3 despesas únicas, 0 repetições, total 127.50, código 0. Confira `$LASTEXITCODE` imediatamente depois de cada programa quando registrar a execução manual.

Para observar erros intencionais:

```powershell
.\.venv\Scripts\python.exe .\cap05\06_observar_falhas.py 404
.\.venv\Scripts\python.exe .\cap05\06_observar_falhas.py 503
.\.venv\Scripts\python.exe .\cap05\06_observar_falhas.py json
.\.venv\Scripts\python.exe .\cap05\06_observar_falhas.py contrato
.\.venv\Scripts\python.exe .\cap05\06_observar_falhas.py tipo
.\.venv\Scripts\python.exe .\cap05\06_observar_falhas.py lenta
.\.venv\Scripts\python.exe .\cap05\06_observar_falhas.py redirect
.\.venv\Scripts\python.exe .\cap05\solucao_exercicio.py
.\.venv\Scripts\python.exe .\cap05\solucao_desafio.py
```

Todos esses nove comandos devem terminar com código **1**, com diagnóstico e sem total. O argumento inexistente ou ausente em `06_observar_falhas.py` produz código 2 e mensagem de uso. Não confundir falha intencional com falha da homologação.

Pare o servidor com Ctrl+C. Agora `03_consultar_catalogo.py` deve falhar com código 1 e `API: falha de comunicação HTTP`. Reinicie o servidor se quiser continuar as consultas manuais.

## Porta ocupada

Primeiro confira se o seu servidor já está aberto. Não encerre processos desconhecidos. Se precisar usar outra porta, por exemplo 8766:

Primeiro terminal:

```powershell
.\.venv\Scripts\python.exe .\cap05\servidor_catalogo.py --porta 8766
```

Segundo terminal, antes dos clientes:

```powershell
$env:PYTHON_PRATICA_API_URL = 'http://127.0.0.1:8766'
.\.venv\Scripts\python.exe .\cap05\03_consultar_catalogo.py
```

Essa variável só configura o endereço base neste terminal; os programas acrescentam o caminho. Para voltar ao padrão:

```powershell
Remove-Item Env:PYTHON_PRATICA_API_URL -ErrorAction SilentlyContinue
```

Não acrescente barra final, caminho, credenciais ou parâmetros ao endereço base. O adaptador integrado aceita somente `http://127.0.0.1:porta/...`, não segue redirecionamentos e não usa proxy ou `.netrc`. A restrição é específica deste laboratório. O primeiro programa de observação pressupõe a configuração local fornecida; não é um cliente para endereços arbitrários.

## Verificador e Windows

O verificador cria seu próprio servidor em uma porta temporária e não depende do servidor manual na 8765. Não faz chamadas externas. Pode ser executado com o servidor manual desligado:

```powershell
.\.venv\Scripts\python.exe .\cap05\verificar_capitulo.py
$LASTEXITCODE
```

Sucesso: todas as verificações aprovadas, sistema Windows e saída 0. Preserve o JSON de `resultados` e siga `ROTEIRO_WINDOWS.md`. O verificador não corrige nem altera os arquivos de entrada. `MANIFESTO_SHA256.json` contém os hashes de scripts, dados e requisitos; para experimentar, duplique a pasta inteira como `cap05_experimentos`, edite nela e troque o caminho nos comandos. Copiar apenas um programa para outra pasta separaria os módulos e dados de que ele depende. Preserve `cap05` para a conferência.

Windows: 99/99 aprovado. A ressalva de acentuação no console cp850 permanece separada da correção dos valores e da legibilidade dos arquivos UTF-8. Consulte `../VERIFICACAO_RESUMO.md`.

## Linux

Na raiz do projeto, usando a `.venv` do livro:

```bash
./.venv/bin/python -m pip install -r cap05/requirements.txt
./.venv/bin/python -m pip check
./.venv/bin/python cap05/servidor_catalogo.py
```

Em outro terminal, na mesma raiz:

```bash
./.venv/bin/python cap05/04_resumo_csv.py
./.venv/bin/python cap05/05_resumo_json.py
./.venv/bin/python cap05/verificar_capitulo.py
echo $?
```

A produção também verificou Linux/Python 3.14.7 com esse conjunto de dependências. macOS não foi executado. Registre o caminho real do seu interpretador ao reproduzir o roteiro.

## Mapa dos arquivos

| Arquivo | Responsabilidade |
| --- | --- |
| `servidor_catalogo.py` | Ferramenta pronta que serve categorias e falhas sintéticas apenas no loopback. |
| `configuracao.py` | Endereço padrão e opção de porta alternativa. |
| `contrato_catalogo.py` | Validação do documento recebido, sem rede. |
| `cliente_catalogo.py` | Uma tentativa HTTP, timeout, limites e validação. |
| `regras.py` | Regras de despesas, com catálogo recebido como parâmetro. |
| `arquivos.py`, `calculos.py` | Leitura CSV/JSON e soma, preservadas do capítulo 4. |
| `aplicacao.py` | Leitura, consulta única, validação e resumo em memória. |
| `01` a `06` | Observação, consumo e falhas, na ordem do capítulo. |
| `solucao_exercicio.py` | Lote rejeitado porque falta Transporte no catálogo. |
| `solucao_desafio.py` | Conflito D002 bloqueia o lote, mesmo com catálogo válido. |
| `dados/` | Os mesmos sete arquivos fictícios do capítulo 4. |
| `verificar_capitulo.py` | Contratos, regressões e requisições HTTP reais locais. |
| `evidencias/` | Pasta para guardar os registros de sua própria execução. |

## Limites e decisões

- Contrato do catálogo: objeto com exatamente `versao` e `categorias`; inteiro exato 1; 1–20 textos únicos, sem espaços externos ou controles e com no máximo 30 caracteres. Preserva acentos e maiúsculas; não normaliza Unicode automaticamente.
- A versão identifica o formato, não o histórico das categorias. Consulta uma vez por lote; nova execução consulta novamente.
- Resposta integrada: status 200, `application/json`, UTF-8, até 32.768 bytes do corpo entregue por Requests. O adaptador lê blocos de até 1.024 bytes e rejeita antes de acumular acima do limite; não é um limitador do total de bytes da rede, dos cabeçalhos ou de todos os recursos internos da biblioteca.
- Timeout padrão: 1 s para conexão e 2 s para leitura; não há prazo global de conclusão. A rota lenta espera 3 s. Durante leitura progressiva, timeout pode aparecer como falha de comunicação HTTP. Em alguns Windows, a ausência de servidor no loopback também chega como `ConnectTimeout` (em vez de recusa imediata); o cliente traduz isso para a mesma falha de comunicação HTTP prevista no roteiro. Sem retry, cache ou retorno alternativo silencioso.
- Os limites monetários, arquivos de até 1 MiB e lotes de até 1.000 registros continuam os do capítulo 4. Arquivo inválido impede a consulta. Catálogo indisponível impede validação e totalização. Conflito de identificador bloqueia o lote inteiro.
- O servidor de apoio usa recursos internos para permitir conexões durante os casos de atraso; isso não introduz processamento concorrente de lotes na aplicação. A trilha do leitor continua sequencial, com uma execução de aplicação por vez.
- HTTP, JSON e categoria permitida não comprovam correção semântica da despesa. Não há aprovação fiscal/contábil real. O catálogo não recebe os dados do lote.
- `01_observar_resposta.py` é uma primeira observação da rota conhecida, com `.json()` direto. A aplicação usa `cliente_catalogo.py`, com validações e limites.
- Rotas de teste adicionais cobrem 204, ausência de tipo, chave JSON repetida, NaN, UTF-8 inválido, tamanho no limite/acima e falha durante o corpo. O servidor é fornecido pronto; não use como serviço público.
