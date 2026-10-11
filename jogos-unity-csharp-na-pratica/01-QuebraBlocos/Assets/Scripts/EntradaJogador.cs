using UnityEngine;
using UnityEngine.InputSystem;

namespace TecnologiaNaPratica.QuebraBlocos
{
    public sealed class EntradaJogador : MonoBehaviour
    {
        InputAction mover, lancar, pausar;
        public float Direcao => mover.ReadValue<float>();
        public bool Lancou => lancar.WasPressedThisFrame();
        public bool Pausou => pausar.WasPressedThisFrame();

        void Awake()
        {
            mover = new InputAction("Mover", InputActionType.Value);
            mover.AddCompositeBinding("1DAxis")
                .With("Negative", "<Keyboard>/a")
                .With("Positive", "<Keyboard>/d");
            mover.AddCompositeBinding("1DAxis")
                .With("Negative", "<Keyboard>/leftArrow")
                .With("Positive", "<Keyboard>/rightArrow");
            lancar = new InputAction("Lancar", InputActionType.Button, "<Keyboard>/space");
            pausar = new InputAction("Pausar", InputActionType.Button, "<Keyboard>/escape");
        }
        void OnEnable() { mover.Enable(); lancar.Enable(); pausar.Enable(); }
        void OnDisable() { mover.Disable(); lancar.Disable(); pausar.Disable(); }
        void OnDestroy() { mover.Dispose(); lancar.Dispose(); pausar.Dispose(); }
    }
}
