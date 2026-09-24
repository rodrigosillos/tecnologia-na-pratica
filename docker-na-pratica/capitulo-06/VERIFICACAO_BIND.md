# Conferir a origem antes de montar — Capítulo 6

Este é o bloco PowerShell aprovado e incorporado à R02. Use-o na pasta `laboratorio/catalogo-estudos`, depois de preparar `dados-host/anotacoes.json`, antes do comando de montagem apresentado no livro.

```powershell
$pasta = Join-Path (Get-Location).Path 'dados-host'
$arquivo = Join-Path $pasta 'anotacoes.json'
if (-not (Test-Path -LiteralPath $pasta -PathType Container)) {
    throw 'Pasta de origem ausente. Nao prossiga com o mount.'
}
if (-not (Test-Path -LiteralPath $arquivo -PathType Leaf)) {
    throw 'Arquivo de anotacoes ausente. Nao prossiga.'
}
$origem = (Resolve-Path -LiteralPath $pasta).Path
```

Se houver exceção, **interrompa a sequência**. Não continue com uma variável antiga e não crie uma pasta vazia apenas para contornar o aviso. O código não lê nem valida toda a estrutura do JSON: confira também o conteúdo pela aplicação depois da montagem.

Na execução de referência Windows/Docker Desktop, a montagem de uma origem previamente ausente foi aceita e o caminho passou a existir. Isso não é evidência de que os dados esperados foram encontrados nem regra universal de todo Engine. O livro distingue esse registro da recusa padrão descrita na documentação do Docker.

O comando seguinte mantém a origem em `$origem` e acesso `readonly`. Não amplia permissões. Para Bash/Zsh, a atribuição de caminho conservada no capítulo não verifica existência; confirme pasta e arquivo antes de montar, como orienta a R02. O pacote não afirma homologação de todas as variações de shell.
