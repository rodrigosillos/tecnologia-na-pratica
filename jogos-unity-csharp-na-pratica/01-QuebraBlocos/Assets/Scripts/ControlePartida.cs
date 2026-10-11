using UnityEngine;

namespace TecnologiaNaPratica.QuebraBlocos
{
    public sealed class ControlePartida : MonoBehaviour
    {
        [SerializeField] EntradaJogador entrada;
        [SerializeField] Raquete raquete;
        [SerializeField] Bola bola;
        [SerializeField] Bloco blocoPrefab;
        [SerializeField] Transform campoBlocos;
        [SerializeField] FaseDados[] fases;
        [SerializeField] SomJogo som;
        public Partida Regras { get; } = new Partida();
        public SomJogo Som => som;
        public int Recorde { get; private set; }
        public string NomeFase => fases[Mathf.Clamp(Regras.Fase, 0, fases.Length - 1)].nome;
        const string ChaveRecorde = "TNP.QuebraBlocos.Recorde.v1";
        bool concluirFase;

        void Awake()
        {
            Time.timeScale = 1f;
            Recorde = PlayerPrefs.GetInt(ChaveRecorde, 0);
        }
        void Start() { bola.Parar(); }
        void Update()
        {
            if (entrada.Pausou) Pausar();
            if (entrada.Lancou && Regras.Lancar()) bola.Lancar();
        }
        void LateUpdate()
        {
            if (!concluirFase || Regras.Estado != EstadoPartida.Jogando) return;
            concluirFase = false;
            int proxima = Regras.Fase + 1;
            Regras.Avancar(fases.Length, proxima < fases.Length ? fases[proxima].Quantidade() : 0);
            bola.Parar();
            if (Regras.Estado == EstadoPartida.Preparando)
            {
                GerarFase(Regras.Fase);
                raquete.Centralizar();
                bola.Preparar(Regras.Fase);
            }
            AtualizarRecorde();
        }
        public void Iniciar()
        {
            EfeitoPedra.Limpar();
            Time.timeScale = 1f;
            concluirFase = false;
            GerarFase(0);
            Regras.Iniciar(fases[0].Quantidade());
            raquete.Centralizar();
            bola.Preparar(0);
        }
        public void Pausar()
        {
            Regras.AlternarPausa();
            Time.timeScale = Regras.Estado == EstadoPartida.Pausado ? 0f : 1f;
        }
        public void VoltarAoMenu()
        {
            EfeitoPedra.Limpar();
            AtualizarRecorde();
            Time.timeScale = 1f;
            concluirFase = false;
            bola.Parar();
            LimparBlocos();
            Regras.Menu();
        }
        public void PerderBola()
        {
            if (Regras.BlocosRestantes == 0) return;
            if (!Regras.PerderBola()) return;
            som.Toque(140, 0.18f);
            bola.Parar();
            raquete.Centralizar();
            if (Regras.Estado == EstadoPartida.Preparando) bola.Preparar(Regras.Fase);
            AtualizarRecorde();
        }
        public void BlocoDestruido(int pontos, Vector3 posicao)
        {
            if (!Regras.DestruirBloco(pontos)) return;
            concluirFase = Regras.BlocosRestantes == 0;
        }
        void AtualizarRecorde()
        {
            if (Regras.Pontos <= Recorde) return;
            Recorde = Regras.Pontos;
            PlayerPrefs.SetInt(ChaveRecorde, Recorde);
            PlayerPrefs.Save();
        }
        void LimparBlocos()
        {
            foreach (Transform filho in campoBlocos)
            {
                filho.gameObject.SetActive(false);
                Destroy(filho.gameObject);
            }
        }
        void GerarFase(int indice)
        {
            LimparBlocos();
            string[] linhas = fases[indice].linhas;
            for (int y = 0; y < linhas.Length; y++)
            {
                string linha = linhas[y];
                for (int x = 0; x < linha.Length; x++)
                {
                    if (linha[x] != '1' && linha[x] != '2') continue;
                    Vector3 pos = new Vector3((x - (linha.Length - 1) * 0.5f) * 1.7f, 3.35f - y * 0.85f);
                    Bloco bloco = Instantiate(blocoPrefab, pos, Quaternion.identity, campoBlocos);
                    bloco.Configurar(this, linha[x] - '0');
                }
            }
        }
        void OnApplicationFocus(bool foco)
        {
            if (!foco && (Regras.Estado == EstadoPartida.Jogando || Regras.Estado == EstadoPartida.Preparando)) Pausar();
        }
        void OnDisable() { Time.timeScale = 1f; }
        public void Sair() { Application.Quit(); }
    }
}
