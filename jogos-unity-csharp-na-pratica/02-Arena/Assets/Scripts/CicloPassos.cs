using System.Collections.Generic;
using UnityEngine;

namespace TecnologiaNaPratica
{
    // Anima a malha da arte original. Não altera textura, collider ou movimento físico.
    public sealed class CicloPassos : MonoBehaviour
    {
        const int Colunas = 24, Linhas = 32;
        Mesh malha;
        MeshRenderer desenho;
        Material material;
        MaterialPropertyBlock propriedades;
        Sprite atual;
        Vector3[] vertices;
        Vector2[] uv;
        Vector2[] normalizados;
        float fase;
        SpriteRenderer original;

        public static void Aplicar(SpriteRenderer visual, bool andando, float velocidade, bool lateral = true)
        {
            var ciclo = visual.GetComponent<CicloPassos>();
            if (!ciclo && !andando) return;
            if (!ciclo) ciclo = visual.gameObject.AddComponent<CicloPassos>();
            ciclo.Atualizar(visual, andando, velocidade, lateral);
        }

        void Inicializar(SpriteRenderer visual)
        {
            original = visual;
            malha = new Mesh { name = "Explorador — malha de passos" };
            malha.MarkDynamic();
            var parte = new GameObject("Passos articulados");
            parte.transform.SetParent(transform, false);
            parte.layer = gameObject.layer;
            var filtro = parte.AddComponent<MeshFilter>();
            filtro.sharedMesh = malha;
            desenho = parte.AddComponent<MeshRenderer>();
            material = new Material(visual.sharedMaterial) { name = "Explorador — arte original" };
            desenho.sharedMaterial = material;
            desenho.sortingLayerID = visual.sortingLayerID;
            desenho.sortingOrder = visual.sortingOrder;
            propriedades = new MaterialPropertyBlock();
            int total = (Colunas + 1) * (Linhas + 1);
            vertices = new Vector3[total]; uv = new Vector2[total]; normalizados = new Vector2[total];
            var cores = new Color[total];
            var indices = new List<int>(Colunas * Linhas * 6);
            for (int y = 0; y <= Linhas; y++)
            for (int x = 0; x <= Colunas; x++)
            {
                int i = y * (Colunas + 1) + x;
                normalizados[i] = new Vector2((float)x / Colunas, (float)y / Linhas);
                cores[i] = Color.white;
                if (x == Colunas || y == Linhas) continue;
                int b = i + Colunas + 1;
                indices.Add(i); indices.Add(b); indices.Add(i + 1);
                indices.Add(i + 1); indices.Add(b); indices.Add(b + 1);
            }
            malha.vertices = vertices; malha.colors = cores; malha.triangles = indices.ToArray();
        }

        void Atualizar(SpriteRenderer visual, bool andando, float velocidade, bool lateral)
        {
            if (!malha) Inicializar(visual);
            if (!andando)
            {
                desenho.enabled = false; visual.enabled = true; fase = 0;
                return;
            }
            var sprite = visual.sprite;
            if (!sprite) return;
            if (sprite != atual)
            {
                atual = sprite;
                var r = sprite.rect;
                for (int i = 0; i < uv.Length; i++)
                    uv[i] = new Vector2((r.x + normalizados[i].x * r.width) / sprite.texture.width,
                                        (r.y + normalizados[i].y * r.height) / sprite.texture.height);
                malha.uv = uv;
                material.mainTexture = sprite.texture;
            }
            // A distância percorrida controla a cadência: andar devagar produz passos lentos.
            fase = Mathf.Repeat(fase + Mathf.Abs(velocidade) * Time.deltaTime * 3.15f, Mathf.PI * 2);
            float intensidade = Mathf.Clamp01(Mathf.Abs(velocidade) / 4);
            Vector2 tamanho = sprite.rect.size / sprite.pixelsPerUnit;
            Vector2 pivo = sprite.pivot / sprite.pixelsPerUnit;
            float balanco = Mathf.Sin(fase * 2) * .007f * intensidade;
            for (int i = 0; i < vertices.Length; i++)
            {
                Vector2 n = normalizados[i];
                Vector2 p = Vector2.Scale(n, tamanho);
                float cintura = 1 - Suave(.25f, .40f, n.y);
                if (lateral)
                {
                    // O braço e a arma ficam acima da região articulada das pernas.
                    if (n.x > .73f && n.y > .20f) cintura = 0;
                    Vector2 esquerda = Perna(p, tamanho, n.y, fase, intensidade, false);
                    Vector2 direita = Perna(p, tamanho, n.y, fase + Mathf.PI, intensidade, true);
                    p = Vector2.Lerp(p, Vector2.Lerp(esquerda, direita, Suave(.43f, .56f, n.x)), cintura);
                }
                else
                {
                    float lado = n.x < .5f ? 1 : -1;
                    float passo = Mathf.Sin(fase) * lado;
                    // Vista de cima: alterna o avanço dos pés, preservando cabeça e mochila.
                    float peso = cintura;
                    if (sprite.name == "Ator04" && n.x > .37f && n.x < .60f) peso *= .08f;
                    p.x += passo * tamanho.x * .04f * peso * intensidade;
                    p.y += passo * tamanho.y * .085f * peso * intensidade;
                }
                p.y += balanco * tamanho.y;
                p -= pivo;
                if (visual.flipX) p.x = -p.x;
                vertices[i] = p;
            }
            malha.vertices = vertices;
            malha.bounds = new Bounds(Vector3.zero, new Vector3(tamanho.x * 2, tamanho.y * 2, 1));
            propriedades.SetColor("_Color", visual.color);
            propriedades.SetColor("_RendererColor", Color.white);
            propriedades.SetVector("_Flip", Vector4.one);
            desenho.SetPropertyBlock(propriedades);
            desenho.enabled = true; visual.enabled = false;
        }

        static Vector2 Perna(Vector2 p, Vector2 tamanho, float altura, float fase, float intensidade, bool direita)
        {
            Vector2 quadril = Vector2.Scale(new Vector2(direita ? .59f : .35f, .33f), tamanho);
            Vector2 joelho = Vector2.Scale(new Vector2(direita ? .62f : .28f, .155f), tamanho);
            float coxa = Mathf.Sin(fase) * .72f * intensidade;
            float flexao = -Mathf.Max(0, Mathf.Cos(fase)) * .95f * intensidade;
            Vector2 esticada = quadril + Girar(p - quadril, coxa);
            Vector2 novoJoelho = quadril + Girar(joelho - quadril, coxa);
            Vector2 dobrada = novoJoelho + Girar(p - joelho, coxa + flexao);
            return Vector2.Lerp(esticada, dobrada, 1 - Suave(.12f, .22f, altura));
        }

        static float Suave(float minimo, float maximo, float valor) => Mathf.SmoothStep(0, 1, Mathf.InverseLerp(minimo, maximo, valor));
        static Vector2 Girar(Vector2 p, float angulo)
        {
            float c = Mathf.Cos(angulo), s = Mathf.Sin(angulo);
            return new Vector2(p.x * c - p.y * s, p.x * s + p.y * c);
        }

        void OnDestroy()
        {
            if (original) original.enabled = true;
            if (malha) Destroy(malha);
            if (material) Destroy(material);
        }
    }
}
