using UnityEngine;

namespace TecnologiaNaPratica
{
    public sealed class InimigoPlataforma : MonoBehaviour
    {
        public Campanha controle;
        public SpriteRenderer visual;
        public int tipo;
        public float alcance = 2;
        Vector2 origem;
        float tempo, proximo, aviso;
        int direcao = 1;
        Vida vida;
        public Vida Saude => vida;
        public bool Chefe => tipo == 3;

        void Awake()
        {
            origem = transform.position;
            vida = GetComponent<Vida>();
            vida.Invulnerabilidade = .08f;
        }

        void OnEnable()
        {
            GetComponent<Vida>().Morreu += Morreu;
        }

        void OnDisable()
        {
            if (vida)
                vida.Morreu -= Morreu;
        }

        void Morreu()
        {
            controle.Som.Tocar(280);
            gameObject.SetActive(false);
        }

        public void Reiniciar()
        {
            gameObject.SetActive(true);
            transform.position = origem;
            tempo = 0;
            aviso = 0;
            proximo = Time.time + 2;
            direcao = 1;
            vida.Restaurar(Chefe ? 12 : tipo == 2 ? 3 : 2);
            visual.color = Color.white;
        }

        void Update()
        {
            if (!controle.Jogando)
                return;
            tempo += Time.deltaTime;
            Vector2 pos = transform.position;
            if (tipo == 0)
            {
                pos.x += direcao * 1.4f * Time.deltaTime;
                if (Mathf.Abs(pos.x - origem.x) > alcance)
                    direcao *= -1;
            }

            if (tipo == 1)
            {
                pos = origem + new Vector2(Mathf.Sin(tempo * 1.6f) * alcance, Mathf.Sin(tempo * 3) * .4f);
            }

            if (tipo >= 2)
            {
                float dx = controle.Jogador.Corpo.position.x - pos.x;
                direcao = dx >= 0 ? 1 : -1;
                if (aviso > 0)
                {
                    visual.color = new Color(1, .52f, .2f);
                    if (Time.time >= aviso)
                    {
                        controle.Projeteis.Disparar(pos + Vector2.right * direcao * .7f, Vector2.right * direcao, 1, true);
                        if (Chefe)
                            for (int i = -1; i <= 1; i += 2)
                                controle.Projeteis.Disparar(pos + Vector2.right * direcao * .7f, new Vector2(direcao, i * .35f), 1, true);
                        aviso = 0;
                        proximo = Time.time + (Chefe ? 1.8f : 2.8f);
                    }
                }
                else
                {
                    visual.color = Color.white;
                    if (Mathf.Abs(dx) < 12 && Time.time >= proximo)
                        aviso = Time.time + .8f;
                }
            }
            else
                visual.color = Time.time < vida.ProtegidoAte ? new Color(1, .7f, .4f) : Color.white;
            visual.flipX = direcao > 0;
            transform.position = pos;
            if (Vector2.Distance(pos, controle.Jogador.Corpo.position) < (Chefe ? 1 : .7f))
                controle.Jogador.Saude.ReceberDano(1, pos);
        }
    }
}
