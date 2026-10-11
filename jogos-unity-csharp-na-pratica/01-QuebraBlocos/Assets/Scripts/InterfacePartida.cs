using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

namespace TecnologiaNaPratica.QuebraBlocos
{
    public sealed class InterfacePartida : MonoBehaviour
    {
        [SerializeField] ControlePartida controle;
        [SerializeField] Text placar, instrucao, tituloMenu, resumoMenu;
        [SerializeField] GameObject painelMenu;
        [SerializeField] Button jogar, continuar, menu, sair;
        [SerializeField] Slider volume;
        bool inscrito;
        void Start()
        {
            jogar.onClick.AddListener(controle.Iniciar);
            continuar.onClick.AddListener(controle.Pausar);
            menu.onClick.AddListener(controle.VoltarAoMenu);
            sair.onClick.AddListener(controle.Sair);
            volume.SetValueWithoutNotify(controle.Som.Volume);
            volume.onValueChanged.AddListener(controle.Som.DefinirVolume);
            controle.Regras.Mudou += Atualizar;
            inscrito = true;
            Atualizar();
        }
        void Atualizar()
        {
            var r = controle.Regras;
            placar.gameObject.SetActive(r.Estado != EstadoPartida.Menu);
            placar.text = $"RUÍNAS EM JOGO     FASE {r.Fase + 1}/3       VIDAS {r.Vidas}       PONTOS {r.Pontos}";
            instrucao.text = r.Estado == EstadoPartida.Preparando
                ? "A / D ou setas para mover  ·  ESPAÇO para lançar  ·  ESC para pausar"
                : r.Estado == EstadoPartida.Jogando ? "ESC para pausar" : "";
            bool aberto = r.Estado == EstadoPartida.Menu || r.Estado == EstadoPartida.Pausado
                || r.Estado == EstadoPartida.Vitoria || r.Estado == EstadoPartida.Derrota;
            painelMenu.SetActive(aberto);
            if (!aberto) { EventSystem.current?.SetSelectedGameObject(null); return; }
            tituloMenu.text = r.Estado == EstadoPartida.Vitoria ? "RUÍNAS RESTAURADAS"
                : r.Estado == EstadoPartida.Derrota ? "UMA NOVA TENTATIVA"
                : r.Estado == EstadoPartida.Pausado ? "PAUSA" : "RUÍNAS EM JOGO";
            resumoMenu.text = r.Estado == EstadoPartida.Menu
                ? "Rebata a esfera e desfaça as muralhas de três pátios.\n\nMova com A / D ou setas. Lance com ESPAÇO.\nESC pausa a partida. Use o mouse ou setas e ENTER nos menus.\n\nTecnologia na Prática · Rodrigo Sillos\nCódigo, arte gerada por IA e áudio sintetizado do laboratório."
                : $"{controle.NomeFase}\nPontos: {r.Pontos}  ·  Recorde: {Mathf.Max(controle.Recorde, r.Pontos)}\n\nO próximo passo depende de você.";
            continuar.gameObject.SetActive(r.Estado == EstadoPartida.Pausado);
            menu.gameObject.SetActive(r.Estado != EstadoPartida.Menu);
            jogar.GetComponentInChildren<Text>().text = r.Estado == EstadoPartida.Menu ? "INICIAR PARTIDA" : "NOVA PARTIDA";
            Posicionar(jogar, r.Estado == EstadoPartida.Menu ? 0 : r.Estado == EstadoPartida.Pausado ? 165 : -165, -44);
            Posicionar(continuar, -165, -44);
            Posicionar(menu, r.Estado == EstadoPartida.Pausado ? -165 : 165, r.Estado == EstadoPartida.Pausado ? -100 : -44);
            Posicionar(sair, r.Estado == EstadoPartida.Pausado ? 165 : 0, -100);
            (r.Estado == EstadoPartida.Pausado ? continuar : jogar).Select();
        }
        static void Posicionar(Button botao, float x, float y)
        {
            ((RectTransform)botao.transform).anchoredPosition = new Vector2(x, y);
        }
        void OnDestroy()
        {
            if (inscrito && controle != null) controle.Regras.Mudou -= Atualizar;
        }
    }
}
