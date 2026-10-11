# Marcos de estudo e resultados observáveis

Cada marco é uma experiência sobre uma cópia da referência integrada. Salve a cópia antes da mudança e anote o valor original. Ao final, restaure esse valor ou conserve a experiência em outra cena. Não apresente esses marcos como versões históricas do código.

| Capítulos | Referência | Experiência e conferência |
|---|---|---|
| 1–2 | Um dos três projetos | Abrir no editor fixado; localizar Assets, Packages e ProjectSettings; reproduzir menu e partida. |
| 3–4 | 01-QuebraBlocos | Prever uma alteração de pontos; distinguir Update, FixedUpdate e estado da partida; testar a hipótese. |
| 5 | Cena nova Capitulo05, conforme o livro | Adicionar somente RaqueteBasica à raquete; conferir deslocamento e limites. Não adicionar Raquete ao mesmo objeto. |
| 6 | QuebraBlocos | Abrir a cena integrada; variar velocidade da bola em uma cópia; verificar rebote, contato lateral e detecção contínua. |
| 7 | QuebraBlocos | Alterar uma formação duplicada; conferir blocos restantes, pontuação, vida e avanço único. |
| 8 | QuebraBlocos | Conferir menu, pausa, derrota, volume zero, reinício e vitória; executar os testes antes de criar uma quarta formação. |
| 9 | Arena | Medir deslocamento reto e diagonal por igual tempo; mover à esquerda mirando à direita; examinar prefab e instância. |
| 10 | Arena | Observar perseguidor, atirador e tanque; identificar anúncio e intervalo de disparo; alterar um parâmetro por vez. |
| 11 | Arena | Conferir invulnerabilidade com impactos próximos, oposição entre equipes e remoção do projétil após contato. |
| 12 | Arena | Duplicar um asset de onda; distinguir emitidos de vivos; terminar uma onda e escolher exatamente uma melhoria. |
| 13 | Arena | Contar objetos antes e depois do reaproveitamento; verificar com Profiler; registrar hardware antes de comparar desempenho. |
| 14 | Fase1 | Duplicar a cena e desativar inimigos; descrever o contrato de morte, retorno e transição. |
| 15 | Cópia de Fase1 | Comparar salto curto e longo; medir aceleração e freio; testar as janelas de salto sem perigos. |
| 16 | Fase1/Fase2 | Ativar Gizmos; conferir célula 2×1, Composite Collider, passagem por baixo e movimento da ponte. |
| 17 | Fase1 | Observar corrida, salto, dano e limites da câmera; separar o sprite do collider. |
| 18 | Fase1/Fase3 | Identificar patrulheiro, voador, sentinela e guardião; conferir anúncio de ataque e restauração após morte. |
| 19 | Projeto de testes | Usar arquivo temporário; validar fase, checkpoint e cristais; corromper apenas a cópia de teste e conferir backup. |
| 20 | Fase1 → Fase2 → Fase3 | Atravessar os portais; conferir checkpoint zerado, cristais preservados e guardião bloqueando a última saída. |
| 21 | Qualquer cena da plataforma | Navegar só por teclado; pausar em combate; zerar os canais de áudio; usar a opção de reduzir efeitos. |
| 22 | Campanha completa | Executar regras e roteiro do player; registrar uma sessão humana, mortes, hesitações e compreensão dos avisos. |
| 23 | Build Windows | Extração nova em outra pasta; executar junto de todos os arquivos; conferir versão e SHA-256. |
| 24 | Sua cópia modificada | Preparar um vídeo e uma ficha: objetivo, contribuição própria, decisão, evidência e limite. |

## Diagnóstico rápido

- Referência Missing: confira se o .meta foi preservado e se a pasta correta foi aberta. Não crie componentes duplicados para tentar compensar uma referência vazia.
- Entrada não funciona: confira Game com foco, Input System habilitado e estado da partida. Interfaces também precisam do EventSystem.
- Tilemap sem chão: confira Layer Solo, Rigidbody2D estático, TilemapCollider2D, CompositeCollider2D e TerrenoFisico. A transformação do tile deve permanecer identidade.
- Movimento diferente: confira escala de tempo, gravidade e passo físico antes de alterar a velocidade.
- Alteração some: não execute o gerador de referência depois de modificar seus assets sem preservar uma cópia.
- Pacote não abre: extraia tudo antes de executar. O .exe sozinho não é a distribuição completa.

## Arquivos de progresso

A plataforma usa Application.persistentDataPath e progresso-v1.json, com cópia .bak e escrita intermediária .tmp. Localize o caminho pela aplicação em vez de supor o nome da pasta do usuário.
Os testes do executável usam um diretório isolado. Faça experiências destrutivas somente com dados de teste.
Vida, velocidade e posições de inimigos não são persistidas. Cristais, fase, checkpoint, mortes e conclusão compõem a sessão salva.

## Desafios

1. Uma quarta formação no quebra-blocos: referências válidas, número de impactos coerente e avanço único.
2. Um quarto adversário na arena: silhueta e regra reconhecíveis, configuração restaurada no reaproveitamento e condição de fim de onda preservada.
3. Uma fase autoral: intenção clara, percurso realizável, retorno seguro e encontro final compreensível.

Os enunciados completos, as 48 soluções comentadas e a explicação dos sistemas pertencem ao livro. O laboratório oferece os arquivos executáveis para acompanhar, investigar e modificar.
