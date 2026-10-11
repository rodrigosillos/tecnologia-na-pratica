using System.Collections;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace TecnologiaNaPratica
{
    public enum EstadoAventura
    {
        Menu,
        Jogando,
        Pausa,
        Retorno,
        Transicao,
        Vitoria
    }

    public sealed class Campanha : MonoBehaviour
    {
        public static DadosProgresso Sessao = new DadosProgresso();
        public static bool EntradaDireta;
        public static string PastaTeste;
        public int indice;
        public string titulo;
        public MotorPlataforma Jogador;
        public ReservaProjeteis Projeteis;
        public Vector2[] checkpoints;
        public InimigoPlataforma[] inimigos;
        public ContatoFase[] contatos;
        public PlataformaMovel[] moveis;
        public EstadoAventura Estado { get; private set; } = EstadoAventura.Menu;
        public bool Jogando => Estado == EstadoAventura.Jogando;
        public bool EfeitosReduzidos { get; private set; }
        public AudioRuinas Som { get; private set; }
        public PainelJogo Interface { get; private set; }
        public RepositorioProgresso Repositorio { get; private set; }

        void Start()
        {
            Som = gameObject.AddComponent<AudioRuinas>();
            Som.Preparar("Plataforma");
            Interface = gameObject.AddComponent<PainelJogo>();
            Interface.Preparar();
            EfeitosReduzidos = PlayerPrefs.GetInt("TNP.Plataforma.Reduzidos", 0) == 1;
            Repositorio = new RepositorioProgresso(Path.Combine(PastaTeste ?? Application.persistentDataPath, "progresso-v1.json"));
            Projeteis.Aquecer(40);
            if (EntradaDireta)
            {
                EntradaDireta = false;
                PrepararFase();
            }
            else
            {
                Jogador.Reposicionar(checkpoints[0]);
                Camera.main.GetComponent<CameraAventura>().Enquadrar();
                Menu();
            }
        }

        void Update()
        {
            if (Interface == null)
                return;
            Interface.Placar.text = Estado == EstadoAventura.Menu ? "TECNOLOGIA NA PRÁTICA  •  LABORATÓRIO 03" : $"VIDA {Jogador.Saude.Atual}/5    FASE {indice + 1}/3    CRISTAIS {Sessao.Total}    CHECKPOINT {Sessao.checkpoint}";
            Interface.Dica.text = Jogando ? (Repositorio.Aviso != "" ? Repositorio.Aviso : titulo + "  •  A/D: mover  |  Espaço: pular  |  J / clique: disparar  |  Esc: pausa") : "Rodrigo Sillos  •  Tecnologia na Prática";
        }

        public void NovaPartida()
        {
            Sessao = new DadosProgresso();
            Repositorio.Salvar(Sessao);
            CarregarCena(0);
        }

        public void Continuar()
        {
            var d = Repositorio.Carregar();
            if (d == null)
            {
                Menu();
                return;
            }

            Sessao = d;
            if (d.concluido)
            {
                Vitoria();
                return;
            }

            CarregarCena(d.fase);
        }

        public void PrepararFase()
        {
            Sessao.fase = indice;
            Estado = EstadoAventura.Jogando;
            Time.timeScale = 1;
            Jogador.Reposicionar(checkpoints[Mathf.Clamp(Sessao.checkpoint, 0, checkpoints.Length - 1)]);
            foreach (var e in inimigos)
                e.Reiniciar();
            foreach (var m in moveis)
                m.Reiniciar();
            foreach (var c in contatos)
                c.AtualizarColeta();
            Projeteis.Limpar();
            Interface.Fechar();
            Camera.main.GetComponent<CameraAventura>().Enquadrar();
        }

        public void Checkpoint(int id)
        {
            if (id <= Sessao.checkpoint || id >= checkpoints.Length)
                return;
            Sessao.checkpoint = id;
            Jogador.Saude.Curar(5);
            Salvar();
            Som.Tocar(990);
        }

        public void Salvar()
        {
            Repositorio.Salvar(Sessao);
        }

        public void Morrer()
        {
            if (!Jogando)
                return;
            Estado = EstadoAventura.Retorno;
            Sessao.mortes++;
            Jogador.Corpo.simulated = false;
            Projeteis.Limpar();
            StartCoroutine(Retornar());
        }

        IEnumerator Retornar()
        {
            yield return new WaitForSeconds(.65f);
            PrepararFase();
            Salvar();
        }

        public void SairDaFase()
        {
            if (!Jogando)
                return;
            if (inimigos.Any(e => e.Chefe && e.gameObject.activeSelf))
            {
                Interface.Dica.text = "Desative o guardião para abrir o portal.";
                Som.Tocar(140);
                return;
            }

            Estado = EstadoAventura.Transicao;
            Projeteis.Limpar();
            if (indice == 2)
            {
                Sessao.concluido = true;
                Salvar();
                Vitoria();
                return;
            }

            Sessao.fase = indice + 1;
            Sessao.checkpoint = 0;
            Salvar();
            CarregarCena(Sessao.fase);
        }

        void CarregarCena(int fase)
        {
            EntradaDireta = true;
            Time.timeScale = 1;
            SceneManager.LoadScene("Fase" + (fase + 1));
        }

        public void AlternarPausa()
        {
            if (Jogando)
            {
                Estado = EstadoAventura.Pausa;
                Time.timeScale = 0;
                Pausa();
            }
            else if (Estado == EstadoAventura.Pausa)
            {
                Estado = EstadoAventura.Jogando;
                Time.timeScale = 1;
                Interface.Fechar();
            }
        }

        void Pausa()
        {
            Interface.Mostrar("PAUSA", "O progresso de cristais e checkpoints é salvo automaticamente.\nInimigos e plataformas aguardam sua volta.", ("CONTINUAR", AlternarPausa), ("CONFIGURAÇÕES", () => Configurar(Pausa)), ("MENU", Menu));
        }

        void Configurar(System.Action voltar)
        {
            Interface.Configurar(Som, voltar, () =>
            {
                EfeitosReduzidos = !EfeitosReduzidos;
                PlayerPrefs.SetInt("TNP.Plataforma.Reduzidos", EfeitosReduzidos ? 1 : 0);
            }, () => EfeitosReduzidos);
        }

        public void Menu()
        {
            Estado = EstadoAventura.Menu;
            Time.timeScale = 0;
            var salvo = Repositorio.Carregar();
            Interface.Mostrar("CAMINHO DO PORTAL", "Explore três trechos das ruínas e enfrente o guardião.\n" + Repositorio.Aviso, (salvo == null ? "NOVA PARTIDA" : "CONTINUAR", salvo == null ? (System.Action)NovaPartida : Continuar), ("INICIAR DO ZERO", () => Interface.Mostrar("RECOMEÇAR?", "Seu progresso atual será substituído por uma nova campanha.", ("SIM, NOVA PARTIDA", NovaPartida), ("VOLTAR", Menu))), ("CONFIGURAÇÕES", () => Configurar(Menu)), ("CRÉDITOS", Creditos), ("SAIR", () => Application.Quit()));
        }

        void Creditos()
        {
            Interface.Mostrar("CRÉDITOS", "Rodrigo Sillos • coleção Tecnologia na Prática\nArte criada com IA; música e efeitos sintetizados pelo projeto.\nDesenvolvido com Unity. Publicação independente.", ("VOLTAR", Menu));
        }

        void Vitoria()
        {
            Estado = EstadoAventura.Vitoria;
            Time.timeScale = 0;
            Interface.Mostrar("O PORTAL ESTÁ ABERTO", $"Você atravessou as três fases.\n{Sessao.Total} cristais encontrados • {Sessao.mortes} retornos ao checkpoint.\nExperimente projetar uma fase sua.", ("MENU", Menu), ("NOVA CAMPANHA", NovaPartida));
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
