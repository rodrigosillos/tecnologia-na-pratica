using UnityEngine;

namespace TecnologiaNaPratica.QuebraBlocos
{
    public sealed class EfeitoPedra : MonoBehaviour
    {
        SpriteRenderer imagem;
        Vector2 velocidade;
        float restante = .32f;
        public static void Criar(SpriteRenderer origem)
        {
            for (int i = 0; i < 3; i++)
            {
                var go = new GameObject("Fragmento visual");
                go.transform.position = origem.transform.position;
                go.transform.localScale = origem.transform.lossyScale * Random.Range(.1f, .17f);
                var efeito = go.AddComponent<EfeitoPedra>();
                efeito.imagem = go.AddComponent<SpriteRenderer>();
                efeito.imagem.sprite = origem.sprite;
                efeito.imagem.sortingOrder = 6;
                efeito.velocidade = new Vector2((i - 1) * 1.5f, Random.Range(.5f, 1.8f));
            }
        }
        void Update()
        {
            restante -= Time.deltaTime;
            if (restante <= 0) { Destroy(gameObject); return; }
            velocidade.y -= 5f * Time.deltaTime;
            transform.position += (Vector3)(velocidade * Time.deltaTime);
            transform.Rotate(0, 0, 160f * Time.deltaTime);
            imagem.color = new Color(1, 1, 1, restante / .32f);
        }
        public static void Limpar()
        {
            foreach (var efeito in FindObjectsByType<EfeitoPedra>(FindObjectsSortMode.None))
                Destroy(efeito.gameObject);
        }
    }
}
