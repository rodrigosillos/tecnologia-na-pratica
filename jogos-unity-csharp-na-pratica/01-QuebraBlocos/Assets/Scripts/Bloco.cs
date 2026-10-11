using UnityEngine;

namespace TecnologiaNaPratica.QuebraBlocos
{
    public sealed class Bloco : MonoBehaviour
    {
        [SerializeField] Sprite normal, reforcado, danificado;
        ControlePartida controle;
        int resistencia, pontos;
        bool destruido;
        float ultimoImpacto = float.NegativeInfinity;

        public void Configurar(ControlePartida destino, int vida)
        {
            controle = destino;
            resistencia = Mathf.Clamp(vida, 1, 2);
            pontos = resistencia == 2 ? 150 : 100;
            GetComponent<SpriteRenderer>().sprite = resistencia == 2 ? reforcado : normal;
        }
        public void ReceberImpacto()
        {
            if (destruido || controle.Regras.Estado != EstadoPartida.Jogando) return;
            if (Time.fixedTime - ultimoImpacto < Time.fixedDeltaTime * 0.5f) return;
            ultimoImpacto = Time.fixedTime;
            resistencia--;
            controle.Som.Toque(resistencia > 0 ? 220 : 660, 0.065f);
            if (resistencia > 0) { GetComponent<SpriteRenderer>().sprite = danificado; return; }
            destruido = true;
            GetComponent<Collider2D>().enabled = false;
            EfeitoPedra.Criar(GetComponent<SpriteRenderer>());
            controle.BlocoDestruido(pontos, transform.position);
            Destroy(gameObject);
        }
    }
}
