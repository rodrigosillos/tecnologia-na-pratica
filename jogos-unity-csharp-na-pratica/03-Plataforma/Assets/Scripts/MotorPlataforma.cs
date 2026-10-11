using UnityEngine;
using UnityEngine.InputSystem;

namespace TecnologiaNaPratica
{
    [RequireComponent(typeof(Rigidbody2D), typeof(Vida))]
    public sealed class MotorPlataforma : MonoBehaviour
    {
        public Campanha controle;
        public float velocidade = 6, aceleracao = 45, freio = 60, impulso = 11.8f;
        public Rigidbody2D Corpo { get; private set; }
        public Vida Saude { get; private set; }
        public bool NoChao { get; private set; }
        public int Direcao { get; private set; } = 1;
        public Vector2 Movimento { get; private set; }
        public float TravadoAte { get; private set; }

        public readonly JanelaSalto Salto = new JanelaSalto();
        Entrada entrada;
        float dispararAte;
        void Awake()
        {
            Corpo = GetComponent<Rigidbody2D>();
            Saude = GetComponent<Vida>();
            entrada = new Entrada();
        }

        void OnEnable()
        {
            GetComponent<Vida>().Ferido += Ferido;
            GetComponent<Vida>().Morreu += Morreu;
        }

        void OnDisable()
        {
            Saude.Ferido -= Ferido;
            Saude.Morreu -= Morreu;
        }

        void OnDestroy()
        {
            entrada?.Dispose();
        }

        public void Reposicionar(Vector2 ponto)
        {
            Corpo.simulated = true;
            Corpo.position = ponto;
            Corpo.linearVelocity = Vector2.zero;
            Movimento = Vector2.zero;
            Salto.Limpar();
            TravadoAte = 0;
            dispararAte = 0;
            Saude.Restaurar(5);
            NoChao = false;
        }

        void Update()
        {
            if (entrada.Pausa)
                controle.AlternarPausa();
            if (!controle.Jogando)
            {
                Movimento = Vector2.zero;
                return;
            }

            Movimento = entrada.Movimento;
            if (Mathf.Abs(Movimento.x) > .1f)
                Direcao = Movimento.x > 0 ? 1 : -1;
            if (entrada.PuloPressionado)
                Salto.Pedir(Time.time);
            if (entrada.PuloSolto && Corpo.linearVelocity.y > 0)
                Corpo.linearVelocity = new Vector2(Corpo.linearVelocity.x, Corpo.linearVelocity.y * .45f);
            bool atirar = entrada.Atirando || (Keyboard.current != null && Keyboard.current.jKey.isPressed);
            if (atirar && Time.time >= dispararAte)
            {
                controle.Projeteis.Disparar(Corpo.position + new Vector2(Direcao * .6f, .08f), Vector2.right * Direcao, 1, false);
                dispararAte = Time.time + .30f;
                controle.Som.Tocar(660);
            }

            if (Corpo.position.y < -6)
                controle.Morrer();
        }

        void FixedUpdate()
        {
            if (!controle.Jogando)
                return;
            var hit = Physics2D.BoxCast(Corpo.position + Vector2.down * .54f, new Vector2(.48f, .08f), 0, Vector2.down, .13f, 1 << 10);
            NoChao = hit.collider && Corpo.linearVelocity.y <= .1f;
            if (NoChao)
                Salto.RegistrarSolo(Time.time);
            if (Time.time < TravadoAte)
                return;
            float carregar = 0;
            if (NoChao && hit.collider.TryGetComponent<PlataformaMovel>(out var plataforma))
                carregar = plataforma.Velocidade.x;
            var v = Corpo.linearVelocity;
            v.x = Mathf.MoveTowards(v.x, Movimento.x * velocidade + carregar, (Mathf.Abs(Movimento.x) > .1f ? aceleracao : freio) * Time.fixedDeltaTime);
            v.y = Mathf.Max(v.y, -18);
            if (Salto.Consumir(Time.time))
            {
                v.y = impulso;
                NoChao = false;
                controle.Som.Tocar(480);
            }

            Corpo.linearVelocity = v;
        }

        void Ferido(Vector2 origem)
        {
            Salto.Limpar();
            TravadoAte = Time.time + .20f;
            float lado = Corpo.position.x >= origem.x ? 1 : -1;
            Corpo.linearVelocity = new Vector2(lado * 5, 6);
            controle.Som.Tocar(150);
        }

        void Morreu()
        {
            controle.Morrer();
        }
    }
}
