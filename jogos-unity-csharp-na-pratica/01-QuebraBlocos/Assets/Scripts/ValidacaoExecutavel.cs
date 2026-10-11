using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;

namespace TecnologiaNaPratica.QuebraBlocos
{
    // Executado somente com --tnp-verificar <pasta>. Não participa da partida normal.
    public sealed class ValidacaoExecutavel : MonoBehaviour
    {
        [Serializable]
        sealed class Resultado
        {
            public string unity, plataforma, erro;
            public bool aprovado;
            public string[] verificacoes;
        }
        readonly List<string> verificacoes = new List<string>();
        string pasta;
        Keyboard teclado;
        ControlePartida controle;
        InputSettings original, temporaria;
        bool tinhaRecorde, tinhaVolume, terminou;
        int recorde;
        float volume, inicio;
        const string Recorde = "TNP.QuebraBlocos.Recorde.v1";
        const string Volume = "TNP.QuebraBlocos.Volume.v1";

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Ativar()
        {
            string[] args = Environment.GetCommandLineArgs();
            int indice = Array.IndexOf(args, "--tnp-verificar");
            if (indice < 0 || indice + 1 >= args.Length) return;
            var teste = new GameObject("Validacao do executavel").AddComponent<ValidacaoExecutavel>();
            teste.pasta = Path.GetFullPath(args[indice + 1]);
        }
        IEnumerator Start()
        {
            inicio = Time.realtimeSinceStartup;
            Application.runInBackground = true;
            tinhaRecorde = PlayerPrefs.HasKey(Recorde); recorde = PlayerPrefs.GetInt(Recorde);
            tinhaVolume = PlayerPrefs.HasKey(Volume); volume = PlayerPrefs.GetFloat(Volume);
            original = InputSystem.settings;
            temporaria = Instantiate(original); InputSystem.settings = temporaria;
            temporaria.backgroundBehavior = InputSettings.BackgroundBehavior.IgnoreFocus;
            teclado = InputSystem.AddDevice<Keyboard>();
            Directory.CreateDirectory(pasta);
            var roteiro = Roteiro();
            while (true)
            {
                object espera;
                try
                {
                    if (!roteiro.MoveNext()) break;
                    espera = roteiro.Current;
                }
                catch (Exception e) { Finalizar(e.ToString()); yield break; }
                yield return espera;
            }
            Finalizar(null);
        }
        void Update()
        {
            if (!terminou && Time.realtimeSinceStartup - inicio > 45)
                Finalizar("Tempo limite excedido no roteiro do executável.");
        }
        IEnumerator Roteiro()
        {
            yield return null;
            controle = FindFirstObjectByType<ControlePartida>();
            var bola = FindFirstObjectByType<Bola>();
            var raquete = FindFirstObjectByType<Raquete>();
            Conferir(controle != null && bola != null && raquete != null, "Cena inicial e componentes presentes");
            Conferir(controle.Regras.Estado == EstadoPartida.Menu, "Menu inicial");
            yield return new WaitForSecondsRealtime(.2f);
            Capturar("menu.png");
            controle.Iniciar(); yield return null;
            Conferir(controle.Regras.BlocosRestantes == 22, "Primeira formação com 22 pedras");
            Capturar("campo.png");
            InputSystem.QueueStateEvent(teclado, new KeyboardState(Key.RightArrow));
            yield return new WaitForSeconds(.8f);
            Conferir(Mathf.Abs(raquete.GetComponent<Rigidbody2D>().position.x - 6.3f) < .03f, "Teclado e limite da raquete");
            InputSystem.QueueStateEvent(teclado, new KeyboardState(Key.Space));
            yield return null; yield return null;
            Conferir(controle.Regras.Estado == EstadoPartida.Jogando && bola.Corpo.simulated, "Lançamento pela ação de entrada");
            InputSystem.QueueStateEvent(teclado, new KeyboardState());
            yield return new WaitForSeconds(.2f);
            Capturar("jogando.png");
            bola.Corpo.position = new Vector2(-4.25f, 0);
            bola.Corpo.linearVelocity = Vector2.up * 7;
            float limite = Time.time + 1;
            while (controle.Regras.Pontos == 0 && Time.time < limite) yield return new WaitForFixedUpdate();
            Conferir(controle.Regras.Pontos > 0, "Colisão física pontua no executável");
            // O teletransporte acima pertence ao teste físico, não a uma jogada.
            bola.GetComponent<TrailRenderer>().Clear();
            // Entrada de pausa é processada no quadro, após os passos físicos pendentes.
            yield return null;
            controle.Pausar(); var posicao = bola.Corpo.position;
            yield return new WaitForSecondsRealtime(.1f);
            if (bola.Corpo.position != posicao || Time.timeScale != 0)
                throw new InvalidOperationException($"Pausa: antes={posicao}, depois={bola.Corpo.position}, escala={Time.timeScale}, estado={controle.Regras.Estado}");
            Conferir(true, "Pausa conserva posição");
            Capturar("pausa.png"); controle.Pausar();
            controle.Iniciar(); yield return null;
            for (int i = 0; i < 3; i++)
            {
                controle.Regras.Lancar(); bola.Lancar();
                bola.Corpo.position = new Vector2(0, -5.8f);
                yield return new WaitForFixedUpdate(); yield return null;
            }
            Conferir(controle.Regras.Estado == EstadoPartida.Derrota && controle.Regras.Vidas == 0, "Três quedas encerram em derrota");
            Capturar("derrota.png");
            controle.Iniciar(); yield return null;
            for (int fase = 0; fase < 3; fase++)
            {
                controle.Regras.Lancar();
                var blocos = FindObjectsByType<Bloco>(FindObjectsSortMode.None);
                foreach (var bloco in blocos) bloco.ReceberImpacto();
                yield return new WaitForFixedUpdate();
                foreach (var bloco in blocos) if (bloco != null) bloco.ReceberImpacto();
                yield return null; yield return null;
            }
            Conferir(controle.Regras.Estado == EstadoPartida.Vitoria && controle.Regras.Pontos == 8400, "Transições das três fases e pontuação total 8400");
            Capturar("vitoria.png");
            controle.Iniciar(); yield return null;
            Conferir(controle.Regras.Vidas == 3 && controle.Regras.Pontos == 0 && controle.Regras.Fase == 0, "Reinício após vitória");
            controle.Som.DefinirVolume(0);
            Conferir(controle.Som.GetComponent<AudioSource>().volume == 0, "Volume zero no AudioSource");
            controle.VoltarAoMenu();
        }
        void Conferir(bool condicao, string descricao)
        {
            if (!condicao) throw new InvalidOperationException(descricao);
            verificacoes.Add(descricao);
        }
        void Capturar(string nome)
        {
            if (SystemInfo.graphicsDeviceType == UnityEngine.Rendering.GraphicsDeviceType.Null) return;
            var cam = Camera.main; var canvas = FindFirstObjectByType<Canvas>();
            var modo = canvas.renderMode; var cameraAnterior = canvas.worldCamera;
            int ordem = canvas.sortingOrder;
            canvas.renderMode = RenderMode.ScreenSpaceCamera;
            canvas.worldCamera = cam; canvas.planeDistance = 1; canvas.sortingOrder = 100;
            var rt = new RenderTexture(1280, 720, 24); rt.Create();
            cam.targetTexture = rt; Canvas.ForceUpdateCanvases(); cam.Render();
            var ativo = RenderTexture.active; RenderTexture.active = rt;
            var tex = new Texture2D(1280, 720, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0); tex.Apply();
            File.WriteAllBytes(Path.Combine(pasta, nome), tex.EncodeToPNG());
            RenderTexture.active = ativo; cam.targetTexture = null;
            Destroy(tex); rt.Release(); Destroy(rt);
            canvas.renderMode = modo; canvas.worldCamera = cameraAnterior; canvas.sortingOrder = ordem;
        }
        void Finalizar(string erro)
        {
            if (terminou) return;
            terminou = true; Time.timeScale = 1;
            if (teclado != null && teclado.added) InputSystem.RemoveDevice(teclado);
            if (original != null) InputSystem.settings = original;
            if (temporaria != null) Destroy(temporaria);
            if (tinhaRecorde) PlayerPrefs.SetInt(Recorde, recorde); else PlayerPrefs.DeleteKey(Recorde);
            if (tinhaVolume) PlayerPrefs.SetFloat(Volume, volume); else PlayerPrefs.DeleteKey(Volume);
            PlayerPrefs.Save();
            var resultado = new Resultado { unity = Application.unityVersion,
                plataforma = Application.platform.ToString(), aprovado = erro == null,
                erro = erro, verificacoes = verificacoes.ToArray() };
            File.WriteAllText(Path.Combine(pasta, "resultado.json"), JsonUtility.ToJson(resultado, true));
            Debug.Log("TNP_EXECUTAVEL: " + (erro == null ? "APROVADO" : erro));
            Application.Quit(erro == null ? 0 : 1);
        }
    }
}
