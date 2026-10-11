using System;
using UnityEngine;

namespace TecnologiaNaPratica
{
    public interface IRecebeDano
    {
        bool ReceberDano(int dano, Vector2 origem);
    }

    public sealed class Vida : MonoBehaviour, IRecebeDano
    {
        public int Atual { get; private set; }
        public int Maxima { get; private set; }

        public float Invulnerabilidade = 0.65f;
        public float ProtegidoAte { get; private set; }

        public event Action Mudou;
        public event Action<Vector2> Ferido;
        public event Action Morreu;
        public void Restaurar(int maxima)
        {
            Maxima = Mathf.Max(1, maxima);
            Atual = Maxima;
            ProtegidoAte = 0;
            Mudou?.Invoke();
        }

        public bool ReceberDano(int dano, Vector2 origem)
        {
            if (dano <= 0 || Atual <= 0 || Time.time < ProtegidoAte || Time.timeScale == 0)
                return false;
            Atual = Mathf.Max(0, Atual - dano);
            ProtegidoAte = Time.time + Invulnerabilidade;
            Mudou?.Invoke();
            Ferido?.Invoke(origem);
            if (Atual == 0)
                Morreu?.Invoke();
            return true;
        }

        public void Curar(int valor)
        {
            if (Atual <= 0)
                return;
            Atual = Mathf.Min(Maxima, Atual + Mathf.Max(0, valor));
            Mudou?.Invoke();
        }
    }
}
