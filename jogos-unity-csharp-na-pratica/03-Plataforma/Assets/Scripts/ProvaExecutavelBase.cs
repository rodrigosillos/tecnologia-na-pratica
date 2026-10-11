using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;

namespace TecnologiaNaPratica
{
    public abstract class ProvaExecutavelBase : MonoBehaviour
    {
        [Serializable]
        class Resultado
        {
            public string unity, plataforma, erro;
            public bool aprovado;
            public string[] verificacoes;
        }

        protected string pasta;
        protected Keyboard teclado;
        protected Mouse mouse;
        InputSettings original, temporaria;
        readonly List<string> verificacoes = new List<string>();
        bool terminou;
        float inicio;
        protected abstract IEnumerator Roteiro();
        protected virtual void Preparar()
        {
        }

        public void Configurar(string path)
        {
            pasta = Path.GetFullPath(path);
            Directory.CreateDirectory(pasta);
            DontDestroyOnLoad(gameObject);
            Preparar();
        }

        IEnumerator Start()
        {
            inicio = Time.realtimeSinceStartup;
            Application.runInBackground = true;
            original = InputSystem.settings;
            temporaria = Instantiate(original);
            InputSystem.settings = temporaria;
            temporaria.backgroundBehavior = InputSettings.BackgroundBehavior.IgnoreFocus;
            teclado = InputSystem.AddDevice<Keyboard>();
            mouse = InputSystem.AddDevice<Mouse>();
            var r = Roteiro();
            while (true)
            {
                object espera;
                try
                {
                    if (!r.MoveNext())
                        break;
                    espera = r.Current;
                }
                catch (Exception e)
                {
                    Finalizar(e.ToString());
                    yield break;
                }

                yield return espera;
            }

            Finalizar(null);
        }

        void Update()
        {
            if (!terminou && Time.realtimeSinceStartup - inicio > 150)
                Finalizar("Tempo limite de 150 segundos.");
        }

        protected void Teclas(params Key[] keys)
        {
            InputSystem.QueueStateEvent(teclado, new KeyboardState(keys));
        }

        protected void Conferir(bool valor, string descricao)
        {
            if (!valor)
                throw new InvalidOperationException(descricao);
            verificacoes.Add(descricao);
        }

        protected void Capturar(string nome)
        {
            if (SystemInfo.graphicsDeviceType == UnityEngine.Rendering.GraphicsDeviceType.Null)
                return;
            var cam = Camera.main;
            var canvas = FindFirstObjectByType<Canvas>();
            var modo = canvas.renderMode;
            var anterior = canvas.worldCamera;
            canvas.renderMode = RenderMode.ScreenSpaceCamera;
            canvas.worldCamera = cam;
            canvas.planeDistance = 1;
            canvas.sortingOrder = 100;
            var rt = new RenderTexture(1280, 720, 24);
            rt.Create();
            cam.targetTexture = rt;
            Canvas.ForceUpdateCanvases();
            cam.Render();
            var ativo = RenderTexture.active;
            RenderTexture.active = rt;
            var tex = new Texture2D(1280, 720, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0);
            tex.Apply();
            File.WriteAllBytes(Path.Combine(pasta, nome), tex.EncodeToPNG());
            RenderTexture.active = ativo;
            cam.targetTexture = null;
            Destroy(tex);
            rt.Release();
            Destroy(rt);
            canvas.renderMode = modo;
            canvas.worldCamera = anterior;
            canvas.sortingOrder = 0;
        }

        void Finalizar(string erro)
        {
            if (terminou)
                return;
            terminou = true;
            Time.timeScale = 1;
            if (teclado != null && teclado.added)
                InputSystem.RemoveDevice(teclado);
            if (mouse != null && mouse.added)
                InputSystem.RemoveDevice(mouse);
            if (original != null)
                InputSystem.settings = original;
            if (temporaria != null)
                Destroy(temporaria);
            File.WriteAllText(Path.Combine(pasta, "resultado.json"), JsonUtility.ToJson(new Resultado { unity = Application.unityVersion, plataforma = Application.platform.ToString(), aprovado = erro == null, erro = erro, verificacoes = verificacoes.ToArray() }, true));
            Debug.Log("TNP_EXECUTAVEL: " + (erro == null ? "APROVADO" : erro));
            Application.Quit(erro == null ? 0 : 1);
        }
    }
}
