using UnityEngine;

namespace TecnologiaNaPratica
{
    [RequireComponent(typeof(Vida))]
    public sealed class InimigoArena : MonoBehaviour
    {
        public SpriteRenderer visual;
        Arena controle;
        Vida saude;
        int tipo;
        float nascer, proximo, aviso;
        Vector2 alvoTravado;
        public int Tipo => tipo;
        public Vida Saude => saude;

        void Awake()
        {
            saude = GetComponent<Vida>();
            saude.Invulnerabilidade = .08f;
        }

        void OnEnable()
        {
            GetComponent<Vida>().Morreu += Morreu;
        }

        void OnDisable()
        {
            if (saude)
                saude.Morreu -= Morreu;
        }

        public void Ativar(Arena arena, int classe, Vector2 pos)
        {
            controle = arena;
            tipo = classe;
            transform.position = pos;
            aviso = 0;
            nascer = Time.time + .8f;
            proximo = nascer + 1.2f;
            gameObject.SetActive(true);
            saude.Restaurar(tipo == 2 ? 8 : tipo == 1 ? 3 : 2);
            visual.sprite = BancoArte.Atual.atores[8 + tipo];
            visual.color = Color.white;
            float altura = tipo == 2 ? 1.3f : 1;
            visual.transform.localScale = Vector3.one * (altura / visual.sprite.bounds.size.y);
        }

        void Morreu()
        {
            controle.Abatido(this);
            gameObject.SetActive(false);
        }

        void Update()
        {
            if (!controle.Jogando)
                return;
            if (Time.time < nascer)
            {
                visual.color = new Color(.55f, .85f, 1, .45f + (Mathf.Sin(Time.time * 16) + 1) * .2f);
                return;
            }

            Vector2 pos = transform.position, delta = controle.Jogador.Corpo.position - pos;
            visual.flipX = delta.x < 0;
            float distancia = delta.magnitude;
            if (aviso > 0)
            {
                visual.color = new Color(1, .55f, .2f);
                if (Time.time >= aviso)
                {
                    controle.Projeteis.Disparar(pos + alvoTravado * .6f, alvoTravado, 1, true);
                    aviso = 0;
                    proximo = Time.time + 2.2f;
                }

                return;
            }

            visual.color = Time.time < saude.ProtegidoAte ? new Color(1, .65f, .45f) : Color.white;
            if (tipo == 1 && Time.time >= proximo)
            {
                alvoTravado = delta.normalized;
                aviso = Time.time + .6f;
                return;
            }

            float direcao = tipo == 1 ? (distancia > 4.5f ? 1 : distancia < 3 ? -1 : 0) : 1;
            float velocidade = tipo == 2 ? 1.05f : tipo == 1 ? 1.45f : 1.9f;
            pos += delta.normalized * (velocidade * direcao * Time.deltaTime);
            pos.x = Mathf.Clamp(pos.x, -8.3f, 8.3f);
            pos.y = Mathf.Clamp(pos.y, -4.15f, 4.15f);
            transform.position = pos;
            if (distancia < .68f)
                controle.Jogador.Saude.ReceberDano(tipo == 2 ? 2 : 1, pos);
        }
    }
}
