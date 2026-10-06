# Origem dos componentes — capítulo 12 R01

A integração mantém os contratos já usados no livro. O pacote é autocontido e não depende de importar pastas de outras entregas.

| Componente | Origem e adaptação |
| --- | --- |
| `extracao/` | Capítulo 8 R01, Entrega 14: módulos, prompts, origens, complementos, casos e revisão didática. Imports internos tornados relativos; lógica e dados preservados. |
| `consulta/` | Capítulo 9 R01, Entrega 16: busca, corpus, prompts, perguntas, casos e validação. Imports internos tornados relativos; lógica e dados preservados. |
| `custos.py` | Controle de estimativas do capítulo 10; imports e caminho de dados adaptados ao pacote. Limite configurado em uma tentativa por invocação real. |
| Núcleo de despesas | Capítulo 11 R01: leitura, regras, catálogo, tentativas, transação, recibo, exportação e logs. Esquema e identificação de aplicação/log alterados para capítulo 12. |
| Persistência e exportação | Recibo passa a incluir proveniência; quinta saída `proveniencia.json`; contrato próprio de recibo do capítulo 12. |
| Coordenação nova | CLI distingue `importar` e `importar-revisado`; revisão revalidada antes da entrada assistida; consulta documental separada da escrita. |
| Extensão real nova | Uma tentativa por comando; transporte SDK exercitado em memória. Arquivos de revisão próprios para cada pacote real; não executada com autenticação nesta entrega. |

A auditoria compara **39 arquivos** reutilizados nos dois pacotes, com zero divergências após normalizar apenas imports relativos nos módulos Python. Os arquivos de dados/prompts são comparados byte a byte. O capítulo 10 terminou com decisão `nao_promover` para a alternativa avaliada; esta entrega não promove essa alternativa nem altera os prompts originais dos capítulos 8/9.

A homologação Windows nativa do capítulo 11 foi recebida e conferida: relatório 97/97 e 23 hashes técnicos compatíveis com o núcleo disponível. O resumo de homologação está em `../VERIFICACAO_RESUMO.md`; os relatórios originais pertencem ao arquivo de auditoria do autor. A conferência técnica compara os arquivos com os hashes recebidos, sem atribuir ao ZIP de origem um hash de outra versão.

`MANIFESTO_SHA256.json` cobre 67 arquivos técnicos desta revisão. Exclui documentos editoriais, evidências, resultados gerados, caches e o próprio manifesto. O SHA do ZIP registra o pacote completo distribuído. Qualquer modificação técnica depois da homologação exige novo manifesto e nova verificação; apenas renomear a evidência não valida uma alteração de código.
