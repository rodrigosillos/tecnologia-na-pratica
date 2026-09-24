# RC1 — material do leitor

Base editorial: manuscrito consolidado R02.

Foram organizadas dez pastas de capítulos, preservadas as fontes e configurações correspondentes, acrescentados README de navegação e trechos de consulta e incorporada a verificação de bind mount já aprovada na R02.

Não foram incluídos os manuscritos, a capa, executores internos, testes de homologação, resultados brutos, logs, imagens TAR, capturas ou backups. Os arquivos de exemplo em `dados-host` e o segredo fictício são exemplos públicos do laboratório, não dados de uma sessão.

Três notas de metadados foram atualizadas para separar estados operacionais de notas antigas de produção: aviso do estado do capítulo 5; limite da interpretação dos controles no capítulo 9; remoção de uma próxima entrega editorial já concluída no estado final do capítulo 10. Nenhum comando de execução ou campo operacional foi modificado nesses estados.

Nenhuma licença de código ou URL pública foi inventada. A escolha de distribuição e a edição pública definitiva dependem do fechamento pelo autor. Uma futura versão deve possuir identificação própria, sem substituir silenciosamente a versão vinculada ao livro.

# Revisão de distribuição MIT-R01

Data da revisão: 2026-09-24.

Foi acrescentada a licença MIT ao código e às configurações originais do laboratório de Docker, com escopo explícito em `LICENCA_ESCOPO.md`. Foram criados `LICENSE`, `LICENCA_ESCOPO.md` e `.gitattributes` (`* -text`) para preservar bytes na distribuição Git.

Os arquivos de software e configuração herdados da RC1 original **não** foram modificados. Ajustes limitam-se à documentação de navegação/metadados (`README.md`, `LEIA_PRIMEIRO.md`, `ALTERACOES.md`, `VERSAO.json`) e ao recálculo de `MANIFESTO_SHA256.json`.

A identificação `RC1` permanece para esta primeira publicação licenciada; a revisão `MIT-R01` distingue a distribuição com MIT da preparação RC1 anterior, em que a licença de código ainda constava como pendente.
