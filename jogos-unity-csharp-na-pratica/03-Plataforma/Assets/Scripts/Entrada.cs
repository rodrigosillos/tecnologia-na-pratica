using System;
using UnityEngine;
using UnityEngine.InputSystem;

namespace TecnologiaNaPratica
{
    public sealed class Entrada : IDisposable
    {
        readonly InputAction mover = new InputAction("Mover", InputActionType.Value);
        readonly InputAction pular = new InputAction("Pular", binding: "<Keyboard>/space");
        readonly InputAction pausar = new InputAction("Pausar", binding: "<Keyboard>/escape");
        readonly InputAction disparar = new InputAction("Disparar", binding: "<Mouse>/leftButton");
        public Entrada()
        {
            mover.AddCompositeBinding("2DVector").With("Up", "<Keyboard>/w").With("Down", "<Keyboard>/s").With("Left", "<Keyboard>/a").With("Right", "<Keyboard>/d");
            mover.AddCompositeBinding("2DVector").With("Up", "<Keyboard>/upArrow").With("Down", "<Keyboard>/downArrow").With("Left", "<Keyboard>/leftArrow").With("Right", "<Keyboard>/rightArrow");
            pular.AddBinding("<Keyboard>/upArrow");
            mover.Enable();
            pular.Enable();
            pausar.Enable();
            disparar.Enable();
        }

        public Vector2 Movimento => Vector2.ClampMagnitude(mover.ReadValue<Vector2>(), 1);
        public bool PuloPressionado => pular.WasPressedThisFrame();
        public bool PuloSolto => pular.WasReleasedThisFrame();
        public bool Pausa => pausar.WasPressedThisFrame();
        public bool Atirando => disparar.IsPressed();
        public Vector2 Mira => Mouse.current == null ? Vector2.right : (Vector2)Camera.main.ScreenToWorldPoint(Mouse.current.position.ReadValue());

        public void Dispose()
        {
            mover.Dispose();
            pular.Dispose();
            pausar.Dispose();
            disparar.Dispose();
        }
    }
}
