using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
using TecnologiaNaPratica.QuebraBlocos;

public sealed class CenaTests
{
    Keyboard teclado;
    InputSettings configuracaoOriginal, configuracaoTeste;
    [SetUp]
    public void PrepararEntradaEmSegundoPlano()
    {
        configuracaoOriginal = InputSystem.settings;
        configuracaoTeste = Object.Instantiate(configuracaoOriginal);
        InputSystem.settings = configuracaoTeste;
        configuracaoTeste.backgroundBehavior = InputSettings.BackgroundBehavior.IgnoreFocus;
#if UNITY_EDITOR
        configuracaoTeste.editorInputBehaviorInPlayMode = InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
#endif
    }
    [TearDown]
    public void Limpar()
    {
        Time.timeScale = 1f;
        if (teclado != null && teclado.added) InputSystem.RemoveDevice(teclado);
        teclado = null;
        InputSystem.settings = configuracaoOriginal;
        Object.DestroyImmediate(configuracaoTeste);
    }
    [UnityTest]
    public IEnumerator LancamentoPerdaEPausaUsamOsComponentesReais()
    {
        SceneManager.LoadScene("QuebraBlocos");
        yield return null;
        var controle = Object.FindFirstObjectByType<ControlePartida>();
        var bola = Object.FindFirstObjectByType<Bola>();
        Assert.IsNotNull(controle); Assert.IsNotNull(bola);
        controle.Iniciar();
        yield return null;
        Assert.AreEqual(22, controle.Regras.BlocosRestantes);
        Assert.AreEqual(22, Object.FindObjectsByType<Bloco>(FindObjectsSortMode.None).Length);
        Assert.IsTrue(controle.Regras.Lancar()); bola.Lancar();
        yield return new WaitForFixedUpdate();
        Assert.Greater(bola.Corpo.linearVelocity.y, 0);
        controle.Pausar();
        Vector2 antes = bola.Corpo.position;
        yield return new WaitForSecondsRealtime(.1f);
        Assert.AreEqual(antes, bola.Corpo.position);
        controle.Pausar();
        bola.Corpo.position = new Vector2(0, -5.8f);
        yield return new WaitForFixedUpdate();
        yield return null;
        Assert.AreEqual(2, controle.Regras.Vidas);
        Assert.AreEqual(EstadoPartida.Preparando, controle.Regras.Estado);
        controle.PerderBola(); Assert.AreEqual(2, controle.Regras.Vidas);
        controle.VoltarAoMenu(); Assert.AreEqual(1f, Time.timeScale);
    }

    [UnityTest]
    public IEnumerator BlocoComumEReinicioNaoDuplicamPontos()
    {
        SceneManager.LoadScene("QuebraBlocos"); yield return null;
        var c = Object.FindFirstObjectByType<ControlePartida>();
        c.Iniciar(); yield return null; c.Regras.Lancar();
        var bloco = Object.FindFirstObjectByType<Bloco>();
        bloco.ReceberImpacto(); bloco.ReceberImpacto();
        Assert.AreEqual(100, c.Regras.Pontos);
        yield return null;
        c.Pausar(); c.Iniciar(); yield return null;
        Assert.AreEqual(0, c.Regras.Pontos); Assert.AreEqual(3, c.Regras.Vidas);
        Assert.AreEqual(22, Object.FindObjectsByType<Bloco>(FindObjectsSortMode.None).Length);
        Assert.AreEqual(1f, Time.timeScale);
    }

    [UnityTest]
    public IEnumerator ColisaoFisicaRealDestroiUmBloco()
    {
        SceneManager.LoadScene("QuebraBlocos"); yield return null;
        var c = Object.FindFirstObjectByType<ControlePartida>();
        var bola = Object.FindFirstObjectByType<Bola>();
        c.Iniciar(); yield return null; c.Regras.Lancar(); bola.Lancar();
        // Na primeira fase, a coluna 1 da última linha contém uma pedra.
        bola.Corpo.position = new Vector2(-4.25f, .0f);
        bola.Corpo.linearVelocity = Vector2.up * 7;
        float limite = Time.time + 1;
        while (c.Regras.Pontos == 0 && Time.time < limite) yield return new WaitForFixedUpdate();
        Assert.Greater(c.Regras.Pontos, 0, "A esfera precisa colidir com o collider e pontuar.");
        c.VoltarAoMenu();
    }

    [UnityTest]
    public IEnumerator PedraReforcadaExigeDoisPassosEConcede150Pontos()
    {
        SceneManager.LoadScene("QuebraBlocos"); yield return null;
        var c = Object.FindFirstObjectByType<ControlePartida>();
        c.Iniciar(); yield return null; c.Regras.Lancar();
        var bloco = Object.FindFirstObjectByType<Bloco>();
        bloco.Configurar(c, 2);
        var imagemInicial = bloco.GetComponent<SpriteRenderer>().sprite;
        bloco.ReceberImpacto(); bloco.ReceberImpacto();
        Assert.AreEqual(0, c.Regras.Pontos);
        Assert.AreEqual(22, c.Regras.BlocosRestantes);
        Assert.AreNotEqual(imagemInicial, bloco.GetComponent<SpriteRenderer>().sprite);
        yield return new WaitForFixedUpdate();
        bloco.ReceberImpacto(); bloco.ReceberImpacto();
        Assert.AreEqual(150, c.Regras.Pontos);
        Assert.AreEqual(21, c.Regras.BlocosRestantes);
        c.VoltarAoMenu();
    }

    [UnityTest]
    public IEnumerator TecladoMoveLimitaELancaPelasAcoesReais()
    {
        SceneManager.LoadScene("QuebraBlocos"); yield return null;
        teclado = InputSystem.AddDevice<Keyboard>();
        var c = Object.FindFirstObjectByType<ControlePartida>();
        var r = Object.FindFirstObjectByType<Raquete>();
        var bola = Object.FindFirstObjectByType<Bola>();
        c.Iniciar(); yield return null;
        InputSystem.QueueStateEvent(teclado, new KeyboardState(Key.RightArrow));
        yield return null; yield return null;
        Assert.AreEqual(1f, Object.FindFirstObjectByType<EntradaJogador>().Direcao, "A ação deve receber o dispositivo virtual mesmo no teste sem janela.");
        yield return new WaitForSeconds(.8f);
        Assert.AreEqual(r.LimiteCentro, r.GetComponent<Rigidbody2D>().position.x, .03f);
        InputSystem.QueueStateEvent(teclado, new KeyboardState(Key.Space));
        yield return null; yield return null;
        Assert.AreEqual(EstadoPartida.Jogando, c.Regras.Estado);
        Assert.IsTrue(bola.Corpo.simulated);
        Assert.Greater(bola.Corpo.linearVelocity.sqrMagnitude, 1);
        InputSystem.QueueStateEvent(teclado, new KeyboardState());
        yield return null;
        InputSystem.QueueStateEvent(teclado, new KeyboardState(Key.Escape));
        yield return null; yield return null;
        Assert.AreEqual(EstadoPartida.Pausado, c.Regras.Estado);
        Assert.AreEqual(0f, Time.timeScale);
        c.VoltarAoMenu();
    }

    [UnityTest]
    public IEnumerator TresFormacoesDaCenaChegamAVitoriaEReiniciam()
    {
        SceneManager.LoadScene("QuebraBlocos"); yield return null;
        var c = Object.FindFirstObjectByType<ControlePartida>();
        c.Iniciar(); yield return null;
        for (int fase = 0; fase < 3; fase++)
        {
            Assert.AreEqual(fase, c.Regras.Fase);
            Assert.AreEqual(EstadoPartida.Preparando, c.Regras.Estado);
            c.Regras.Lancar();
            var blocos = Object.FindObjectsByType<Bloco>(FindObjectsSortMode.None);
            Assert.AreEqual(c.Regras.BlocosRestantes, blocos.Length);
            foreach (var bloco in blocos) bloco.ReceberImpacto();
            yield return new WaitForFixedUpdate();
            foreach (var bloco in blocos) if (bloco != null) bloco.ReceberImpacto();
            yield return null; yield return null;
        }
        Assert.AreEqual(EstadoPartida.Vitoria, c.Regras.Estado);
        Assert.Greater(c.Regras.Pontos, 0);
        c.Iniciar(); yield return null;
        Assert.AreEqual(0, c.Regras.Fase); Assert.AreEqual(0, c.Regras.Pontos);
        Assert.AreEqual(22, Object.FindObjectsByType<Bloco>(FindObjectsSortMode.None).Length);
        c.VoltarAoMenu();
    }
}
