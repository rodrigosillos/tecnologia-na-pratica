using UnityEngine;
using UnityEngine.InputSystem;

namespace TecnologiaNaPratica.QuebraBlocos
{
    // Marco do capítulo 5: sem estados, vidas ou pontuação.
    [RequireComponent(typeof(Rigidbody2D))]
    public sealed class RaqueteBasica : MonoBehaviour
    {
        [SerializeField, Min(0)] float velocidade = 11f;
        [SerializeField, Min(0)] float limiteCentro = 6.3f;
        Rigidbody2D corpo;
        InputAction mover;
        float direcao;

        void Awake()
        {
            corpo = GetComponent<Rigidbody2D>();
            mover = new InputAction("Mover", InputActionType.Value);
            mover.AddCompositeBinding("1DAxis")
                .With("Negative", "<Keyboard>/a")
                .With("Positive", "<Keyboard>/d");
            mover.AddCompositeBinding("1DAxis")
                .With("Negative", "<Keyboard>/leftArrow")
                .With("Positive", "<Keyboard>/rightArrow");
        }
        void OnEnable() { mover.Enable(); }
        void Update() { direcao = mover.ReadValue<float>(); }
        void FixedUpdate()
        {
            float x = corpo.position.x;
            x += direcao * velocidade * Time.fixedDeltaTime;
            x = Mathf.Clamp(x, -limiteCentro, limiteCentro);
            corpo.MovePosition(new Vector2(x, corpo.position.y));
        }
        void OnDisable() { mover.Disable(); direcao = 0f; }
        void OnDestroy() { mover.Dispose(); }
    }
}
