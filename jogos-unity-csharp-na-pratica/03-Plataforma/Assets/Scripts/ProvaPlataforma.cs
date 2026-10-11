using System;
using System.Collections;
using System.IO;
using UnityEngine;
using UnityEngine.InputSystem;
namespace TecnologiaNaPratica
{
    public sealed class ProvaPlataforma : ProvaExecutavelBase
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]static void Ativar()
        {if(FindFirstObjectByType<ProvaPlataforma>())return;var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,"--tnp-verificar");if(i>=0 && i+1<a.Length)new GameObject("Prova executavel").AddComponent<ProvaPlataforma>().Configurar(a[i+1]);}
        protected override void Preparar(){Campanha.PastaTeste=Path.Combine(pasta,"save-isolado");}
        protected override IEnumerator Roteiro()
        {
            yield return null;var c=FindFirstObjectByType<Campanha>();Conferir(c.Estado==EstadoAventura.Menu,"Menu inicial");Capturar("menu.png");
            Campanha.Sessao=new DadosProgresso();c.PrepararFase();yield return new WaitForSeconds(.35f);
            Capturar("diagnostico-solo.png");
            Conferir(c.Jogador.NoChao,"Personagem assenta no Tilemap com Composite Collider; pos="+c.Jogador.Corpo.position+" vel="+c.Jogador.Corpo.linearVelocity+" gravity="+Physics2D.gravity+" paths="+FindFirstObjectByType<CompositeCollider2D>().pathCount);Capturar("fase1.png");
            yield return null;yield return null;Teclas(Key.D);yield return null;yield return null;
            float inicial=c.Jogador.Corpo.position.x;
            for(int passo=0;passo<25;passo++)yield return new WaitForFixedUpdate();
            Teclas();yield return null;yield return null;yield return new WaitForSeconds(.2f);
            Capturar("diagnostico-movimento.png");
            Conferir(c.Jogador.Corpo.position.x>inicial+2.1f && Mathf.Abs(c.Jogador.Corpo.linearVelocity.x)<.1f,"Aceleração e freio por teclado; inicio="+inicial+" fim="+c.Jogador.Corpo.position+" vel="+c.Jogador.Corpo.linearVelocity+" estado="+c.Estado+" escala="+Time.timeScale);
            yield return null;yield return null;
            float y=c.Jogador.Corpo.position.y;Teclas(Key.Space);yield return null;yield return null;
            for(int passo=0;passo<10;passo++)yield return new WaitForFixedUpdate();
            Conferir(c.Jogador.Corpo.position.y>y+1.3f,"Salto físico por Espaço");Teclas();yield return new WaitForSeconds(.8f);
            Conferir(c.Jogador.NoChao,"Aterrissagem após salto variável");
            c.Jogador.Reposicionar(new Vector2(24,-.3f));yield return new WaitForSeconds(.2f);Teclas(Key.Space);yield return new WaitForSeconds(.8f);Teclas();yield return new WaitForSeconds(.15f);
            Conferir(c.Jogador.NoChao && c.Jogador.Corpo.position.y>1.6f,"Salto atravessa a plataforma por baixo e aterrissa por cima");Capturar("plataforma-passagem.png");
            c.Jogador.Reposicionar(new Vector2(5,-.3f));yield return new WaitForSeconds(.2f);Teclas(Key.J);yield return new WaitForSeconds(.15f);Teclas();yield return null;
            Conferir(c.Projeteis.Ativos>0,"Disparo horizontal por J");
            c.Checkpoint(1);c.Jogador.Corpo.position=new Vector2(18,-7);yield return new WaitForSeconds(.9f);
            Conferir(c.Jogador.Corpo.position.x>27 && c.Jogador.Corpo.position.x<29 && c.Jogador.Saude.Atual==5,"Queda retorna ao checkpoint com vida restaurada");
            Conferir(c.Repositorio.Carregar().checkpoint==1 && Campanha.Sessao.mortes==1,"Checkpoint e morte persistem no arquivo isolado");
            Teclas(Key.Escape);yield return null;yield return null;Teclas();yield return null;var pos=c.Jogador.Corpo.position;yield return new WaitForSecondsRealtime(.2f);
            Conferir(c.Estado==EstadoAventura.Pausa && c.Jogador.Corpo.position==pos,"Pausa congela o personagem");Capturar("pausa.png");c.AlternarPausa();
            c.SairDaFase();yield return null;yield return null;c=FindFirstObjectByType<Campanha>();yield return new WaitForSeconds(.2f);
            Conferir(c.indice==1 && Campanha.Sessao.checkpoint==0,"Portal carrega a segunda cena e zera checkpoint");Capturar("fase2.png");
            var ponte=c.moveis[0];var antes=ponte.transform.position;yield return new WaitForSeconds(.4f);Conferir(Vector3.Distance(antes,ponte.transform.position)>.1f,"Plataforma móvel percorre a rota");
            c.SairDaFase();yield return null;yield return null;c=FindFirstObjectByType<Campanha>();yield return new WaitForSeconds(.2f);
            Conferir(c.indice==2,"Terceira cena carregada");c.SairDaFase();Conferir(c.Jogando,"Guardião bloqueia a saída enquanto está ativo");
            c.Jogador.Reposicionar(new Vector2(65,-.3f));Camera.main.GetComponent<CameraAventura>().Enquadrar();yield return new WaitForSeconds(.12f);yield return null;Capturar("guardiao.png");
            foreach(var e in c.inimigos)if(e.Chefe)e.Saude.ReceberDano(100,Vector2.zero);c.SairDaFase();yield return null;
            Conferir(c.Estado==EstadoAventura.Vitoria && c.Repositorio.Carregar().concluido,"Guardião desativado por dano controlado libera a vitória salva");Capturar("vitoria.png");
            c.NovaPartida();yield return null;yield return null;
            float saltoAte=0,proximoSalto=0,inicioPercurso=Time.realtimeSinceStartup;
            while(!Campanha.Sessao.concluido)
            {
                c=FindFirstObjectByType<Campanha>();
                if(c && c.Jogando)
                {
                    Vector2 p=c.Jogador.Corpo.position;
                    bool guardaVivo=false;
                    foreach(var e in c.inimigos)if(e.Chefe && e.gameObject.activeSelf)guardaVivo=true;
                    bool parar=c.indice==2 && guardaVivo && p.x>67;
                    bool perigo=false;
                    foreach(var contato in c.contatos)
                        if(contato.tipo==TipoContato.Espinhos && contato.transform.position.x-p.x>-.6f && contato.transform.position.x-p.x<1.9f)perigo=true;
                    bool borda=!Physics2D.Raycast(p+new Vector2(.95f,-.45f),Vector2.down,.55f,1<<10);
                    if(c.Jogador.NoChao && Time.time>=proximoSalto && (borda||perigo||parar))
                    {saltoAte=Time.time+.44f;proximoSalto=Time.time+.65f;}
                    if(Time.time<saltoAte)Teclas(parar?new[]{Key.J,Key.Space}:new[]{Key.D,Key.J,Key.Space});
                    else Teclas(parar?new[]{Key.J}:new[]{Key.D,Key.J});
                }
                else Teclas();
                ConferirPercurso(Campanha.Sessao.mortes<=8 && Time.realtimeSinceStartup-inicioPercurso<100,c);
                yield return null;
            }
            Teclas();
            Conferir(Campanha.Sessao.concluido,"Travessia automatizada integral das três fases por teclado, sem teletransporte nem dano forçado");
        }
        void ConferirPercurso(bool ok,Campanha c)
        {if(!ok)throw new InvalidOperationException("Percurso por teclado não concluiu: fase="+Campanha.Sessao.fase+" mortes="+Campanha.Sessao.mortes+" pos="+(c?c.Jogador.Corpo.position.ToString():"transicao"));}
    }
}
