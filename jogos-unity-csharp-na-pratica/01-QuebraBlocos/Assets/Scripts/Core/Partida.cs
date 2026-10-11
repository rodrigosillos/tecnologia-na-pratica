using System;

namespace TecnologiaNaPratica.QuebraBlocos
{
    public enum EstadoPartida { Menu, Preparando, Jogando, Pausado, Vitoria, Derrota }

    // Regra pura: não depende de GameObject, cena, áudio ou interface.
    public sealed class Partida
    {
        public EstadoPartida Estado { get; private set; } = EstadoPartida.Menu;
        public int Vidas { get; private set; }
        public int Pontos { get; private set; }
        public int Fase { get; private set; }
        public int BlocosRestantes { get; private set; }
        public event Action Mudou;
        EstadoPartida estadoAntesDaPausa;

        public void Iniciar(int blocos)
        {
            if (blocos <= 0) throw new ArgumentOutOfRangeException(nameof(blocos));
            Vidas = 3;
            Pontos = 0;
            Fase = 0;
            BlocosRestantes = blocos;
            Estado = EstadoPartida.Preparando;
            Mudou?.Invoke();
        }

        public bool Lancar()
        {
            if (Estado != EstadoPartida.Preparando) return false;
            Estado = EstadoPartida.Jogando;
            Mudou?.Invoke();
            return true;
        }

        public bool PerderBola()
        {
            if (Estado != EstadoPartida.Jogando) return false;
            Vidas = Math.Max(0, Vidas - 1);
            Estado = Vidas == 0 ? EstadoPartida.Derrota : EstadoPartida.Preparando;
            Mudou?.Invoke();
            return true;
        }

        public bool DestruirBloco(int pontos)
        {
            if (Estado != EstadoPartida.Jogando || BlocosRestantes <= 0) return false;
            if (pontos < 0) throw new ArgumentOutOfRangeException(nameof(pontos));
            Pontos += pontos;
            BlocosRestantes--;
            Mudou?.Invoke();
            return true;
        }

        public void Avancar(int totalFases, int blocosDaProxima)
        {
            if (Estado != EstadoPartida.Jogando || BlocosRestantes != 0) return;
            if (Fase + 1 >= totalFases) Estado = EstadoPartida.Vitoria;
            else
            {
                if (blocosDaProxima <= 0) throw new ArgumentOutOfRangeException(nameof(blocosDaProxima));
                Fase++;
                BlocosRestantes = blocosDaProxima;
                Estado = EstadoPartida.Preparando;
            }
            Mudou?.Invoke();
        }

        public void AlternarPausa()
        {
            if (Estado == EstadoPartida.Pausado) Estado = estadoAntesDaPausa;
            else if (Estado == EstadoPartida.Jogando || Estado == EstadoPartida.Preparando)
            {
                estadoAntesDaPausa = Estado;
                Estado = EstadoPartida.Pausado;
            }
            else return;
            Mudou?.Invoke();
        }

        public void Menu()
        {
            Estado = EstadoPartida.Menu;
            Mudou?.Invoke();
        }
    }
}
