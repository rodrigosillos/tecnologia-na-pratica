using System;
using System.Collections;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;

namespace TecnologiaNaPratica
{
    public sealed class ProvaArena : ProvaExecutavelBase
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Ativar()
        {
            var a = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(a, "--tnp-verificar");
            if (i >= 0 && i + 1 < a.Length)
                new GameObject("Prova executavel").AddComponent<ProvaArena>().Configurar(a[i + 1]);
        }

        protected override IEnumerator Roteiro()
        {
            yield return null;
            var a = FindFirstObjectByType<Arena>();
            Conferir(a && a.Regras.Estado == EstadoArena.Menu, "Menu inicial carregado");
            Capturar("menu.png");
            a.Iniciar();
            yield return null;
            Teclas(Key.D, Key.W);
            var inicio = a.Jogador.Corpo.position;
            yield return new WaitForSeconds(.35f);
            Teclas();
            yield return null;
            float distancia = Vector2.Distance(inicio, a.Jogador.Corpo.position);
            Conferir(distancia > 1.4f && distancia < 2.1f, "Movimento diagonal normalizado por entrada real");
            a.Jogador.Corpo.position = Vector2.zero;
            yield return null;
            var ponto = Camera.main.WorldToScreenPoint(new Vector3(6, 0));
            InputSystem.QueueStateEvent(mouse, new MouseState { position = ponto, buttons = 1 });
            yield return new WaitForSeconds(.5f);
            InputSystem.QueueStateEvent(mouse, new MouseState { position = ponto });
            yield return null;
            Conferir(a.Projeteis.Ativos > 0, "Mouse dispara projéteis pela ação de entrada");
            yield return new WaitForSeconds(1.1f);
            Capturar("combate.png");
            Teclas(Key.Escape);
            yield return null;
            yield return null;
            Teclas();
            yield return null;
            Conferir(a.Regras.Estado == EstadoArena.Pausa && Time.timeScale == 0, "Escape pausa a arena");
            int emitidos = a.Emitidos;
            var pos = a.Jogador.Corpo.position;
            yield return new WaitForSecondsRealtime(.2f);
            Conferir(a.Emitidos == emitidos && a.Jogador.Corpo.position == pos, "Pausa congela movimento e geração de inimigos");
            Capturar("pausa.png");
            a.AlternarPausa();
            yield return null;
            a.Jogador.Saude.Restaurar(5);
            bool um = a.Jogador.Saude.ReceberDano(1, Vector2.left);
            bool dois = a.Jogador.Saude.ReceberDano(1, Vector2.left);
            Conferir(um && !dois && a.Jogador.Saude.Atual == 4, "Invulnerabilidade bloqueia dano duplicado");
            a.Jogador.Saude.Restaurar(1);
            a.Jogador.Saude.ReceberDano(1, Vector2.zero);
            yield return null;
            Conferir(a.Regras.Estado == EstadoArena.Derrota, "Vida zero encerra em derrota");
            Capturar("derrota.png");
            a.Iniciar();
            a.Jogador.Saude.Restaurar(500);
            yield return null;
            for (int onda = 0; onda < 5; onda++)
            {
                Time.timeScale = 4;
                while (a.Jogando)
                {
                    foreach (var e in a.Inimigos)
                        if (e.gameObject.activeSelf)
                            e.Saude.ReceberDano(100, e.transform.position);
                    yield return new WaitForSecondsRealtime(.05f);
                }

                if (onda < 4)
                {
                    Conferir(a.Regras.Estado == EstadoArena.Melhoria, "Onda " + (onda + 1) + " abre melhoria uma vez");
                    if (onda == 1)
                        Capturar("melhoria.png");
                    a.Melhorar(onda % 3);
                    a.Jogador.Saude.Restaurar(500);
                }
            }

            Conferir(a.Regras.Estado == EstadoArena.Vitoria && a.Regras.Abates == 48, "Cinco ondas, 48 abates e vitória por dano controlado");
            Capturar("vitoria.png");
            a.Iniciar();
            yield return null;
            Conferir(a.Regras.Onda == 0 && a.Regras.Abates == 0 && a.Jogador.Saude.Atual == 5, "Reinício restaura progressão e saúde");
            int criados = a.Projeteis.Criados;
            for (int i = 0; i < 25; i++)
            {
                a.Projeteis.Disparar(Vector2.zero, Vector2.right, 1, false);
                a.Projeteis.Limpar();
            }

            Conferir(a.Projeteis.Criados == criados && a.Projeteis.Ativos == 0, "Reserva reutiliza projéteis sem criação adicional no ciclo");
            a.Menu();
        }
    }
}
