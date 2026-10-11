using UnityEngine;

namespace TecnologiaNaPratica
{
    public sealed class Projetil : MonoBehaviour
    {
        Vector2 direcao;
        int dano, mascara;
        float expira, velocidade;
        SpriteRenderer visual;
        void Awake()
        {
            visual = GetComponentInChildren<SpriteRenderer>();
        }

        public void Ativar(Vector2 origem, Vector2 vetor, int impacto, bool hostil)
        {
            transform.position = origem;
            direcao = vetor.sqrMagnitude > .001f ? vetor.normalized : Vector2.right;
            dano = impacto;
            mascara = (1 << (hostil ? 8 : 9)) | (1 << 10);
            velocidade = hostil ? 5 : 13;
            expira = Time.time + 2.5f;
            gameObject.SetActive(true);
            visual.color = hostil ? new Color(1, .35f, .12f) : Color.cyan;
        }

        void FixedUpdate()
        {
            float passo = velocidade * Time.fixedDeltaTime;
            var hit = Physics2D.CircleCast(transform.position, .08f, direcao, passo, mascara);
            if (hit.collider)
            {
                var alvo = hit.collider.GetComponent<IRecebeDano>();
                alvo?.ReceberDano(dano, transform.position);
                gameObject.SetActive(false);
                return;
            }

            transform.position += (Vector3)(direcao * passo);
            if (Time.time >= expira)
                gameObject.SetActive(false);
        }
    }
}
