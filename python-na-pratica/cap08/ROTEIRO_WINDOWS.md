# Homologação Windows — capítulo 8 R01

**Escopo obrigatório: percurso local. Extensão autenticada: opcional.** Não é necessário obter chave para concluir este roteiro local.

## Preparar

Extraia `cap08` ao lado de `cap07`. Preserve os arquivos homologados dos capítulos anteriores. Na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe --version
$PSVersionTable.PSVersion
chcp
.\.venv\Scripts\python.exe -m pip install -r .\cap08\requirements.txt
.\.venv\Scripts\python.exe -m pip check
Remove-Item Env:PYTHON_PRATICA_IA_MAX_SAIDA -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe .\cap08\verificar_capitulo.py
$LASTEXITCODE
```

Esperado: Python 3.14.7, SDK 3.24.0, nenhuma dependência quebrada; **95/95**, zero falhas, `aprovado_local`, saída 0, chamadas reais 0. O verificador isola a configuração dos testes e não utiliza a chave do leitor, mesmo se houver alguma no ambiente.

Copie o JSON recém-gerado para `cap08/evidencias/relatorio-windows-python314.json`, mantendo o original. Use o caminho impresso pelo programa.

## Percurso manual

Execute um comando por vez e confira `$LASTEXITCODE` logo depois. Os exemplos usam pastas novas. Se já existirem, preserve-as e escolha outro destino com `--destino`, ajustando `--pacote` em 02/03.

```powershell
.\.venv\Scripts\python.exe .\cap08\01_preparar.py
.\.venv\Scripts\python.exe .\cap08\02_inspecionar.py
.\.venv\Scripts\python.exe .\cap08\03_revisar.py --revisao .\cap08\revisoes\aceite_invalido.json --destino .\cap08\gerados\aceite-invalido
.\.venv\Scripts\python.exe .\cap08\03_revisar.py --revisao .\cap08\gerados\reproducao\revisao_pendente.json --destino .\cap08\gerados\pendente
.\.venv\Scripts\python.exe .\cap08\03_revisar.py --revisao .\cap08\revisoes\decisoes_exemplo.json
.\.venv\Scripts\python.exe .\cap08\05_examinar_erros.py
.\.venv\Scripts\python.exe .\cap08\solucao_desafio.py
```

| Comando | Esperado | Exit |
| --- | --- | ---: |
| 01 | Três sugestões sintéticas, três revisões pendentes, zero gravações no banco. | 0 |
| 02 | T001: data pendente; T002: campos preenchidos; T003: categoria pendente. Todas aguardam revisão. | 0 |
| 03 com aceite inválido | Bloqueio por data; pasta `aceite-invalido` não criada. | 1 |
| 03 com revisão pendente | Bloqueio por revisor vazio ou decisão pendente; pasta `pendente` não criada. | 1 |
| 03 com decisões de exemplo | Dois registros, um rejeitado, total 53.50; banco não utilizado. | 0 |
| 05 | Dez casos bloqueados; categoria sem suporte e subtotal como total aguardam revisão. | 0 |
| Desafio | Categoria Materiais e trecho Café e lanche; solução comentada Alimentação. | 0 |

Confira os arquivos UTF-8 em `gerados/revisado`:

- D101: 2026-09-11, Transporte, 35.00.
- D102: 2026-09-12, Alimentação, 18.50.
- D103 ausente do lote; rejeição de T003 registrada na trilha.
- Original de T001 com data null; final com 2026-09-11 e referência à mensagem complementar.
- Total 53.50, `persistencia: nao_executada`.

Reexecute 01 e 03 com os mesmos destinos existentes. Esperado: saída 1, mensagem de pasta existente e preservação dos arquivos anteriores. Não há necessidade de reimportar no PostgreSQL para testar este capítulo.

## API sem ativação

```powershell
.\.venv\Scripts\python.exe .\cap08\04_extrair_real.py
$LASTEXITCODE
```

Esperado: desativada, saída 2, nenhuma chamada. Se não houver chave na sessão, o comando abaixo também não faz chamada:

```powershell
.\.venv\Scripts\python.exe .\cap08\04_extrair_real.py --confirmar-envio
$LASTEXITCODE
```

Esperado sem chave: saída 1, configuração ausente. **Se houver chave, não use esse segundo comando como teste de bloqueio:** ele autoriza uma tentativa real. A condição sem chave já é exercitada pelo verificador com ambiente isolado.

## Extensão real opcional

Pode permanecer “não executada por ausência de chave”. Isso não bloqueia a aprovação local nem a continuidade editorial.

Quando houver acesso e decisão de usar a API, seguir o README: carregar a chave na sessão, conferir contexto e cobrança, executar 04 explicitamente, inspecionar o pacote com 02 e preencher uma revisão própria. Use uma pasta nova. Registre modelo, SDK, origem, uso e resultado. Não envie chave ou cabeçalhos.

Para T001, o critério semântico é valor 35.00, data null e nenhuma informação inventada. A categoria Transporte precisa ser conferida contra a descrição. Uma resposta compatível com o esquema não encerra a revisão automaticamente.

## Material a devolver

1. `cap08/evidencias/relatorio-windows-python314.json`.
2. `cap08/REGISTRO_WINDOWS.md`, preenchido a partir do modelo.
3. Se possível, o ZIP atualizado, preservando os arquivos técnicos e adicionando as evidências.

Se a extensão real for realizada, incluir seus arquivos e a revisão; caso contrário, registrar “não executada — opcional”. Registrar cp850 separadamente da legibilidade do JSON UTF-8.
