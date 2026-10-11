using UnityEngine;

namespace TecnologiaNaPratica
{
    public enum TipoContato
    {
        Cristal,
        Checkpoint,
        Espinhos,
        Portal
    }

    public sealed class ContatoFase : MonoBehaviour
    {
        public Campanha controle;
        public TipoContato tipo;
        public int id;
        public SpriteRenderer visual;
        public void AtualizarColeta()
        {
            if (tipo == TipoContato.Cristal)
                gameObject.SetActive(!Campanha.Sessao.Coletado(id));
            if (tipo == TipoContato.Checkpoint)
                visual.color = Campanha.Sessao.checkpoint >= id ? Color.cyan : Color.white;
        }

        void OnTriggerEnter2D(Collider2D outro)
        {
            Tocar(outro);
        }

        void OnTriggerStay2D(Collider2D outro)
        {
            if (tipo == TipoContato.Espinhos)
                Tocar(outro);
        }

        void Tocar(Collider2D outro)
        {
            if (!controle.Jogando || !outro.GetComponent<MotorPlataforma>())
                return;
            switch (tipo)
            {
                case TipoContato.Cristal:
                    Campanha.Sessao.Coletar(id);
                    controle.Salvar();
                    controle.Som.Tocar(880);
                    gameObject.SetActive(false);
                    break;
                case TipoContato.Checkpoint:
                    controle.Checkpoint(id);
                    AtualizarColeta();
                    break;
                case TipoContato.Espinhos:
                    controle.Jogador.Saude.ReceberDano(1, transform.position);
                    break;
                case TipoContato.Portal:
                    controle.SairDaFase();
                    break;
            }
        }
    }
}
