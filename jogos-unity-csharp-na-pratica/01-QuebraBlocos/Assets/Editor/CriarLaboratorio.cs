using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.U2D.Sprites;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.SceneManagement;
using TecnologiaNaPratica.QuebraBlocos;

public static class CriarLaboratorio
{
    static Sprite[] sprites;
    static Font fonte;
    static readonly Color Azul = new Color(0.045f, 0.12f, 0.19f, 0.97f);

    [MenuItem("Tecnologia na Pratica/Criar cena do quebra-blocos")]
    public static void Criar()
    {
        Directory.CreateDirectory("Assets/Scenes");
        Directory.CreateDirectory("Assets/Dados");
        Directory.CreateDirectory("Assets/Prefabs");
        AssetDatabase.Refresh();
        PrepararSprites();
        fonte = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        PlayerSettings.companyName = "Rodrigo Sillos";
        PlayerSettings.productName = "Ruinas em Jogo";
        PlayerSettings.defaultScreenWidth = 1280;
        PlayerSettings.defaultScreenHeight = 720;
        PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
        PlayerSettings.runInBackground = false;
        PlayerSettings.colorSpace = ColorSpace.Gamma;
        var settings = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
        var inputMode = settings.FindProperty("activeInputHandler");
        if (inputMode != null) inputMode.intValue = 1;
        settings.ApplyModifiedPropertiesWithoutUndo();
        Time.fixedDeltaTime = 0.02f;
        Physics2D.gravity = Vector2.zero;

        var cam = new GameObject("Main Camera", typeof(Camera), typeof(AudioListener));
        cam.tag = "MainCamera"; cam.transform.position = new Vector3(0, 0, -10);
        var camera = cam.GetComponent<Camera>(); camera.orthographic = true; camera.orthographicSize = 6f;
        camera.clearFlags = CameraClearFlags.SolidColor;
        camera.backgroundColor = new Color(0.035f, 0.085f, 0.12f);
        var decoracao = new GameObject("Cenario").transform;
        for (int y = -3; y <= 3; y++)
            for (int x = -5; x <= 5; x++)
            {
                var piso = Desenhar("Piso", sprites[0], new Vector3(x * 1.55f, y * 1.55f), new Vector2(1.6f, 1.6f), -20);
                piso.GetComponent<SpriteRenderer>().color = new Color(0.50f, 0.59f, 0.65f);
                piso.transform.SetParent(decoracao);
            }
        var fisica = new PhysicsMaterial2D("Rebote") { friction = 0, bounciness = 1 };
        SalvarAsset(fisica, "Assets/Dados/Rebote.physicsMaterial2D");
        Parede("ParedeEsquerda", new Vector2(-7.65f, 0), new Vector2(.5f, 11), fisica);
        Parede("ParedeDireita", new Vector2(7.65f, 0), new Vector2(.5f, 11), fisica);
        Parede("ParedeSuperior", new Vector2(0, 5f), new Vector2(15.8f, .5f), fisica);
        for (int i = -4; i <= 4; i++)
        {
            Desenhar("Muralha", sprites[1], new Vector3(-7.55f, i * 1.2f), new Vector2(.7f, 1.3f), 1).transform.SetParent(decoracao);
            Desenhar("Muralha", sprites[1], new Vector3(7.55f, i * 1.2f), new Vector2(.7f, 1.3f), 1).transform.SetParent(decoracao);
        }
        for (int i = 0; i < 6; i++)
        {
            float x = i % 2 == 0 ? -7.3f : 7.3f;
            Desenhar("Vegetacao", sprites[7], new Vector3(x, 4f - (i / 2) * 3.7f), new Vector2(1.35f, 1.2f), 2).transform.SetParent(decoracao);
        }

        var sistema = new GameObject("Partida");
        var entrada = sistema.AddComponent<EntradaJogador>();
        var som = sistema.AddComponent<SomJogo>();
        var controle = sistema.AddComponent<ControlePartida>();
        var raqueteGo = Desenhar("Raquete", sprites[5], new Vector3(0, -4.15f), new Vector2(2.2f, .5f), 4);
        var corpoRaquete = raqueteGo.AddComponent<Rigidbody2D>();
        corpoRaquete.bodyType = RigidbodyType2D.Kinematic;
        corpoRaquete.interpolation = RigidbodyInterpolation2D.Interpolate;
        var colRaquete = raqueteGo.AddComponent<BoxCollider2D>();
        colRaquete.sharedMaterial = fisica;
        var raquete = raqueteGo.AddComponent<Raquete>();
        Atribuir(raquete, "entrada", entrada); Atribuir(raquete, "controle", controle);

        var bolaGo = Desenhar("Bola", sprites[6], new Vector3(0, -3.55f), new Vector2(.55f, .55f), 5);
        var corpoBola = bolaGo.AddComponent<Rigidbody2D>();
        corpoBola.gravityScale = 0; corpoBola.constraints = RigidbodyConstraints2D.FreezeRotation;
        corpoBola.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
        corpoBola.interpolation = RigidbodyInterpolation2D.Interpolate;
        var circulo = bolaGo.AddComponent<CircleCollider2D>();
        circulo.radius = sprites[6].bounds.size.x * .27f;
        circulo.sharedMaterial = fisica;
        var bola = bolaGo.AddComponent<Bola>();
        Atribuir(bola, "raquete", raquete); Atribuir(bola, "controle", controle);

        var blocoGo = Desenhar("Bloco", sprites[2], Vector3.zero, new Vector2(1.57f, .67f), 3);
        var colBloco = blocoGo.AddComponent<BoxCollider2D>(); colBloco.sharedMaterial = fisica;
        var bloco = blocoGo.AddComponent<Bloco>();
        Atribuir(bloco, "normal", sprites[2]); Atribuir(bloco, "reforcado", sprites[3]); Atribuir(bloco, "danificado", sprites[4]);
        var prefab = PrefabUtility.SaveAsPrefabAsset(blocoGo, "Assets/Prefabs/Bloco.prefab").GetComponent<Bloco>();
        UnityEngine.Object.DestroyImmediate(blocoGo);
        var campo = new GameObject("Blocos").transform;
        string[][] desenhos = {
            new[] { "00111100", "01111110", "11111111", "01100110" },
            new[] { "12122121", "01111110", "11011011", "01100110" },
            new[] { "22200222", "21111112", "01222210", "11100111", "01011010" }
        };
        string[] nomes = { "Pátio de entrada", "Muralhas antigas", "Coração das ruínas" };
        var fases = new FaseDados[3];
        for (int i = 0; i < 3; i++)
        {
            var fase = ScriptableObject.CreateInstance<FaseDados>(); fase.nome = nomes[i]; fase.linhas = desenhos[i];
            SalvarAsset(fase, $"Assets/Dados/Fase{i + 1}.asset"); fases[i] = fase;
        }
        Atribuir(controle, "entrada", entrada); Atribuir(controle, "raquete", raquete);
        Atribuir(controle, "bola", bola); Atribuir(controle, "som", som);
        Atribuir(controle, "blocoPrefab", prefab); Atribuir(controle, "campoBlocos", campo);
        var sc = new SerializedObject(controle); var lista = sc.FindProperty("fases"); lista.arraySize = 3;
        for (int i = 0; i < 3; i++) lista.GetArrayElementAtIndex(i).objectReferenceValue = fases[i];
        sc.ApplyModifiedPropertiesWithoutUndo();
        CriarInterface(controle);
        EditorSceneManager.SaveScene(SceneManager.GetActiveScene(), "Assets/Scenes/QuebraBlocos.unity");
        EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene("Assets/Scenes/QuebraBlocos.unity", true) };
        AssetDatabase.SaveAssets();
        Debug.Log("TNP_CENA_CRIADA: três fases, sprites, física e interface.");
    }

    static void PrepararSprites()
    {
        const string path = "Assets/Art/RuinasAtlas.png";
        var imp = (TextureImporter)AssetImporter.GetAtPath(path);
        imp.textureType = TextureImporterType.Sprite; imp.spriteImportMode = SpriteImportMode.Multiple;
        imp.isReadable = true; imp.alphaIsTransparency = true; imp.maxTextureSize = 2048;
        imp.mipmapEnabled = false; imp.textureCompression = TextureImporterCompression.Uncompressed;
        imp.SaveAndReimport();
        var tex = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        var cores = tex.GetPixels32();
        var fabrica = new SpriteDataProviderFactories(); fabrica.Init();
        var provedor = fabrica.GetSpriteEditorDataProviderFromObject(imp);
        provedor.InitSpriteEditorDataProvider();
        var anteriores = provedor.GetSpriteRects().ToDictionary(r => r.name, r => r.spriteID);
        var metas = new SpriteRect[9];
        string[] nomes = { "Piso", "Muralha", "Pedra", "PedraReforcada", "PedraDanificada", "Raquete", "Esfera", "Vegetacao", "Portal" };
        for (int i = 0; i < 9; i++)
        {
            int col = i % 3, row = 2 - i / 3;
            int x0 = col * tex.width / 3, x1 = (col + 1) * tex.width / 3;
            int y0 = row * tex.height / 3, y1 = (row + 1) * tex.height / 3;
            // O portal ultrapassa a divisão de células; os recortes não podem se sobrepor.
            if (i == 5) y0 = Mathf.RoundToInt(tex.height * .40f);
            if (i == 8) y1 = Mathf.RoundToInt(tex.height * .38f);
            int minX = x1, minY = y1, maxX = x0, maxY = y0;
            for (int y = y0; y < y1; y++) for (int x = x0; x < x1; x++)
            {
                if (cores[y * tex.width + x].a < 20) continue;
                minX = Math.Min(minX, x); minY = Math.Min(minY, y);
                maxX = Math.Max(maxX, x); maxY = Math.Max(maxY, y);
            }
            metas[i] = new SpriteRect { name = nomes[i], rect = new Rect(minX, minY, maxX - minX + 1, maxY - minY + 1), alignment = SpriteAlignment.Center, pivot = new Vector2(.5f, .5f), spriteID = anteriores.TryGetValue(nomes[i], out var id) ? id : GUID.Generate() };
        }
        provedor.SetSpriteRects(metas);
        provedor.GetDataProvider<ISpriteNameFileIdDataProvider>().SetNameFileIdPairs(metas.Select(r => new SpriteNameFileIdPair(r.name, r.spriteID)));
        provedor.Apply(); imp.SaveAndReimport();
        var todos = AssetDatabase.LoadAllAssetsAtPath(path).OfType<Sprite>().ToArray();
        sprites = nomes.Select(nome => todos.First(s => s.name == nome)).ToArray();
    }
    static GameObject Desenhar(string nome, Sprite sprite, Vector3 pos, Vector2 tamanho, int ordem)
    {
        var go = new GameObject(nome, typeof(SpriteRenderer)); go.transform.position = pos;
        var sr = go.GetComponent<SpriteRenderer>(); sr.sprite = sprite; sr.sortingOrder = ordem;
        go.transform.localScale = new Vector3(tamanho.x / sprite.bounds.size.x, tamanho.y / sprite.bounds.size.y, 1);
        return go;
    }
    static void Parede(string nome, Vector2 pos, Vector2 tamanho, PhysicsMaterial2D material)
    {
        var go = new GameObject(nome, typeof(BoxCollider2D)); go.transform.position = pos;
        var col = go.GetComponent<BoxCollider2D>(); col.size = tamanho; col.sharedMaterial = material;
    }
    static void SalvarAsset(UnityEngine.Object obj, string path)
    {
        if (AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(path) != null) AssetDatabase.DeleteAsset(path);
        AssetDatabase.CreateAsset(obj, path);
    }
    static void Atribuir(UnityEngine.Object obj, string campo, UnityEngine.Object valor)
    {
        var s = new SerializedObject(obj); s.FindProperty(campo).objectReferenceValue = valor; s.ApplyModifiedPropertiesWithoutUndo();
    }
    static RectTransform Retangulo(string nome, Transform pai, Vector2 ancora, Vector2 pos, Vector2 tamanho)
    {
        var go = new GameObject(nome, typeof(RectTransform)); var rt = go.GetComponent<RectTransform>();
        rt.SetParent(pai, false); rt.anchorMin = rt.anchorMax = ancora; rt.anchoredPosition = pos; rt.sizeDelta = tamanho;
        return rt;
    }
    static Text Texto(string nome, Transform pai, string texto, Vector2 pos, Vector2 tamanho, int tamanhoFonte, Vector2? ancora = null)
    {
        var rt = Retangulo(nome, pai, ancora ?? new Vector2(.5f, .5f), pos, tamanho);
        var t = rt.gameObject.AddComponent<Text>(); t.font = fonte; t.text = texto;
        t.fontSize = tamanhoFonte; t.color = new Color(.91f, .95f, .96f); t.alignment = TextAnchor.MiddleCenter;
        t.horizontalOverflow = HorizontalWrapMode.Wrap; t.verticalOverflow = VerticalWrapMode.Overflow;
        t.raycastTarget = false; return t;
    }
    static Button Botao(string nome, Transform pai, string texto, Vector2 pos)
    {
        var rt = Retangulo(nome, pai, new Vector2(.5f, .5f), pos, new Vector2(290, 43));
        var im = rt.gameObject.AddComponent<Image>(); im.color = new Color(.14f, .36f, .44f);
        var b = rt.gameObject.AddComponent<Button>();
        var cs = b.colors; cs.highlightedColor = new Color(1f, .8f, .45f); cs.selectedColor = cs.highlightedColor; b.colors = cs;
        Texto("Legenda", rt, texto, Vector2.zero, new Vector2(280, 40), 19);
        return b;
    }
    static void CriarInterface(ControlePartida controle)
    {
        var canvas = new GameObject("Interface", typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
        canvas.GetComponent<Canvas>().renderMode = RenderMode.ScreenSpaceOverlay;
        var scaler = canvas.GetComponent<CanvasScaler>(); scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1280, 720); scaler.matchWidthOrHeight = .5f;
        var eventos = new GameObject("EventSystem", typeof(EventSystem), typeof(InputSystemUIInputModule));
        eventos.GetComponent<InputSystemUIInputModule>().AssignDefaultActions();
        var hud = canvas.AddComponent<InterfacePartida>();
        Atribuir(hud, "controle", controle);
        var placar = Texto("Placar", canvas.transform, "", new Vector2(0, -26), new Vector2(1200, 45), 22, new Vector2(.5f, 1));
        var instrucao = Texto("Instrucao", canvas.transform, "", new Vector2(0, 24), new Vector2(1200, 42), 19, new Vector2(.5f, 0));
        var painel = Retangulo("Menu", canvas.transform, new Vector2(.5f, .5f), Vector2.zero, new Vector2(710, 640));
        painel.gameObject.AddComponent<Image>().color = Azul;
        var titulo = Texto("Titulo", painel, "", new Vector2(0, 258), new Vector2(650, 55), 34);
        var resumo = Texto("Resumo", painel, "", new Vector2(0, 122), new Vector2(650, 196), 19);
        var jogar = Botao("Jogar", painel, "INICIAR PARTIDA", new Vector2(-165, -44));
        var continuar = Botao("Continuar", painel, "CONTINUAR", new Vector2(165, -44));
        var menu = Botao("Voltar", painel, "MENU INICIAL", new Vector2(-165, -100));
        var sair = Botao("Sair", painel, "SAIR", new Vector2(165, -100));
        Texto("VolumeLabel", painel, "VOLUME", new Vector2(0, -169), new Vector2(250, 36), 18);
        var barra = Retangulo("Volume", painel, new Vector2(.5f, .5f), new Vector2(0, -217), new Vector2(400, 10));
        var fundo = barra.gameObject.AddComponent<Image>(); fundo.color = new Color(.16f, .23f, .28f);
        var slider = barra.gameObject.AddComponent<Slider>();
        var alca = Retangulo("Alca", barra, new Vector2(.5f, .5f), Vector2.zero, new Vector2(18, 20));
        alca.gameObject.AddComponent<Image>().color = new Color(1f, .68f, .25f);
        slider.handleRect = alca; slider.targetGraphic = alca.GetComponent<Image>(); slider.minValue = 0; slider.maxValue = 1;
        Atribuir(hud, "placar", placar); Atribuir(hud, "instrucao", instrucao); Atribuir(hud, "painelMenu", painel.gameObject);
        Atribuir(hud, "tituloMenu", titulo); Atribuir(hud, "resumoMenu", resumo);
        Atribuir(hud, "jogar", jogar); Atribuir(hud, "continuar", continuar); Atribuir(hud, "menu", menu);
        Atribuir(hud, "sair", sair); Atribuir(hud, "volume", slider);
    }
    public static void BuildWindows()
    {
        var resultado = BuildPipeline.BuildPlayer(EditorBuildSettings.scenes, "Build/Windows/RuinasEmJogo.exe", BuildTarget.StandaloneWindows64, BuildOptions.None);
        if (resultado.summary.result != UnityEditor.Build.Reporting.BuildResult.Succeeded)
            throw new Exception("O build falhou: " + resultado.summary.result);
        Debug.Log("TNP_BUILD_OK: " + resultado.summary.totalSize);
    }
    public static void CriarECompilar() { Criar(); BuildWindows(); }
}
