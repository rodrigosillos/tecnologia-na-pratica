using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;

namespace TecnologiaNaPratica
{
    public sealed class PainelJogo : MonoBehaviour
    {
        public Text Placar { get; private set; }
        public Text Dica { get; private set; }
        public Canvas Tela { get; private set; }

        RectTransform painel;
        Text titulo, resumo;
        readonly List<GameObject> botoes = new List<GameObject>();
        Font fonte;
        public bool Aberto => painel.gameObject.activeSelf;

        public void Preparar()
        {
            fonte = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            var c = new GameObject("Interface", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            c.transform.SetParent(transform);
            Tela = c.GetComponent<Canvas>();
            Tela.renderMode = RenderMode.ScreenSpaceOverlay;
            var s = c.GetComponent<CanvasScaler>();
            s.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            s.referenceResolution = new Vector2(1280, 720);
            s.matchWidthOrHeight = .5f;
            var e = new GameObject("EventSystem", typeof(EventSystem), typeof(InputSystemUIInputModule));
            e.transform.SetParent(transform);
            e.GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
            var faixa = Retangulo("Faixa", c.transform, new Vector2(0, 320), new Vector2(1280, 72));
            faixa.gameObject.AddComponent<Image>().color = new Color(.025f, .08f, .12f, .92f);
            Placar = Texto(c.transform, "", new Vector2(0, 319), new Vector2(1220, 50), 22);
            var rodape = Retangulo("Faixa inferior", c.transform, new Vector2(0, -330), new Vector2(1280, 60));
            rodape.gameObject.AddComponent<Image>().color = new Color(.025f, .08f, .12f, .92f);
            Dica = Texto(c.transform, "", new Vector2(0, -330), new Vector2(1240, 42), 19);
            painel = Retangulo("Menu", c.transform, Vector2.zero, new Vector2(760, 590));
            painel.gameObject.AddComponent<Image>().color = new Color(.025f, .085f, .14f, .97f);
            titulo = Texto(painel, "", new Vector2(0, 225), new Vector2(700, 60), 34);
            resumo = Texto(painel, "", new Vector2(0, 130), new Vector2(685, 115), 20);
        }

        public void Mostrar(string cabecalho, string texto, params (string, Action)[] acoes)
        {
            foreach (var b in botoes)
            {
                b.SetActive(false);
                Destroy(b);
            }

            botoes.Clear();
            painel.gameObject.SetActive(true);
            titulo.text = cabecalho;
            resumo.text = texto;
            for (int i = 0; i < acoes.Length; i++)
            {
                var rt = Retangulo("Acao", painel, new Vector2(0, 40 - i * 48), new Vector2(610, 40));
                rt.gameObject.AddComponent<Image>().color = new Color(.12f, .31f, .40f);
                var btn = rt.gameObject.AddComponent<Button>();
                var cb = btn.colors;
                cb.highlightedColor = new Color(1, .75f, .35f);
                cb.selectedColor = cb.highlightedColor;
                btn.colors = cb;
                var acao = acoes[i].Item2;
                btn.onClick.AddListener(() => acao());
                Texto(rt, acoes[i].Item1, Vector2.zero, new Vector2(590, 38), 19);
                botoes.Add(rt.gameObject);
            }

            if (botoes.Count > 0)
                EventSystem.current.SetSelectedGameObject(botoes[0]);
        }

        public void Fechar()
        {
            painel.gameObject.SetActive(false);
            EventSystem.current.SetSelectedGameObject(null);
        }

        public void Configurar(AudioRuinas audio, Action voltar, Action efeitosVisuais = null, Func<bool> reduzido = null)
        {
            Action abrir = null;
            abrir = () => Mostrar("CONFIGURAÇÕES", "As alterações de áudio são salvas neste computador.\nUse o mouse ou as setas e Enter.", ($"Efeitos: {Mathf.RoundToInt(audio.Efeitos * 100)}%  — alterar", () =>
            {
                audio.DefinirEfeitos(audio.Efeitos >= .99f ? 0 : audio.Efeitos + .25f);
                abrir();
            }), ($"Música: {Mathf.RoundToInt(audio.Musica * 100)}%  — alterar", () =>
            {
                audio.DefinirMusica(audio.Musica >= .99f ? 0 : audio.Musica + .25f);
                abrir();
            }), ("Tela: " + (Screen.fullScreen ? "cheia" : "janela"), () =>
            {
                Screen.fullScreen = !Screen.fullScreen;
                abrir();
            }), (efeitosVisuais == null ? "Resolução: 1280 × 720" : ("Efeitos reduzidos: " + (reduzido() ? "sim" : "não")), () =>
            {
                if (efeitosVisuais != null)
                    efeitosVisuais();
                else
                    Screen.SetResolution(1280, 720, Screen.fullScreen);
                abrir();
            }), ("VOLTAR", voltar));
            abrir();
        }

        RectTransform Retangulo(string nome, Transform pai, Vector2 pos, Vector2 tamanho)
        {
            var go = new GameObject(nome, typeof(RectTransform));
            var rt = go.GetComponent<RectTransform>();
            rt.SetParent(pai, false);
            rt.anchorMin = rt.anchorMax = new Vector2(.5f, .5f);
            rt.anchoredPosition = pos;
            rt.sizeDelta = tamanho;
            return rt;
        }

        Text Texto(Transform pai, string texto, Vector2 pos, Vector2 tamanho, int n)
        {
            var rt = Retangulo("Texto", pai, pos, tamanho);
            var t = rt.gameObject.AddComponent<Text>();
            t.font = fonte;
            t.text = texto;
            t.fontSize = n;
            t.alignment = TextAnchor.MiddleCenter;
            t.color = new Color(.93f, .96f, .97f);
            t.raycastTarget = false;
            return t;
        }
    }
}
