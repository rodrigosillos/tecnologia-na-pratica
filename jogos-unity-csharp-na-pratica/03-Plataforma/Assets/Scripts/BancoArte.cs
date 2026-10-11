using UnityEngine;

namespace TecnologiaNaPratica
{
    public sealed class BancoArte : ScriptableObject
    {
        public Sprite[] ambiente;
        public Sprite[] atores;
        static BancoArte instancia;
        public static BancoArte Atual => instancia ? instancia : instancia = Resources.Load<BancoArte>("BancoArte");

        public static SpriteRenderer Desenhar(string nome, Sprite sprite, Transform pai, Vector2 pos, Vector2 tamanho, int ordem = 0)
        {
            var go = new GameObject(nome);
            go.transform.SetParent(pai, false);
            go.transform.localPosition = pos;
            var r = go.AddComponent<SpriteRenderer>();
            r.sprite = sprite;
            r.sortingOrder = ordem;
            go.transform.localScale = new Vector3(tamanho.x / sprite.bounds.size.x, tamanho.y / sprite.bounds.size.y, 1);
            return r;
        }
    }
}
