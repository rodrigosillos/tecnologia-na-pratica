using UnityEngine;

namespace TecnologiaNaPratica
{
    public sealed class CameraAventura : MonoBehaviour
    {
        public MotorPlataforma alvo;
        public float larguraFase = 80;
        Vector3 velocidade;
        public void Enquadrar()
        {
            velocidade = Vector3.zero;
            transform.position = Destino();
        }

        Vector3 Destino()
        {
            float meia = GetComponent<Camera>().orthographicSize * GetComponent<Camera>().aspect;
            Vector2 posicao = alvo.Corpo.position;
            float x = Mathf.Clamp(posicao.x + alvo.Direcao * 2.2f, meia, larguraFase - meia);
            return new Vector3(x, Mathf.Clamp(posicao.y + .8f, .6f, 3.1f), -10);
        }

        void LateUpdate()
        {
            if (alvo)
                transform.position = Vector3.SmoothDamp(transform.position, Destino(), ref velocidade, .18f, 100, Time.deltaTime);
        }
    }
}
