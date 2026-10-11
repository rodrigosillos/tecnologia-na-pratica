using System.Collections.Generic;
using UnityEngine;
using Unity.Profiling;
namespace TecnologiaNaPratica
{
    public sealed class ReservaProjeteis : MonoBehaviour
    {
        public Projetil prefab;
        readonly List<Projetil> todos=new List<Projetil>();
        static readonly ProfilerMarker marcador=new ProfilerMarker("TNP.Arena.Disparar");
        public int Criados=>todos.Count;
        public int Ativos {get{int n=0;foreach(var p in todos)if(p.gameObject.activeSelf)n++;return n;}}
        public void Aquecer(int quantidade){while(todos.Count<quantidade)Criar();}
        Projetil Criar(){var p=Instantiate(prefab,transform);p.gameObject.SetActive(false);todos.Add(p);return p;}
        public bool Disparar(Vector2 origem,Vector2 direcao,int dano,bool hostil)
        {
            using(marcador.Auto())
            {
                Projetil livre=null;
                foreach(var p in todos)if(!p.gameObject.activeSelf){livre=p;break;}
                if(livre==null){if(todos.Count>=80)return false;livre=Criar();}
                livre.Ativar(origem,direcao,dano,hostil);return true;
            }
        }
        public void Limpar(){foreach(var p in todos)p.gameObject.SetActive(false);}
    }
}
