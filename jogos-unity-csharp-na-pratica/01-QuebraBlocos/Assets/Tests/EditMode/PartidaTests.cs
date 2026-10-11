using NUnit.Framework;
using TecnologiaNaPratica.QuebraBlocos;

public sealed class PartidaTests
{
    [Test] public void PerdaDuplicadaDescontaSomenteUmaVida()
    {
        var p = new Partida(); p.Iniciar(2); p.Lancar();
        Assert.IsTrue(p.PerderBola()); Assert.IsFalse(p.PerderBola());
        Assert.AreEqual(2, p.Vidas); Assert.AreEqual(EstadoPartida.Preparando, p.Estado);
    }
    [Test] public void UltimaVidaTerminaSemValorNegativo()
    {
        var p = new Partida(); p.Iniciar(2);
        for (int i = 0; i < 3; i++) { p.Lancar(); p.PerderBola(); }
        Assert.IsFalse(p.PerderBola()); Assert.IsFalse(p.Lancar());
        Assert.AreEqual(0, p.Vidas); Assert.AreEqual(EstadoPartida.Derrota, p.Estado);
    }
    [Test] public void PausaPreservaEsperaAntesDoLancamento()
    {
        var p = new Partida(); p.Iniciar(1); p.AlternarPausa();
        Assert.IsFalse(p.Lancar()); Assert.IsFalse(p.PerderBola());
        p.AlternarPausa(); Assert.AreEqual(EstadoPartida.Preparando, p.Estado);
    }
    [Test] public void TresFasesEncerramEmVitoria()
    {
        var p = new Partida(); p.Iniciar(1);
        for (int i = 0; i < 3; i++)
        {
            Assert.IsTrue(p.Lancar()); Assert.IsTrue(p.DestruirBloco(100));
            p.Avancar(3, i < 2 ? 1 : 0);
        }
        Assert.AreEqual(EstadoPartida.Vitoria, p.Estado);
        Assert.AreEqual(300, p.Pontos); Assert.AreEqual(2, p.Fase);
        Assert.IsFalse(p.DestruirBloco(100));
    }
    [Test] public void ReiniciarRestauraTodosOsDadosDaPartida()
    {
        var p = new Partida(); p.Iniciar(2); p.Lancar(); p.DestruirBloco(150); p.PerderBola(); p.AlternarPausa();
        p.Iniciar(7);
        Assert.AreEqual(3, p.Vidas); Assert.AreEqual(0, p.Pontos);
        Assert.AreEqual(0, p.Fase); Assert.AreEqual(7, p.BlocosRestantes);
        Assert.AreEqual(EstadoPartida.Preparando, p.Estado);
    }
    [Test] public void NaoAvancaComBlocosRestantes()
    {
        var p = new Partida(); p.Iniciar(3); p.Lancar(); p.DestruirBloco(100); p.Avancar(3, 9);
        Assert.AreEqual(0, p.Fase); Assert.AreEqual(2, p.BlocosRestantes);
    }
    [Test] public void MenuNaoRecebePontosNemPerdeVidas()
    {
        var p = new Partida(); Assert.IsFalse(p.DestruirBloco(100)); Assert.IsFalse(p.PerderBola());
    }
    [Test] public void ConfiguracaoVaziaFalhaComMensagemDeOrigem()
    {
        Assert.Throws<System.ArgumentOutOfRangeException>(() => new Partida().Iniciar(0));
    }
}
