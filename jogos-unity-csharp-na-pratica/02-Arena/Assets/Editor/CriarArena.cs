using UnityEditor;
using UnityEngine;
using TecnologiaNaPratica;

public static class CriarArena
{
    [MenuItem("Tecnologia na Pratica/Criar arena")]
    public static void Criar()
    {
        var arte = FerramentasEditor.Preparar("Arena das Ruinas", 0);
        var cenario = new GameObject("Cenario").transform;
        for (int y = -3; y <= 3; y++)
            for (int x = -6; x <= 6; x++)
            {
                var piso = BancoArte.Desenhar("Piso", arte.ambiente[0], cenario, new Vector2(x * 1.5f, y * 1.5f), new Vector2(1.55f, 1.55f), -20);
                piso.color = new Color(.42f, .54f, .62f);
            }

        for (int x = -6; x <= 6; x++)
            for (int lado = -1; lado <= 1; lado += 2)
                BancoArte.Desenhar("Muralha", arte.ambiente[1], cenario, new Vector2(x * 1.5f, lado * 4.85f), new Vector2(1.55f, .7f), -5);
        for (int y = -3; y <= 3; y++)
            for (int lado = -1; lado <= 1; lado += 2)
                BancoArte.Desenhar("Muralha", arte.ambiente[1], cenario, new Vector2(lado * 9.05f, y * 1.5f), new Vector2(.7f, 1.55f), -5);
        for (int i = 0; i < 4; i++)
            BancoArte.Desenhar("Vegetacao", arte.ambiente[7], cenario, new Vector2(i % 2 == 0 ? -8.6f : 8.6f, i < 2 ? 4.35f : -4.35f), new Vector2(1.7f, 1.5f), -3);
        foreach (var pos in new[]
        {
            new Vector2(-9, 0),
            new Vector2(9, 0),
            new Vector2(0, 4.9f),
            new Vector2(0, -4.9f)
        }

        )
        {
            var wall = new GameObject("Limite");
            wall.layer = 10;
            wall.transform.position = pos;
            wall.AddComponent<BoxCollider2D>().size = pos.x == 0 ? new Vector2(19, .5f) : new Vector2(.5f, 10);
        }

        var go = new GameObject("Controle da arena");
        var arena = go.AddComponent<Arena>();
        var bala = new GameObject("Projetil");
        var proj = bala.AddComponent<Projetil>();
        BancoArte.Desenhar("Esfera", arte.ambiente[6], bala.transform, Vector2.zero, new Vector2(.24f, .24f), 5);
        var projPrefab = PrefabUtility.SaveAsPrefabAsset(bala, "Assets/Prefabs/Projetil.prefab").GetComponent<Projetil>();
        Object.DestroyImmediate(bala);
        var reserva = new GameObject("Reserva de projeteis").AddComponent<ReservaProjeteis>();
        reserva.prefab = projPrefab;
        arena.Projeteis = reserva;
        var enemy = new GameObject("Robo");
        enemy.layer = 9;
        enemy.AddComponent<CircleCollider2D>().isTrigger = true;
        enemy.GetComponent<CircleCollider2D>().radius = .40f;
        enemy.AddComponent<Vida>();
        var e = enemy.AddComponent<InimigoArena>();
        e.visual = BancoArte.Desenhar("Visual", arte.atores[8], enemy.transform, Vector2.zero, Vector2.one, 2);
        arena.inimigoPrefab = PrefabUtility.SaveAsPrefabAsset(enemy, "Assets/Prefabs/Robo.prefab").GetComponent<InimigoArena>();
        Object.DestroyImmediate(enemy);
        var jogador = FerramentasEditor.Corpo("Explorador", Vector2.zero, 8, RigidbodyType2D.Dynamic);
        jogador.GetComponent<Rigidbody2D>().gravityScale = 0;
        jogador.AddComponent<CircleCollider2D>().radius = .32f;
        jogador.AddComponent<Vida>();
        var j = jogador.AddComponent<JogadorArena>();
        j.controle = arena;
        j.visual = BancoArte.Desenhar("Visual", arte.atores[4], jogador.transform, Vector2.zero, new Vector2(.9f, 1.25f), 3);
        arena.Jogador = j;
        int[, ] quantidades =
        {
            {
                5,
                0,
                0
            },
            {
                5,
                2,
                0
            },
            {
                6,
                3,
                1
            },
            {
                6,
                4,
                2
            },
            {
                7,
                4,
                3
            }
        };
        string[] titulos =
        {
            "O despertar",
            "A linha de tiro",
            "Blindagem antiga",
            "Cerco às muralhas",
            "O coração da arena"
        };
        arena.ondas = new OndaDados[5];
        for (int i = 0; i < 5; i++)
        {
            var onda = ScriptableObject.CreateInstance<OndaDados>();
            onda.titulo = titulos[i];
            onda.perseguidores = quantidades[i, 0];
            onda.atiradores = quantidades[i, 1];
            onda.resistentes = quantidades[i, 2];
            onda.intervalo = 1.2f - i * .12f;
            arena.ondas[i] = FerramentasEditor.Salvar(onda, "Assets/Dados/Onda" + (i + 1) + ".asset");
        }

        FerramentasEditor.Cena("Arena");
    }

    public static void CriarECompilar()
    {
        Criar();
        FerramentasEditor.Compilar("ArenaDasRuinas");
    }
}
