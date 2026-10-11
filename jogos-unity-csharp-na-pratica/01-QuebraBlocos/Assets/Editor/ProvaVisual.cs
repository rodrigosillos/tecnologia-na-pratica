using System;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using TecnologiaNaPratica.QuebraBlocos;

[InitializeOnLoad]
public static class ProvaVisual
{
    const string Chave = "TNP.ProvaVisual";
    static double inicio;
    static ProvaVisual()
    {
        if (SessionState.GetInt(Chave, 0) > 0)
        {
            inicio = EditorApplication.timeSinceStartup;
            EditorApplication.update += Passo;
        }
    }
    public static void Executar()
    {
        EditorSceneManager.OpenScene("Assets/Scenes/QuebraBlocos.unity");
        SessionState.SetInt(Chave, 1);
        EditorApplication.isPlaying = true;
    }
    static void Passo()
    {
        if (!EditorApplication.isPlaying || EditorApplication.isPlayingOrWillChangePlaymode != true) return;
        if (EditorApplication.timeSinceStartup - inicio < 2) return;
        int etapa = SessionState.GetInt(Chave, 0);
        try
        {
            if (etapa == 1)
            {
                Capturar("menu.png");
                UnityEngine.Object.FindFirstObjectByType<ControlePartida>().Iniciar();
                SessionState.SetInt(Chave, 2); inicio = EditorApplication.timeSinceStartup;
            }
            else if (etapa == 2)
            {
                Capturar("campo.png");
                SessionState.SetInt(Chave, 0);
                EditorApplication.update -= Passo;
                EditorApplication.Exit(0);
            }
        }
        catch (Exception e)
        {
            Debug.LogException(e); SessionState.SetInt(Chave, 0); EditorApplication.Exit(1);
        }
    }
    static void Capturar(string nome)
    {
        Directory.CreateDirectory("Provas");
        var cam = Camera.main;
        var canvas = UnityEngine.Object.FindFirstObjectByType<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceCamera; canvas.worldCamera = cam; canvas.planeDistance = 1;
        canvas.sortingOrder = 100;
        var rt = new RenderTexture(1280, 720, 24); rt.Create();
        cam.targetTexture = rt; Canvas.ForceUpdateCanvases(); cam.Render();
        var anterior = RenderTexture.active; RenderTexture.active = rt;
        var tex = new Texture2D(1280, 720, TextureFormat.RGB24, false);
        tex.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0); tex.Apply();
        File.WriteAllBytes("Provas/" + nome, tex.EncodeToPNG());
        RenderTexture.active = anterior; cam.targetTexture = null;
        UnityEngine.Object.DestroyImmediate(tex); rt.Release(); UnityEngine.Object.DestroyImmediate(rt);
        Debug.Log("TNP_PROVA_VISUAL: " + nome);
    }
}
