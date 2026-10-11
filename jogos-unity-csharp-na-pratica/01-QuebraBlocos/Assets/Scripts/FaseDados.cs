using UnityEngine;

namespace TecnologiaNaPratica.QuebraBlocos
{
    [CreateAssetMenu(menuName = "Tecnologia na Pratica/Fase de quebra-blocos")]
    public sealed class FaseDados : ScriptableObject
    {
        public string nome;
        [Tooltip("0 = vazio; 1 = pedra; 2 = pedra reforçada")]
        public string[] linhas;
        public int Quantidade()
        {
            int total = 0;
            foreach (string linha in linhas)
                foreach (char c in linha)
                    if (c == '1' || c == '2') total++;
            return total;
        }
    }
}
