# Homologação Windows — capítulo 5 R01

Objetivo: comprovar esta entrega no Windows, com o mesmo código e dados. Nenhuma homologação nativa foi antecipada pelo resultado Linux.

1. Extraia `cap05` na raiz do projeto, preservando os arquivos originais. Reutilize `.venv` 3.14.7. Confira o interpretador do editor.
2. Execute a instalação e `pip check` descritos no README. Se um pacote não instalar ou houver conflito, registre a mensagem e pare antes dos exemplos; não considere o ambiente aprovado.
3. Abra dois terminais. No primeiro, inicie `servidor_catalogo.py`. No segundo, execute `01` a `05`; confira status 200, categorias acentuadas e total CSV/JSON 127.50. Observe o código de saída imediatamente depois de cada comando com `$LASTEXITCODE`.
4. Execute os sete argumentos de `06_observar_falhas.py` descritos no README. Todos devem retornar 1; a mensagem deve corresponder à etapa que falhou.
5. Execute `solucao_exercicio.py` e `solucao_desafio.py`. Espere bloqueios no registro 2 (categoria) e registro 4 (D002), respectivamente, sem total e com saída 1.
6. Pare o servidor com Ctrl+C e execute `03_consultar_catalogo.py`. Espere falha de comunicação HTTP e saída 1. Essa falha confirma que o cliente não inventa um catálogo.
7. Execute `verificar_capitulo.py` sem servidor manual. Exija todas as verificações aprovadas e saída 0. O script abre sua própria porta temporária, exercita HTTP real local e salva um JSON com plataforma, Python, dependências, resultados e hashes.
8. Confira o JSON no editor: acentos, números, `sistema: Windows` e `status: aprovado`. Verifique separadamente a legibilidade no console. Se só o terminal exibir acentos incorretos, descreva isso sem mudar valores esperados, sem considerar o texto visual corrigido e sem editar os dados para retirar acentos.
9. Preencha uma cópia de `REGISTRO_WINDOWS_MODELO.md`, chamada `REGISTRO_WINDOWS.md`. Envie-a junto do JSON original recém-gerado. Não substitua a evidência Linux nem reutilize o JSON de outro capítulo.

Para registrar a versão do terminal, pode consultar `$PSVersionTable.PSVersion`. Não publique dados de conta, caminhos privados não necessários ou variáveis de ambiente completas. O JSON inclui o caminho do interpretador para a conferência de ambiente; revise esse campo antes de uma eventual publicação pública.

A aprovação funcional requer 100% dos casos do pacote e integridade dos arquivos. A leitura correta dos acentos no console/editor é uma observação manual separada. Qualquer alteração para corrigir um problema requer nova execução e nova evidência; preserve o registro anterior.
