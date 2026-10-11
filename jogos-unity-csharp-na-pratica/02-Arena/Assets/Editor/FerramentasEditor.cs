using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.U2D.Sprites;
using UnityEditor.SceneManagement;
using UnityEngine;
using TecnologiaNaPratica;

public static class FerramentasEditor
{
    public static BancoArte Preparar(string titulo, float gravidade)
    {
        foreach (string pasta in new[]
        {
            "Assets/Scenes",
            "Assets/Prefabs",
            "Assets/Dados",
            "Assets/Resources"
        }

        )
            Directory.CreateDirectory(pasta);
        AssetDatabase.Refresh();
        ImportarAtores();
        var banco = ScriptableObject.CreateInstance<BancoArte>();
        string[] nomes =
        {
            "Piso",
            "Muralha",
            "Pedra",
            "PedraReforcada",
            "PedraDanificada",
            "Raquete",
            "Esfera",
            "Vegetacao",
            "Portal"
        };
        var ambiente = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/RuinasAtlas.png").OfType<Sprite>().ToArray();
        banco.ambiente = nomes.Select(n => ambiente.First(s => s.name == n)).ToArray();
        var atores = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/AtoresAtlas.png").OfType<Sprite>().ToArray();
        banco.atores = Enumerable.Range(0, 16).Select(i => atores.First(s => s.name == "Ator" + i.ToString("00"))).ToArray();
        banco = Salvar(banco, "Assets/Resources/BancoArte.asset");
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        PlayerSettings.companyName = "Rodrigo Sillos";
        PlayerSettings.productName = titulo;
        PlayerSettings.defaultScreenWidth = 1280;
        PlayerSettings.defaultScreenHeight = 720;
        PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
        PlayerSettings.runInBackground = false;
        PlayerSettings.colorSpace = ColorSpace.Gamma;
        var ps = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
        ps.FindProperty("activeInputHandler").intValue = 1;
        ps.ApplyModifiedPropertiesWithoutUndo();
        var tags = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
        string[] layers =
        {
            "Jogador",
            "Inimigo",
            "Solo"
        };
        for (int i = 0; i < 3; i++)
            tags.FindProperty("layers").GetArrayElementAtIndex(i + 8).stringValue = layers[i];
        tags.ApplyModifiedPropertiesWithoutUndo();
        Physics2D.gravity = new Vector2(0, gravidade);
        Time.fixedDeltaTime = .02f;
        var camera = new GameObject("Main Camera", typeof(Camera), typeof(AudioListener));
        camera.tag = "MainCamera";
        camera.transform.position = new Vector3(0, 0, -10);
        var c = camera.GetComponent<Camera>();
        c.orthographic = true;
        c.orthographicSize = 6;
        c.clearFlags = CameraClearFlags.SolidColor;
        c.backgroundColor = new Color(.035f, .085f, .12f);
        return banco;
    }

    static void ImportarAtores()
    {
        const string path = "Assets/Art/AtoresAtlas.png";
        var imp = (TextureImporter)AssetImporter.GetAtPath(path);
        imp.textureType = TextureImporterType.Sprite;
        imp.spriteImportMode = SpriteImportMode.Multiple;
        imp.isReadable = true;
        imp.alphaIsTransparency = true;
        imp.maxTextureSize = 2048;
        imp.mipmapEnabled = false;
        imp.textureCompression = TextureImporterCompression.Uncompressed;
        imp.SaveAndReimport();
        var tex = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        var pixels = tex.GetPixels32();
        var f = new SpriteDataProviderFactories();
        f.Init();
        var provider = f.GetSpriteEditorDataProviderFromObject(imp);
        provider.InitSpriteEditorDataProvider();
        var anteriores = provider.GetSpriteRects().ToDictionary(r => r.name, r => r.spriteID);
        var rects = new SpriteRect[16];
        // Faixas conferidas na arte original; a primeira linha não termina exatamente em 25%.
        float[] faixas =
        {
            0,
            370 / 1280f,
            690 / 1280f,
            944 / 1280f,
            1
        };
        for (int i = 0; i < 16; i++)
        {
            int row = i / 4, col = i % 4;
            int x0 = col * tex.width / 4, x1 = (col + 1) * tex.width / 4;
            if (row == 3 && col == 0)
                x1 = Mathf.RoundToInt(tex.width * 353 / 1280f);
            if (row == 3 && col == 1)
                x0 = Mathf.RoundToInt(tex.width * 354 / 1280f);
            int y0 = Mathf.RoundToInt((1 - faixas[row + 1]) * tex.height), y1 = Mathf.RoundToInt((1 - faixas[row]) * tex.height);
            int minX = x1, minY = y1, maxX = x0, maxY = y0;
            for (int y = y0; y < y1; y++)
                for (int x = x0; x < x1; x++)
                    if (pixels[y * tex.width + x].a > 32)
                    {
                        minX = Math.Min(minX, x);
                        minY = Math.Min(minY, y);
                        maxX = Math.Max(maxX, x);
                        maxY = Math.Max(maxY, y);
                    }

            string nome = "Ator" + i.ToString("00");
            rects[i] = new SpriteRect
            {
                name = nome,
                rect = new Rect(minX, minY, maxX - minX + 1, maxY - minY + 1),
                alignment = SpriteAlignment.Center,
                pivot = new Vector2(.5f, .5f),
                spriteID = anteriores.TryGetValue(nome, out var id) ? id : GUID.Generate()
            };
        }

        provider.SetSpriteRects(rects);
        provider.GetDataProvider<ISpriteNameFileIdDataProvider>().SetNameFileIdPairs(rects.Select(r => new SpriteNameFileIdPair(r.name, r.spriteID)));
        provider.Apply();
        imp.SaveAndReimport();
    }

    public static T Salvar<T>(T obj, string path)
        where T : UnityEngine.Object
    {
        var anterior = AssetDatabase.LoadAssetAtPath<T>(path);
        if (anterior)
        {
            EditorUtility.CopySerialized(obj, anterior);
            UnityEngine.Object.DestroyImmediate(obj);
            EditorUtility.SetDirty(anterior);
            return anterior;
        }

        AssetDatabase.CreateAsset(obj, path);
        return obj;
    }

    public static GameObject Corpo(string nome, Vector2 pos, int layer, RigidbodyType2D tipo)
    {
        var go = new GameObject(nome);
        go.transform.position = pos;
        go.layer = layer;
        var rb = go.AddComponent<Rigidbody2D>();
        rb.bodyType = tipo;
        rb.freezeRotation = true;
        rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
        rb.interpolation = RigidbodyInterpolation2D.Interpolate;
        return go;
    }

    public static void Cena(string nome)
    {
        string path = "Assets/Scenes/" + nome + ".unity";
        EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), path);
        EditorBuildSettings.scenes = new[]
        {
            new EditorBuildSettingsScene(path, true)
        };
        AssetDatabase.SaveAssets();
    }

    public static void Compilar(string nome)
    {
        Directory.CreateDirectory("Build/Windows");
        var resultado = BuildPipeline.BuildPlayer(EditorBuildSettings.scenes.Where(s => s.enabled).Select(s => s.path).ToArray(), "Build/Windows/" + nome + ".exe", BuildTarget.StandaloneWindows64, BuildOptions.None);
        if (resultado.summary.result != UnityEditor.Build.Reporting.BuildResult.Succeeded)
            throw new Exception("Build falhou: " + resultado.summary.result);
    }
}
