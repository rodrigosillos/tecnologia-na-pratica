using UnityEngine;

namespace TecnologiaNaPratica.QuebraBlocos
{
    [RequireComponent(typeof(Rigidbody2D), typeof(CircleCollider2D))]
    public sealed class Bola : MonoBehaviour
    {
        [SerializeField] Raquete raquete;
        [SerializeField] ControlePartida controle;
        [SerializeField] float velocidadeInicial = 7f;
        [SerializeField] float velocidadeMaxima = 11f;
        Rigidbody2D corpo;
        TrailRenderer rastro;
        Material materialRastro;
        float velocidade;
        public Rigidbody2D Corpo => corpo;

        void Awake()
        {
            corpo = GetComponent<Rigidbody2D>();
            velocidade = velocidadeInicial;
            rastro = gameObject.AddComponent<TrailRenderer>();
            materialRastro = new Material(Shader.Find("Sprites/Default"));
            rastro.sharedMaterial = materialRastro;
            rastro.time = .14f;
            rastro.startWidth = .14f; rastro.endWidth = 0;
            rastro.startColor = new Color(.3f, .9f, 1f, .7f);
            rastro.endColor = new Color(.3f, .9f, 1f, 0);
            rastro.minVertexDistance = .035f;
            rastro.sortingOrder = 4;
            rastro.emitting = false;
        }
        void LateUpdate()
        {
            if (controle.Regras.Estado == EstadoPartida.Preparando)
                transform.position = raquete.transform.position + Vector3.up * 0.6f;
        }
        void FixedUpdate()
        {
            if (controle.Regras.Estado != EstadoPartida.Jogando) return;
            Vector2 v = corpo.linearVelocity;
            if (v.sqrMagnitude < 0.01f) v = Vector2.up;
            v.Normalize();
            if (Mathf.Abs(v.y) < 0.28f)
            {
                float sinalY = v.y < 0 ? -1f : 1f;
                v = new Vector2(Mathf.Sign(v.x) * Mathf.Sqrt(1f - 0.28f * 0.28f), sinalY * 0.28f);
            }
            corpo.linearVelocity = v * velocidade;
            if (corpo.position.y < -5.35f) controle.PerderBola();
        }
        public void Preparar(int fase)
        {
            rastro.emitting = false; rastro.Clear();
            corpo.simulated = false;
            corpo.linearVelocity = Vector2.zero;
            velocidade = Mathf.Min(velocidadeInicial + fase * 0.9f, velocidadeMaxima);
            corpo.position = (Vector2)raquete.transform.position + Vector2.up * 0.6f;
        }
        public void Lancar()
        {
            rastro.Clear(); rastro.emitting = true;
            corpo.position = (Vector2)raquete.transform.position + Vector2.up * 0.6f;
            corpo.simulated = true;
            corpo.linearVelocity = new Vector2(0.23f, 1f).normalized * velocidade;
        }
        public void Parar()
        {
            corpo.linearVelocity = Vector2.zero; corpo.simulated = false;
            rastro.emitting = false; rastro.Clear();
        }
        void OnDestroy() { if (materialRastro != null) Destroy(materialRastro); }
        void OnCollisionEnter2D(Collision2D colisao)
        {
            if (controle.Regras.Estado != EstadoPartida.Jogando) return;
            if (colisao.collider.TryGetComponent<Raquete>(out var alvo))
            {
                float desvio = Mathf.Clamp((corpo.position.x - alvo.transform.position.x) / 1.1f, -1f, 1f);
                corpo.linearVelocity = new Vector2(desvio * 0.85f, 1f).normalized * velocidade;
                controle.Som.Toque(420, 0.055f);
            }
            else if (colisao.collider.TryGetComponent<Bloco>(out var bloco))
                bloco.ReceberImpacto();
            else controle.Som.Toque(270, 0.025f);
        }
    }
}
