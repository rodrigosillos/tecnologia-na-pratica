using UnityEngine;
using UnityEngine.Tilemaps;
namespace TecnologiaNaPratica
{
    [RequireComponent(typeof(Tilemap),typeof(TilemapCollider2D),typeof(CompositeCollider2D))]
    public sealed class TerrenoFisico : MonoBehaviour
    {
        void Awake()
        {
            var mapa=GetComponent<Tilemap>();mapa.RefreshAllTiles();
            GetComponent<TilemapCollider2D>().ProcessTilemapChanges();
            GetComponent<CompositeCollider2D>().GenerateGeometry();
        }
    }
}
