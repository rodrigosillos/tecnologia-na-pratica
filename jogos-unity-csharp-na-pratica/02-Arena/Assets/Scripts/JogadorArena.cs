using UnityEngine;

namespace TecnologiaNaPratica
{
    [RequireComponent(typeof(Rigidbody2D), typeof(Vida))]
    public sealed class JogadorArena : MonoBehaviour
    {
        public Arena controle;
        public SpriteRenderer visual;
        public Rigidbody2D Corpo { get; private set; }
        public Vida Saude { get; private set; }

        Entrada entrada;
        Vector2 movimento, mira;
        float proximo;
        void Awake()
        {
            Corpo = GetComponent<Rigidbody2D>();
            Saude = GetComponent<Vida>();
            entrada = new Entrada();
        }

        void OnEnable()
        {
            GetComponent<Vida>().Ferido += Ferido;
            GetComponent<Vida>().Morreu += Morreu;
        }

        void OnDisable()
        {
            Saude.Ferido -= Ferido;
            Saude.Morreu -= Morreu;
        }

        void OnDestroy()
        {
            entrada?.Dispose();
        }

        void Ferido(Vector2 origem)
        {
            controle.Som.Tocar(150);
        }

        void Morreu()
        {
            controle.Perder();
        }

        public void Restaurar(bool inicio)
        {
            if (inicio)
            {
                Corpo.position = Vector2.zero;
                proximo = 0;
            }

            Saude.Restaurar(5 + controle.Regras.Vitalidade * 2);
            Corpo.linearVelocity = Vector2.zero;
        }

        void Update()
        {
            if (entrada.Pausa)
                controle.AlternarPausa();
            if (!controle.Jogando)
            {
                movimento = Vector2.zero;
                return;
            }

            movimento = entrada.Movimento;
            mira = entrada.Mira - Corpo.position;
            if (mira.sqrMagnitude < .001f)
                mira = Vector2.right;
            int indice = Mathf.Abs(mira.y) > Mathf.Abs(mira.x) ? (mira.y > 0 ? 5 : 4) : (movimento.sqrMagnitude > .1f && (int)(Time.time * 9) % 2 == 1 ? 7 : 6);
            visual.sprite = BancoArte.Atual.atores[indice];
            visual.flipX = mira.x < 0 && (indice == 6 || indice == 7);
            visual.color = Time.time < Saude.ProtegidoAte && (int)(Time.time * 16) % 2 == 0 ? new Color(1, .65f, .35f) : Color.white;
            if (entrada.Atirando && Time.time >= proximo)
            {
                controle.Projeteis.Disparar(Corpo.position + mira.normalized * .55f, mira, 1 + controle.Regras.Potencia, false);
                proximo = Time.time + .25f;
                controle.Som.Tocar(660);
            }
        }

        void FixedUpdate()
        {
            if (!controle.Jogando)
            {
                Corpo.linearVelocity = Vector2.zero;
                return;
            }

            var alvo = Corpo.position + movimento * (5 + controle.Regras.Agilidade * .5f) * Time.fixedDeltaTime;
            alvo.x = Mathf.Clamp(alvo.x, -8.25f, 8.25f);
            alvo.y = Mathf.Clamp(alvo.y, -4.1f, 4.1f);
            Corpo.MovePosition(alvo);
        }
    }
}
