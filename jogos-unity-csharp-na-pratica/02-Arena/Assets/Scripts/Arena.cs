using System.Collections.Generic;
using UnityEngine;

namespace TecnologiaNaPratica
{
    public sealed class Arena : MonoBehaviour
    {
        public JogadorArena Jogador;
        public InimigoArena inimigoPrefab;
        public ReservaProjeteis Projeteis;
        public OndaDados[] ondas;
        public ProgressoArena Regras { get; } = new ProgressoArena();
        public PainelJogo Interface { get; private set; }
        public AudioRuinas Som { get; private set; }

        readonly List<InimigoArena> inimigos = new List<InimigoArena>();
        int emitidos, vivos;
        float proximo;
        public bool Jogando => Regras.Estado == EstadoArena.Combate;
        public int Vivos => vivos;
        public int Emitidos => emitidos;
        public IReadOnlyList<InimigoArena> Inimigos => inimigos;

        void Start()
        {
            Som = gameObject.AddComponent<AudioRuinas>();
            Som.Preparar("Arena");
            Interface = gameObject.AddComponent<PainelJogo>();
            Interface.Preparar();
            Projeteis.Aquecer(40);
            for (int i = 0; i < 12; i++)
            {
                var e = Instantiate(inimigoPrefab);
                e.gameObject.SetActive(false);
                inimigos.Add(e);
            }

            Menu();
        }

        public void Iniciar()
        {
            Limpar();
            Regras.Iniciar();
            Time.timeScale = 1;
            Jogador.Restaurar(true);
            ComecarOnda();
        }

        void ComecarOnda()
        {
            emitidos = vivos = 0;
            proximo = Time.time + 1;
            Projeteis.Limpar();
            Interface.Fechar();
            Som.Tocar(440);
        }

        void Update()
        {
            if (Interface == null)
                return;
            Interface.Placar.text = Regras.Estado == EstadoArena.Menu ? "TECNOLOGIA NA PRÁTICA  •  LABORATÓRIO 02" : $"VIDA {Jogador.Saude.Atual}/{Jogador.Saude.Maxima}    ONDA {Regras.Onda + 1}/{ondas.Length}    ROBÔS {vivos}    ABATES {Regras.Abates}";
            Interface.Dica.text = Jogando ? ondas[Regras.Onda].titulo + "  •  WASD / setas: mover   |   mouse: mirar e atirar   |   Esc: pausa" : "Rodrigo Sillos  •  Tecnologia na Prática";
            if (!Jogando)
                return;
            var onda = ondas[Regras.Onda];
            if (emitidos < onda.Total && vivos < 12 && Time.time >= proximo)
            {
                InimigoArena livre = inimigos.Find(e => !e.gameObject.activeSelf);
                if (livre != null)
                {
                    livre.Ativar(this, onda.Tipo(emitidos), PontoSeguro(emitidos));
                    vivos++;
                    emitidos++;
                    proximo = Time.time + onda.intervalo;
                }
            }

            if (emitidos == onda.Total && vivos == 0)
            {
                Regras.ConcluirOnda(ondas.Length);
                Projeteis.Limpar();
                Time.timeScale = 0;
                if (Regras.Estado == EstadoArena.Vitoria)
                    Interface.Mostrar("ARENA LIBERTADA", $"Você venceu as cinco ondas.\n{Regras.Abates} robôs desativados. Experimente outra combinação de melhorias.", ("JOGAR NOVAMENTE", Iniciar), ("MENU", Menu));
                else
                    Interface.Mostrar("ESCOLHA UMA MELHORIA", "A próxima onda começa após sua escolha.\nA vida é restaurada entre ondas; cada melhoria tem limite de três níveis.", ($"Potência {Regras.Potencia}/3 — +1 dano por disparo", () => Melhorar(0)), ($"Agilidade {Regras.Agilidade}/3 — +0,5 de velocidade", () => Melhorar(1)), ($"Vitalidade {Regras.Vitalidade}/3 — +2 de vida máxima", () => Melhorar(2)));
            }
        }

        public Vector2 PontoSeguro(int indice)
        {
            Vector2[] pontos =
            {
                new Vector2(-7.6f, 3.6f),
                new Vector2(7.6f, -3.6f),
                new Vector2(7.6f, 3.6f),
                new Vector2(-7.6f, -3.6f)
            };
            for (int i = 0; i < pontos.Length; i++)
            {
                var p = pontos[(indice + i) % pontos.Length];
                if (Vector2.Distance(p, Jogador.Corpo.position) >= 6)
                    return p;
            }

            return pontos[indice % 4];
        }

        public void Abatido(InimigoArena inimigo)
        {
            if (!Jogando)
                return;
            vivos = Mathf.Max(0, vivos - 1);
            Regras.Abater();
            Som.Tocar(320);
        }

        public void Melhorar(int opcao)
        {
            if (!Regras.Melhorar(opcao))
                return;
            Time.timeScale = 1;
            Jogador.Restaurar(false);
            ComecarOnda();
        }

        public void Perder()
        {
            if (!Jogando)
                return;
            Regras.Perder();
            Time.timeScale = 0;
            Interface.Mostrar("TENTE OUTRA ROTA", "Mantenha distância dos robôs pesados.\nO brilho laranja avisa que o atirador vai disparar.", ("TENTAR NOVAMENTE", Iniciar), ("MENU", Menu));
        }

        public void AlternarPausa()
        {
            if (Jogando)
            {
                Regras.Pausar();
                Time.timeScale = 0;
                MostrarPausa();
            }
            else if (Regras.Estado == EstadoArena.Pausa)
            {
                Regras.Retomar();
                Time.timeScale = 1;
                Interface.Fechar();
            }
        }

        void MostrarPausa()
        {
            Interface.Mostrar("PAUSA", "A simulação está parada.\nMovimento, disparos e surgimento de inimigos aguardam o retorno.", ("CONTINUAR", AlternarPausa), ("CONFIGURAÇÕES", () => Interface.Configurar(Som, MostrarPausa)), ("MENU", Menu));
        }

        public void Menu()
        {
            Limpar();
            Regras.Menu();
            Time.timeScale = 0;
            Interface.Mostrar("ARENA DAS RUÍNAS", "Cinco ondas. Três tipos de robô. Quatro escolhas.\nSobreviva e adapte sua estratégia entre os combates.", ("INICIAR", Iniciar), ("CONFIGURAÇÕES", () => Interface.Configurar(Som, Menu)), ("CRÉDITOS", Creditos), ("SAIR", () => Application.Quit()));
        }

        void Creditos()
        {
            Interface.Mostrar("CRÉDITOS", "Rodrigo Sillos • coleção Tecnologia na Prática\nArte criada com IA; música e efeitos sintetizados pelo projeto.\nDesenvolvido com Unity. Publicação independente.", ("VOLTAR", Menu));
        }

        void Limpar()
        {
            Projeteis.Limpar();
            foreach (var e in inimigos)
                e.gameObject.SetActive(false);
            vivos = emitidos = 0;
        }

        void OnApplicationFocus(bool foco)
        {
            if (!foco && Jogando)
                AlternarPausa();
        }

        void OnDestroy()
        {
            Time.timeScale = 1;
        }
    }
}
