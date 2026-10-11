using UnityEngine;

namespace TecnologiaNaPratica.QuebraBlocos
{
    [RequireComponent(typeof(Rigidbody2D))]
    public sealed class Raquete : MonoBehaviour
    {
        [SerializeField] EntradaJogador entrada;
        [SerializeField] ControlePartida controle;
        [SerializeField, Min(0)] float velocidade = 11f;
        [SerializeField, Min(0)] float limiteCentro = 6.3f;
        Rigidbody2D corpo;
        public float LimiteCentro => limiteCentro;

        void Awake() { corpo = GetComponent<Rigidbody2D>(); }
        void FixedUpdate()
        {
            var estado = controle.Regras.Estado;
            if (estado != EstadoPartida.Jogando && estado != EstadoPartida.Preparando) return;
            float x = corpo.position.x + entrada.Direcao * velocidade * Time.fixedDeltaTime;
            corpo.MovePosition(new Vector2(Mathf.Clamp(x, -limiteCentro, limiteCentro), corpo.position.y));
        }
        public void Centralizar() { corpo.position = new Vector2(0, -4.15f); }
    }
}
