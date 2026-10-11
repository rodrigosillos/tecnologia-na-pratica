using UnityEngine;
namespace TecnologiaNaPratica
{
    public sealed class PaisagemRuinas : MonoBehaviour
    {
        public Sprite fundo;
        Transform camada;
        void Start()
        {
            camada=new GameObject("Panorama em paralaxe").transform;
            camada.SetParent(transform,false);
            float altura=25*fundo.bounds.size.y/fundo.bounds.size.x;
            for(int i=-1;i<6;i++)
                BancoArte.Desenhar("Vale distante",fundo,camada,new Vector2(i*25+12.5f,1.9f),new Vector2(25.02f,altura),-40);
        }
        void LateUpdate()
        {
            if(camada && Camera.main)
                camada.localPosition=new Vector3(Camera.main.transform.position.x*.65f,0,0);
        }
    }
}
