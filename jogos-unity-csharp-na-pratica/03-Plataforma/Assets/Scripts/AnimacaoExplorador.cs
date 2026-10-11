using UnityEngine;

namespace TecnologiaNaPratica
{
    public sealed class AnimacaoExplorador : MonoBehaviour
    {
        public MotorPlataforma motor;
        public SpriteRenderer visual;
        public string Estado { get; private set; } = "Parado";

        void LateUpdate()
        {
            int quadro = 0;
            if (!motor.NoChao)
            {
                Estado = motor.Corpo.linearVelocity.y > 0 ? "Subindo" : "Caindo";
                quadro = 3;
            }
            else if (Mathf.Abs(motor.Corpo.linearVelocity.x) > .2f)
            {
                Estado = "Correndo";
                quadro = 0;
            }
            else
                Estado = "Parado";
            if (Time.time < motor.TravadoAte)
                Estado = "Ferido";
            visual.sprite = BancoArte.Atual.atores[quadro];
            visual.flipX = motor.Direcao < 0;
            visual.transform.localScale = Vector3.one * (1.4f / visual.sprite.bounds.size.y);
            visual.color = Time.time < motor.Saude.ProtegidoAte && !motor.controle.EfeitosReduzidos ? new Color(1, .7f, .4f) : Color.white;
            CicloPassos.Aplicar(visual, Estado == "Correndo", Mathf.Abs(motor.Corpo.linearVelocity.x));
        }
    }
}
