using NUnit.Framework;
using TecnologiaNaPratica;

public class ArenaTests
{
    [Test]
    public void InicioRestauraTudo()
    {
        var r = new ProgressoArena();
        r.Iniciar();
        r.Abater();
        r.ConcluirOnda(5);
        r.Melhorar(0);
        r.Iniciar();
        Assert.AreEqual(0, r.Potencia);
        Assert.AreEqual(0, r.Abates);
        Assert.AreEqual(0, r.Onda);
    }

    [Test]
    public void MelhoriaSoEntreOndas()
    {
        var r = new ProgressoArena();
        r.Iniciar();
        Assert.IsFalse(r.Melhorar(0));
        Assert.AreEqual(0, r.Onda);
    }

    [Test]
    public void CliqueDuploNaoAvancaDuasOndas()
    {
        var r = new ProgressoArena();
        r.Iniciar();
        r.ConcluirOnda(5);
        Assert.IsTrue(r.Melhorar(1));
        Assert.IsFalse(r.Melhorar(1));
        Assert.AreEqual(1, r.Onda);
    }

    [Test]
    public void QuintaOndaEncerra()
    {
        var r = new ProgressoArena();
        r.Iniciar();
        for (int i = 0; i < 4; i++)
        {
            r.ConcluirOnda(5);
            r.Melhorar(i % 3);
        }

        r.ConcluirOnda(5);
        Assert.AreEqual(EstadoArena.Vitoria, r.Estado);
        Assert.IsFalse(r.Melhorar(0));
    }

    [Test]
    public void PausaBloqueiaAbates()
    {
        var r = new ProgressoArena();
        r.Iniciar();
        r.Pausar();
        r.Abater();
        Assert.AreEqual(0, r.Abates);
        r.Retomar();
        r.Abater();
        Assert.AreEqual(1, r.Abates);
    }

    [Test]
    public void DerrotaNaoSeTransformaEmVitoria()
    {
        var r = new ProgressoArena();
        r.Iniciar();
        r.Perder();
        r.ConcluirOnda(1);
        Assert.AreEqual(EstadoArena.Derrota, r.Estado);
    }

    [Test]
    public void OpcoesInvalidasNaoAlteramEstado()
    {
        var r = new ProgressoArena();
        r.Iniciar();
        r.ConcluirOnda(5);
        Assert.IsFalse(r.Melhorar(9));
        Assert.AreEqual(EstadoArena.Melhoria, r.Estado);
    }

    [Test]
    public void PotenciaTemLimite()
    {
        var r = new ProgressoArena();
        r.Iniciar();
        for (int i = 0; i < 3; i++)
        {
            r.ConcluirOnda(5);
            Assert.IsTrue(r.Melhorar(0));
        }

        r.ConcluirOnda(5);
        Assert.IsFalse(r.Melhorar(0));
        Assert.AreEqual(3, r.Potencia);
    }
}
