using UnityEngine;

namespace TecnologiaNaPratica
{
    [CreateAssetMenu(menuName = "Tecnologia na Pratica/Onda")]
    public sealed class OndaDados : ScriptableObject
    {
        public string titulo;
        [Min(0)]
        public int perseguidores = 5, atiradores, resistentes;
        [Min(.2f)]
        public float intervalo = 1.1f;
        public int Total => perseguidores + atiradores + resistentes;

        public int Tipo(int indice)
        {
            if (indice < perseguidores)
                return 0;
            return indice < perseguidores + atiradores ? 1 : 2;
        }
    }
}
