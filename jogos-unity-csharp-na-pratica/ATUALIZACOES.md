# Atualizações dos laboratórios

## 1.0.0-rc.2 — 11 de outubro de 2026

Ao caminhar ou correr, o explorador agora alterna os passos na arena e na plataforma. O novo `CicloPassos.cs` movimenta uma malha que usa a textura original: pernas alternadas, flexão dos joelhos e cadência proporcional à velocidade.

Na plataforma, `AnimacaoExplorador.cs` mantém os estados parado e saltando e aplica a articulação durante a corrida. Na arena, `JogadorArena.cs` informa a direção e a velocidade ao ciclo. Não é necessário recriar as cenas. Abra o projeto e execute a cena inicial indicada no README.

Esta é uma melhoria visual complementar ao conteúdo do livro. As regras de movimento, colisões, combate e progressão permanecem as mesmas; o quebra-blocos não foi alterado. As ilustrações e licenças foram preservadas.

Os executáveis Windows foram recompilados com Unity 6000.3.15f1, sem as ferramentas privadas usadas para gravar anúncios. Os roteiros de execução passaram: 14 verificações da arena e 16 da plataforma. Também foram inspecionados quadros sucessivos dos passos. Esses testes não equivalem a uma sessão humana completa de balanceamento.

Os testes EditMode/PlayMode e a importação limpa registrados na RC1 são evidências históricas, não novas execuções na RC2. Consulte VALIDACAO.json.

## 1.0.0-rc.1 — revisão documental L01

Primeira distribuição pública dos três projetos, com código original sob MIT e ilustrações autorizadas para os jogos dos leitores, inclusive comerciais, com os créditos indicados.
