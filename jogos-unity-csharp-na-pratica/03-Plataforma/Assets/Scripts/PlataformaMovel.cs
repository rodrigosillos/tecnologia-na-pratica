using UnityEngine;

namespace TecnologiaNaPratica
{
    [RequireComponent(typeof(Rigidbody2D))]
    public sealed class PlataformaMovel : MonoBehaviour
    {
        public Vector2 deslocamento = new Vector2(4, 0);
        public float periodo = 4;
        Vector2 origem;
        Rigidbody2D corpo;
        float tempo;
        public Vector2 Velocidade { get; private set; }

        void Awake()
        {
            corpo = GetComponent<Rigidbody2D>();
            origem = corpo.position;
        }

        public void Reiniciar()
        {
            tempo = 0;
            corpo.position = origem;
            Velocidade = Vector2.zero;
        }

        void FixedUpdate()
        {
            tempo += Time.fixedDeltaTime;
            Vector2 alvo = origem + deslocamento * (.5f - .5f * Mathf.Cos(tempo * 2 * Mathf.PI / periodo));
            Velocidade = (alvo - corpo.position) / Time.fixedDeltaTime;
            corpo.MovePosition(alvo);
        }
    }
}
