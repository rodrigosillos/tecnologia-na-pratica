using System;

namespace TecnologiaNaPratica
{
    public enum EstadoArena
    {
        Menu,
        Combate,
        Melhoria,
        Pausa,
        Vitoria,
        Derrota
    }

    public sealed class ProgressoArena
    {
        public EstadoArena Estado { get; private set; } = EstadoArena.Menu;
        public int Onda { get; private set; }
        public int Potencia { get; private set; }
        public int Agilidade { get; private set; }
        public int Vitalidade { get; private set; }
        public int Abates { get; private set; }

        public void Iniciar()
        {
            Onda = 0;
            Potencia = Agilidade = Vitalidade = Abates = 0;
            Estado = EstadoArena.Combate;
        }

        public void Abater()
        {
            if (Estado == EstadoArena.Combate)
                Abates++;
        }

        public void ConcluirOnda(int total)
        {
            if (Estado == EstadoArena.Combate)
                Estado = Onda + 1 >= total ? EstadoArena.Vitoria : EstadoArena.Melhoria;
        }

        public bool Melhorar(int indice)
        {
            if (Estado != EstadoArena.Melhoria || indice < 0 || indice > 2)
                return false;
            if ((indice == 0 && Potencia >= 3) || (indice == 1 && Agilidade >= 3) || (indice == 2 && Vitalidade >= 3))
                return false;
            if (indice == 0)
                Potencia = Math.Min(3, Potencia + 1);
            if (indice == 1)
                Agilidade = Math.Min(3, Agilidade + 1);
            if (indice == 2)
                Vitalidade = Math.Min(3, Vitalidade + 1);
            Onda++;
            Estado = EstadoArena.Combate;
            return true;
        }

        public void Pausar()
        {
            if (Estado == EstadoArena.Combate)
                Estado = EstadoArena.Pausa;
        }

        public void Retomar()
        {
            if (Estado == EstadoArena.Pausa)
                Estado = EstadoArena.Combate;
        }

        public void Perder()
        {
            if (Estado == EstadoArena.Combate)
                Estado = EstadoArena.Derrota;
        }

        public void Menu()
        {
            Estado = EstadoArena.Menu;
        }
    }
}
