using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Tilemaps;
using TecnologiaNaPratica;

public static class CriarPlataforma
{
    [MenuItem("Tecnologia na Pratica/Criar tres fases")]
    public static void Criar()
    {
        for (int nivel = 0; nivel < 3; nivel++)
            CriarFase(nivel);
        EditorBuildSettings.scenes = Enumerable.Range(1, 3).Select(i => new EditorBuildSettingsScene("Assets/Scenes/Fase" + i + ".unity", true)).ToArray();
        AssetDatabase.SaveAssets();
    }

    static void CriarFase(int nivel)
    {
        var arte = FerramentasEditor.Preparar("Caminho do Portal", -27);
        Camera.main.orthographicSize = 5.4f;
        Camera.main.backgroundColor = new Color(.32f, .58f, .69f);
        var campanha = new GameObject("Campanha").AddComponent<Campanha>();
        campanha.indice = nivel;
        campanha.titulo = new[]
        {
            "Pátio das descobertas",
            "Pontes esquecidas",
            "O último guardião"
        }[nivel];
        campanha.checkpoints = new[]
        {
            new Vector2(2, -.3f),
            new Vector2(28, -.3f),
            new Vector2(60, -.3f)
        };
        var fundo = new GameObject("Ruinas ao fundo").transform;
        var importador=(TextureImporter)AssetImporter.GetAtPath("Assets/Art/PaisagemRuinas.png");
        importador.textureType=TextureImporterType.Sprite;
        importador.spriteImportMode=SpriteImportMode.Single;
        importador.maxTextureSize=2048;importador.mipmapEnabled=false;
        importador.SaveAndReimport();
        fundo.gameObject.AddComponent<PaisagemRuinas>().fundo=AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Art/PaisagemRuinas.png");
        for (int x = 0; x < 80; x += 6)
        {
            BancoArte.Desenhar("Vegetacao", arte.ambiente[7], fundo, new Vector2(x, -2.8f), new Vector2(5, 3), -10).color = new Color(.25f, .53f, .58f);
        }

        var grid = new GameObject("Terreno", typeof(Grid));
        grid.GetComponent<Grid>().cellSize = new Vector3(2, 1, 1);
        var solo = new GameObject("Solo", typeof(Tilemap), typeof(TilemapRenderer), typeof(Rigidbody2D), typeof(TilemapCollider2D), typeof(CompositeCollider2D));
        solo.transform.SetParent(grid.transform);
        solo.layer = 10;
        solo.GetComponent<Rigidbody2D>().bodyType = RigidbodyType2D.Static;
        solo.GetComponent<TilemapCollider2D>().compositeOperation = Collider2D.CompositeOperation.Merge;
        var material = FerramentasEditor.Salvar(new PhysicsMaterial2D("Sem atrito") { friction = 0, bounciness = 0 }, "Assets/Dados/SemAtrito.physicsMaterial2D");
        solo.GetComponent<CompositeCollider2D>().sharedMaterial = material;
        solo.AddComponent<TerrenoFisico>();
        var tile = ScriptableObject.CreateInstance<Tile>();
        tile.sprite = arte.atores[12];
        tile.colliderType = Tile.ColliderType.Grid;
        // O collider Grid deve manter a célula inteira; escalar o tile também reduz a geometria física.
        tile.transform = Matrix4x4.identity;
        tile = FerramentasEditor.Salvar(tile, "Assets/Dados/PedraComMusgo.asset");
        int[][] buracos =
        {
            new[]
            {
                8,
                9,
                21,
                22
            },
            new[]
            {
                7,
                8,
                9,
                22,
                23
            },
            new[]
            {
                8,
                9,
                18,
                19,
                20
            }
        };
        var mapa = solo.GetComponent<Tilemap>();
        for (int x = 0; x < 40; x++)
            if (!buracos[nivel].Contains(x))
                for (int y = -4; y <= -2; y++)
                    mapa.SetTile(new Vector3Int(x, y, 0), tile);
        mapa.RefreshAllTiles();
        solo.GetComponent<TilemapCollider2D>().ProcessTilemapChanges();
        solo.GetComponent<CompositeCollider2D>().GenerateGeometry();
        Debug.Log("TNP_TERRAIN_PATHS=" + solo.GetComponent<CompositeCollider2D>().pathCount);
        foreach (float x in new[]
        {
            -.5f,
            80.5f
        }

        )
        {
            var limite = new GameObject("Limite lateral");
            limite.transform.position = new Vector2(x, 2);
            limite.layer = 10;
            limite.AddComponent<BoxCollider2D>().size = new Vector2(1, 16);
        }

        var moveis = new List<PlataformaMovel>();
        if (nivel == 1)
            moveis.Add(Plataforma(arte, new Vector2(14.3f, -.35f), new Vector2(4.6f, 0), true));
        if (nivel == 2)
            moveis.Add(Plataforma(arte, new Vector2(36.3f, -.35f), new Vector2(4.6f, 0), true));
        Plataforma(arte, new Vector2(24, 1), Vector2.zero, false);
        Plataforma(arte, new Vector2(54, 1.1f), Vector2.zero, false);
        campanha.moveis = moveis.ToArray();
        var bala = new GameObject("Projetil");
        bala.AddComponent<Projetil>();
        BancoArte.Desenhar("Esfera", arte.ambiente[6], bala.transform, Vector2.zero, new Vector2(.22f, .22f), 5);
        var prefab = PrefabUtility.SaveAsPrefabAsset(bala, "Assets/Prefabs/Projetil.prefab");
        Object.DestroyImmediate(bala);
        campanha.Projeteis = new GameObject("Reserva de projeteis").AddComponent<ReservaProjeteis>();
        campanha.Projeteis.prefab = prefab.GetComponent<Projetil>();
        var j = FerramentasEditor.Corpo("Explorador", campanha.checkpoints[0], 8, RigidbodyType2D.Dynamic);
        var capsule = j.AddComponent<CapsuleCollider2D>();
        capsule.size = new Vector2(.62f, 1.2f);
        capsule.sharedMaterial = material;
        j.AddComponent<Vida>();
        var motor = j.AddComponent<MotorPlataforma>();
        motor.controle = campanha;
        campanha.Jogador = motor;
        var anim = j.AddComponent<AnimacaoExplorador>();
        anim.motor = motor;
        anim.visual = BancoArte.Desenhar("Visual", arte.atores[0], j.transform, new Vector2(0, .1f), new Vector2(.95f, 1.4f), 3);
        var cam = Camera.main.gameObject.AddComponent<CameraAventura>();
        cam.alvo = motor;
        cam.larguraFase = 80;
        var inimigos = new List<InimigoPlataforma>();
        inimigos.Add(Inimigo(arte, campanha, 0, new Vector2(12, -.4f), 1.5f));
        inimigos.Add(Inimigo(arte, campanha, 1, new Vector2(33, 1), 2));
        inimigos.Add(Inimigo(arte, campanha, 2, new Vector2(49, -.4f), 0));
        if (nivel > 0)
            inimigos.Add(Inimigo(arte, campanha, 0, new Vector2(64, -.4f), 2));
        if (nivel == 2)
            inimigos.Add(Inimigo(arte, campanha, 3, new Vector2(71, 0), 0));
        campanha.inimigos = inimigos.ToArray();
        var contatos = new List<ContatoFase>();
        float[] xs =
        {
            8,
            13,
            18,
            24,
            30,
            36,
            44,
            51,
            54,
            63,
            69,
            74
        };
        for (int i = 0; i < xs.Length; i++)
        {
            float y = xs[i] == 24 || xs[i] == 54 ? 2.1f : (i == 2 || i == 6 ? 1 : -.1f);
            contatos.Add(Contato(arte, campanha, TipoContato.Cristal, i, new Vector2(xs[i], y), new Vector2(.45f, .65f), arte.atores[15]));
        }

        for (int i = 1; i <= 2; i++)
            contatos.Add(Contato(arte, campanha, TipoContato.Checkpoint, i, campanha.checkpoints[i] + new Vector2(0, .25f), new Vector2(.9f, 1.6f), arte.atores[14]));
        foreach (float x in nivel == 0 ? new[]
        {
            38f
        }

        : nivel == 1 ? new[]
        {
            26f,
            57f
        }

        : new[]
        {
            26f,
            47f,
            66f
        }

        )
            contatos.Add(Contato(arte, campanha, TipoContato.Espinhos, 0, new Vector2(x, -.65f), new Vector2(1.6f, .7f), arte.atores[13]));
        contatos.Add(Contato(arte, campanha, TipoContato.Portal, 0, new Vector2(77, .65f), new Vector2(2.7f, 3.3f), arte.ambiente[8]));
        campanha.contatos = contatos.ToArray();
        FerramentasEditor.Cena("Fase" + (nivel + 1));
    }

    static PlataformaMovel Plataforma(BancoArte arte, Vector2 pos, Vector2 delta, bool movel)
    {
        var go = FerramentasEditor.Corpo(movel ? "Ponte movel" : "Plataforma de passagem", pos, 10, RigidbodyType2D.Kinematic);
        var c = go.AddComponent<BoxCollider2D>();
        c.size = new Vector2(3, .35f);
        c.usedByEffector = true;
        var e = go.AddComponent<PlatformEffector2D>();
        e.useOneWay = true;
        e.useOneWayGrouping = true;
        e.surfaceArc = 160;
        e.useSideFriction = false;
        BancoArte.Desenhar("Pedra com musgo", arte.atores[12], go.transform, new Vector2(0, -.2f), new Vector2(3, .8f), 1);
        if (!movel)
            return null;
        var m = go.AddComponent<PlataformaMovel>();
        m.deslocamento = delta;
        m.periodo = 5;
        return m;
    }

    static InimigoPlataforma Inimigo(BancoArte arte, Campanha campanha, int tipo, Vector2 pos, float alcance)
    {
        var go = new GameObject(tipo == 3 ? "Guardiao" : "Inimigo tipo " + tipo);
        go.transform.position = pos;
        go.layer = 9;
        var c = go.AddComponent<CircleCollider2D>();
        c.radius = tipo == 3 ? .8f : .4f;
        c.isTrigger = true;
        go.AddComponent<Vida>();
        var e = go.AddComponent<InimigoPlataforma>();
        e.controle = campanha;
        e.tipo = tipo;
        e.alcance = alcance;
        e.visual = BancoArte.Desenhar("Visual", arte.atores[tipo == 0 ? 11 : tipo == 1 ? 8 : tipo == 2 ? 9 : 10], go.transform, Vector2.zero, tipo == 3 ? new Vector2(1.7f, 2) : new Vector2(.9f, 1), 2);
        return e;
    }

    static ContatoFase Contato(BancoArte arte, Campanha campanha, TipoContato tipo, int id, Vector2 pos, Vector2 tamanho, Sprite sprite)
    {
        var go = new GameObject(tipo + " " + id);
        go.transform.position = pos;
        var c = go.AddComponent<BoxCollider2D>();
        c.isTrigger = true;
        c.size = tipo == TipoContato.Portal ? new Vector2(1, 2) : tamanho * .8f;
        var contato = go.AddComponent<ContatoFase>();
        contato.controle = campanha;
        contato.tipo = tipo;
        contato.id = id;
        contato.visual = BancoArte.Desenhar("Visual", sprite, go.transform, Vector2.zero, tamanho, tipo == TipoContato.Portal ? -1 : 1);
        return contato;
    }

    public static void CriarECompilar()
    {
        Criar();
        FerramentasEditor.Compilar("CaminhoDoPortal");
    }
}
