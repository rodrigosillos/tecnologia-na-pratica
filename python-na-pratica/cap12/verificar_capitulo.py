"""Projeto final: integração local reproduzível; banco nativo com --com-banco."""
import argparse
from contextlib import redirect_stdout
from copy import deepcopy
from datetime import date,datetime,timezone
from decimal import Decimal
from importlib.metadata import version
import io,json,hashlib,os,platform,subprocess,sys,tempfile
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4
import httpx2
import psycopg
from psycopg import sql
from openai.types.responses import Response
import app,aplicacao,banco,exportacao,ia_real
from arquivos import ler_entrada,json_bytes
from assistencia import pacote_sintetico,lote_revisado,preparar_sugestoes,revisar_sugestoes,consulta_sintetica
from extracao.arquivos import ler_json,resumo,gravar_conjunto
from extracao import fluxo as ef,contexto as ec
from extracao.configuracao_ia import PASTA as PE,MODELO
from extracao.cliente_ia import criar_cliente
from consulta import fluxo as cf
from consulta.configuracao_ia import PASTA as PC
from consulta.documentos import carregar_corpus
from recibos import criar_retrato,conferir_recibo
from proveniencia import conferir_vinculo
from regras import validar_lote
from custos import novo_controle,reservar,concluir,retrato
from conexao import conectar,configuracao_banco
from servidor_catalogo import criar_servidor
from solucao_desafio import destacar

BASE=Path(__file__).resolve().parent
CASOS=[];EXECUCOES=[];CATS=['Alimentação','Transporte','Materiais']

def exigir(v):
    if not v:raise AssertionError('Resultado diferente do esperado')

def erro(tipo,f):
    try:f()
    except tipo:return
    raise AssertionError('Erro esperado não ocorreu')

def caso(nome,f):
    try:f();CASOS.append({'nome':nome,'status':'aprovado'})
    except Exception as e:CASOS.append({'nome':nome,'status':'reprovado','tipo':type(e).__name__})

def silencioso(f):
    with redirect_stdout(io.StringIO()):return f()

def revisao_padrao():return ler_json(PE/'revisoes/decisoes_exemplo.json')

def recibo_local():
    p=pacote_sintetico();r=revisao_padrao();lote,h,origem=lote_revisado(p,r)
    base,_=ler_entrada(BASE/'dados/validas.json')
    ds=validar_lote(base+lote,CATS)['despesas']
    linhas=[(d['id'],d['data'],d['descricao'],d['categoria'],d['valor']) for d in ds]
    return {'execucao':'final-b','entrada_sha256':h,'novas':2,'existentes':0,
            'retrato':criar_retrato(linhas),'proveniencia':origem}

def cli(nome,args,codigo,trecho):
    env=os.environ.copy();env.pop('OPENAI_API_KEY',None);env.pop('PYTHON_PRATICA_IA_MAX_SAIDA',None);env['PYTHONIOENCODING']='utf-8'
    r=subprocess.run([sys.executable,str(BASE/nome),*args],cwd=BASE,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=30)
    EXECUCOES.append({'arquivo':nome,'argumentos':args,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    exigir(r.returncode==codigo and trecho in r.stdout+r.stderr)

def locais(raiz):
    caso('Python 3.14 em ambiente virtual',lambda:exigir(sys.version_info[:2]==(3,14) and sys.prefix!=sys.base_prefix))
    def deps():
        for l in (BASE/'requirements.txt').read_text().splitlines():
            if '==' in l:
                n,v=l.split('==');exigir(version(n)==v)
    caso('Dependências fixadas',deps)
    manifesto=ler_json(BASE/'MANIFESTO_SHA256.json')
    caso('Hashes técnicos atuais',lambda:exigir(all(hashlib.sha256((BASE/f).read_bytes()).hexdigest()==h for f,h in manifesto.items())))
    p=pacote_sintetico();r=revisao_padrao();analises=ef.conferir_pacote(p)
    caso('Reprodução explicitamente sintética',lambda:exigir(p['modo']=='reproducao' and p['origem']=='sintetica'))
    caso('T001 data ausente permanece pendente',lambda:exigir(analises['T001']['sugestao']['data'] is None and 'data' in analises['T001']['pendencias']))
    caso('T002 usa total pago 18.50',lambda:exigir(analises['T002']['sugestao']['valor']=='18.50'))
    caso('T003 categoria ausente',lambda:exigir('categoria' in analises['T003']['pendencias']))
    lote,h,origem=lote_revisado(p,r)
    caso('Revisão libera dois IDs e soma 53.50',lambda:exigir([x['id'] for x in lote]==['D101','D102'] and origem['trilha']['total_lote_revisado']=='53.50'))
    caso('D103 rejeitado sem valor no lote',lambda:exigir(origem['trilha']['rejeitados']==1 and 'D103' not in [x['id'] for x in lote]))
    caso('Trilha preserva null, correção e complemento',lambda:exigir(origem['trilha']['decisoes'][0]['original']['data'] is None and origem['trilha']['decisoes'][0]['final']['data']=='2026-09-11' and origem['trilha']['decisoes'][0]['complemento']['id']=='mensagem_T001'))
    caso('Modelo pendente bloqueia lote',lambda:erro(ValueError,lambda:lote_revisado(p,ef.modelo_revisao(p))))
    alteracoes=[('revisor vazio',lambda q:q.update(revisor='')),('hash diferente',lambda q:q.update(pacote_sha256='a'*64)),('decisão ausente',lambda q:q['decisoes'].pop()),('aceite de data ausente',lambda q:q['decisoes'][0].update(acao='aceitar',correcoes={},complemento=None)),('origem repetida',lambda q:q['decisoes'][1].update(origem_id='T001')),('complemento errado',lambda q:q['decisoes'][0].update(complemento='inexistente'))]
    for nome,mudar in alteracoes:
        rev=deepcopy(r);mudar(rev)
        caso('Revisão bloqueada: '+nome,lambda rev=rev:erro(ValueError,lambda:lote_revisado(p,rev)))
    for c in ['incompleta','recusa']:
        q=pacote_sintetico(c)
        caso('Sugestão bloqueada: '+c,lambda q=q:exigir(ef.conferir_pacote(q)['T002']['estado']=='bloqueada'))
        rev=deepcopy(r);rev['pacote_sha256']=resumo(q)
        caso('Aceite não promove falha: '+c,lambda q=q,rev=rev:erro(ValueError,lambda:lote_revisado(q,rev)))
    caso('Vínculo da revisão confere',lambda:conferir_vinculo(origem,h))
    trocada=deepcopy(origem);trocada['revisao']['revisor']='Outro nome'
    caso('Proveniência adulterada bloqueada',lambda:erro(ValueError,lambda:conferir_vinculo(trocada,h)))
    copia=raiz/'lote.json';copia.write_bytes(json_bytes(lote))
    caso('Importação simples não contorna IDs assistidos',lambda:erro(ValueError,lambda:aplicacao.preparar_entrada(SimpleNamespace(comando='importar',entrada=copia))))
    rb=recibo_local()
    caso('Total integrado cinco / 181.00',lambda:exigir(rb['retrato']['quantidade']==5 and rb['retrato']['total']=='181.00'))
    caso('Recibo inclui a revisão conferida',lambda:conferir_recibo(rb))
    invalid=deepcopy(rb);invalid['retrato']['total']='180.00'
    caso('Total divergente bloqueado',lambda:erro(ValueError,lambda:conferir_recibo(invalid)))
    arquivos=exportacao.renderizar(rb)
    caso('Cinco arquivos e proveniência explícita',lambda:exigir(set(arquivos)=={'despesas.csv','despesas.html','recibo.json','proveniencia.json','manifesto.json'}))
    destino=raiz/'relatorios'
    caso('Exportação integrada criada',lambda:exigir(exportacao.exportar(rb,destino)=='criada'))
    def repetir():
        antes={x.name:(x.read_bytes(),x.stat().st_mtime_ns) for x in (destino/'final-b').iterdir()}
        exigir(exportacao.exportar(rb,destino)=='reutilizada')
        exigir(antes=={x.name:(x.read_bytes(),x.stat().st_mtime_ns) for x in (destino/'final-b').iterdir()})
    caso('Reexportação mantém bytes e datas',repetir)
    def retomar():
        a=SimpleNamespace(comando='exportar',execucao='final-b',destino=raiz/'retomada')
        with patch.object(banco,'consultar_recibo',return_value=rb),patch.object(banco,'importar',side_effect=AssertionError),patch.object(aplicacao,'preparar_entrada',side_effect=AssertionError),patch.object(aplicacao,'obter_catalogo',side_effect=AssertionError),patch.object(ia_real,'chamar_modelo',side_effect=AssertionError):
            exigir(silencioso(lambda:aplicacao.executar(a,{},lambda *a,**k:None))==0)
    caso('Retomada não acessa revisão, catálogo, importação ou IA',retomar)
    def destino_alterado():
        x=destino/'final-b'/'proveniencia.json';x.write_bytes(b'preservar')
        erro(ValueError,lambda:exportacao.exportar(rb,destino));exigir(x.read_bytes()==b'preservar')
    caso('Arquivo divergente é preservado',destino_alterado)
    for pergunta,estado in [('P01','aguarda_revisao'),('P02','aguarda_revisao'),('P03','abstencao_proposta'),('P04','abstencao_local'),('P05','aguarda_revisao')]:
        q=cf.preparar_reproducao(pergunta)
        caso('RAG '+pergunta+' '+estado,lambda q=q,estado=estado:exigir(cf.conferir_pacote(q)['estado']==estado))
    q=cf.preparar_reproducao('P01')
    caso('P01 encontra POL-002 com sete pontos',lambda:exigir(q['recuperacao']['trechos'][0]['id']=='POL-002' and q['recuperacao']['trechos'][0]['pontos']==7))
    def corpus_alterado():
        corpus=deepcopy(carregar_corpus());corpus['sha256']='f'*64
        with patch('consulta.fluxo.carregar_corpus',return_value=corpus):
            erro(ValueError,lambda:cf.conferir_pacote(q))
    caso('Pacote RAG não aceita corpus diferente',corpus_alterado)
    def fonte_inventada():
        q2=deepcopy(q);out=q2['resposta']['output'][0]['content'][0];corpo=json.loads(out['text']);corpo['afirmacoes'][0]['fontes'][0]['trecho_id']='POL-999';out['text']=json.dumps(corpo)
        q2['pacote_sha256']=resumo({k:v for k,v in q2.items() if k!='pacote_sha256'})
        exigir(cf.conferir_pacote(q2)['estado']=='bloqueada')
    caso('Fonte inexistente bloqueada',fonte_inventada)
    def consulta_sem_banco():
        with patch.object(banco,'conectar',side_effect=AssertionError):
            exigir(silencioso(lambda:consulta_sintetica('P01',raiz/'rag-sem-banco'))==0)
    caso('Consulta documental não usa banco',consulta_sem_banco)
    # SDK real com transporte em memória: nenhuma requisição externa.
    base_resp=ler_json(PE/'casos/T002.json')['resposta']
    caso('Envelope sintético compatível com SDK',lambda:Response.model_validate(base_resp))
    for tipo in ['ok','incompleta','recusa','uso_ausente','modelo_divergente',401,429,500,'timeout']:
        def sdk(tipo=tipo):
            chamadas=[]
            def transporte(req):
                chamadas.append(json.loads(req.content))
                if tipo=='timeout':raise httpx2.ReadTimeout('nao_expor',request=req)
                if isinstance(tipo,int):return httpx2.Response(tipo,json={'error':{'message':'nao_expor','type':'invalid_request_error','code':'teste'}})
                rr=deepcopy(base_resp);rr['id']='resp_teste_transporte';rr['output'][0]['id']='msg_teste'
                if tipo in ['incompleta','recusa']:
                    alvo='resposta_incompleta' if tipo=='incompleta' else 'recusa'
                    rr=deepcopy(next(x['resposta'] for x in ler_json(PE/'casos/erros.json') if x['nome']==alvo));rr['id']='resp_teste_transporte'
                if tipo=='uso_ausente':rr['usage']=None
                if tipo=='modelo_divergente':rr['model']='outro'
                return httpx2.Response(200,json=rr)
            def fabrica(k):return criar_cliente(k,http_client=httpx2.Client(transport=httpx2.MockTransport(transporte)))
            dest=raiz/('sdk-'+str(tipo))
            with patch.object(ia_real,'obter_chave',return_value='credencial-ficticia-de-teste'):
                saida=io.StringIO()
                with redirect_stdout(saida):codigo=ia_real.executar_real('extracao','T002',dest,True,fabrica_cliente=fabrica)
            meta=ler_json(dest/'metadados.json')
            exigir(len(chamadas)==1 and meta['tentativas_sdk']==1 and meta['max_retries']==0 and 'nao_expor' not in saida.getvalue())
            exigir(chamadas[0].get('tools',[])==[] and chamadas[0]['store'] is False)
            exigir(codigo==(0 if tipo=='ok' else 1))
            if tipo in ['uso_ausente','timeout',401,429,500]:exigir(meta['controle']['incerto'] is True and meta['controle']['reserva'] is not None)
            if tipo=='ok':exigir(ler_json(dest/'revisao_pendente.json')['decisoes'][0]['acao']=='pendente')
        caso('Extensão SDK com transporte simulado: '+str(tipo),sdk)
    def consulta_sdk():
        chamadas=[]
        def transporte(req):
            chamadas.append(json.loads(req.content))
            rr=deepcopy(ler_json(PC/'casos/P01.json')['resposta']);rr['id']='resp_consulta_teste'
            return httpx2.Response(200,json=rr)
        def fabrica(k):return criar_cliente(k,http_client=httpx2.Client(transport=httpx2.MockTransport(transporte)))
        pergunta=cf.preparar_reproducao('P01')['recuperacao']['pergunta']
        dest=raiz/'sdk-consulta'
        with patch.object(ia_real,'obter_chave',return_value='teste'),patch.object(banco,'conectar',side_effect=AssertionError):
            exigir(silencioso(lambda:ia_real.executar_real('consulta',pergunta,dest,True,fabrica_cliente=fabrica))==0)
        exigir(len(chamadas)==1 and chamadas[0].get('tools',[])==[])
        exigir(cf.conferir_pacote(ler_json(dest/'pacote.json'))['estado']=='aguarda_revisao')
        exigir(ler_json(dest/'metadados.json')['banco']=='nao_utilizado')
    caso('Consulta SDK simulada preserva fontes, revisão e isolamento do banco',consulta_sdk)
    def sem_chamada(tipo,entrada,conf,orcamento,esperado):
        dest=raiz/('guard-'+uuid4().hex)
        with patch.object(ia_real,'obter_chave',side_effect=ValueError),patch.object(ia_real,'chamar_modelo',side_effect=AssertionError):
            exigir(silencioso(lambda:ia_real.executar_real(tipo,entrada,dest,conf,orcamento))==esperado)
    caso('API sem confirmação não chama',lambda:sem_chamada('extracao','T002',False,'0.01',2))
    caso('API confirmada sem chave não chama',lambda:sem_chamada('extracao','T002',True,'0.01',1))
    caso('Orçamento zero bloqueia antes de chamar',lambda:sem_chamada('extracao','T002',True,'0',1))
    caso('Pergunta sem trechos abstém sem chave',lambda:sem_chamada('consulta','Quanto posso gastar com almoço?',True,'0.01',0))
    def salvar_falha():
        chamadas=[]
        def transporte(req):
            chamadas.append(1);rr=deepcopy(base_resp);rr['id']='resp_teste';return httpx2.Response(200,json=rr)
        def fabrica(k):return criar_cliente(k,http_client=httpx2.Client(transport=httpx2.MockTransport(transporte)))
        with patch.object(ia_real,'obter_chave',return_value='teste'),patch.object(ia_real,'gravar_conjunto',side_effect=OSError):
            exigir(silencioso(lambda:ia_real.executar_real('extracao','T002',raiz/'falha-salvar',True,fabrica_cliente=fabrica))==3)
        exigir(chamadas==[1])
    caso('Falha de arquivo após SDK não repete chamada',salvar_falha)
    def gasto_incerto():
        c=novo_controle(1,'0.01');reservar(c,1000,512);concluir(c,None)
        exigir(c['incerto'] and c['reserva'] is not None)
        erro(ValueError,lambda:reservar(c,100,32))
    caso('Uso ausente preserva reserva e impede repetição',gasto_incerto)
    dados,_=ler_entrada(BASE/'dados/validas.json');original=deepcopy(dados)
    caso('Desafio destaca somente D003 no lote inicial',lambda:exigir([x['id'] for x in destacar(dados) if x['destaque']]==['D003']))
    caso('Desafio não altera dados',lambda:exigir(dados==original))
    for valor,resultado in [('49.99',False),('50.00',True),('50.01',True)]:
        caso('Limite do destaque '+valor,lambda valor=valor,resultado=resultado:exigir(destacar([{'id':'D900','valor':valor}])[0]['destaque'] is resultado))
    # Roteiro CLI completo sem banco e sem chave.
    sug=raiz/'cli-sug';rev=raiz/'cli-rev'
    etapas=[('app.py',['--help'],0,'importar-revisado'),
      ('app.py',['sugerir','--destino',str(sug)],0,'sintetica'),
      ('app.py',['inspecionar','--pacote',str(sug/'pacote.json')],0,'T001'),
      ('app.py',['revisar','--pacote',str(sug/'pacote.json'),'--revisao',str(sug/'revisao_pendente.json'),'--destino',str(rev)],1,'bloqueada'),
      ('app.py',['revisar','--pacote',str(sug/'pacote.json'),'--revisao',str(PE/'revisoes/decisoes_exemplo.json'),'--destino',str(rev)],0,'53.50'),
      ('app.py',['sugerir','--destino',str(sug)],1,'bloqueada'),
      ('app.py',['sugerir','--cenario','incompleta','--destino',str(raiz/'cli-falha')],1,'bloqueada'),
      ('app.py',['consultar','--caso','P01','--destino',str(raiz/'cli-p01')],0,'aguarda_revisao'),
      ('app.py',['consultar','--caso','P03','--destino',str(raiz/'cli-p03')],0,'abstencao_proposta'),
      ('app.py',['consultar','--caso','P04','--destino',str(raiz/'cli-p04')],0,'abstencao_local'),
      ('app.py',['extrair-real','--origem','T002','--destino',str(raiz/'cli-real')],2,'desativada'),
      ('app.py',['extrair-real','--origem','T002','--destino',str(raiz/'cli-real'),'--confirmar-envio'],1,'bloqueada'),
      ('app.py',['importar-revisado'],2,'required'),
      ('solucao_desafio.py',[],0,'D003 80.00 destacar')]
    antes_sug = None
    for indice,(arquivo,args,codigo,trecho) in enumerate(etapas):
        caso('CLI '+arquivo+' '+str(len(CASOS)),lambda a=arquivo,b=args,c=codigo,d=trecho:cli(a,b,c,d))
        if indice == 1:
            antes_sug = {x.name:x.read_bytes() for x in sug.iterdir()}
        if indice == 3:
            caso('Revisão pendente não cria pasta de saída',lambda:exigir(not rev.exists()))
        if indice == 5:
            caso('Pasta de sugestões existente mantém seus bytes',lambda:exigir(antes_sug=={x.name:x.read_bytes() for x in sug.iterdir()}))

def integracao(config,raiz):
    esquema='tnp_c12_t_'+uuid4().hex[:16];nome=banco.nome_esquema(esquema)
    servidor=criar_servidor(0);thread=Thread(target=servidor.serve_forever,daemon=True);thread.start()
    url='http://127.0.0.1:'+str(servidor.server_address[1])+'/categorias'
    with conectar(config) as con:
        versao=con.execute('SELECT version()').fetchone()[0]
        motor={'versao':con.info.server_version,'descricao':versao,'tipo':'complementar_wasm' if any(x in versao.lower() for x in ['pglite','wasm','emscripten']) else 'postgresql_nativo'}
    def args(comando,execucao,**extra):return SimpleNamespace(comando=comando,execucao=execucao,destino=raiz/'relatorios-pg',catalogo=url,tentativas=3,**extra)
    def run(a,esperado):
        saida=io.StringIO();eventos=[]
        with redirect_stdout(saida):ret=aplicacao.executar(a,config,lambda e,**k:eventos.append({'evento':e,**k}),esquema)
        EXECUCOES.append({'funcao':'aplicacao.executar','comando':a.comando,'execucao':a.execucao,'exit':ret,'stdout':saida.getvalue(),'eventos':eventos})
        exigir(ret==esperado)
    try:
        caso('PG esquema isolado preparado',lambda:banco.preparar(config,esquema))
        a=args('importar','pg-a',entrada=BASE/'dados/validas.json')
        caso('PG fluxo estruturado com HTTP e relatório',lambda:run(a,0))
        caso('PG A três / 127.50',lambda:exigir(banco.consultar_recibo(config,'pg-a',esquema)['retrato']['total']=='127.50'))
        sugestoes=raiz/'pg-sugestoes'
        preparar_sugestoes(sugestoes)
        b=args('importar-revisado','pg-b',pacote=sugestoes/'pacote.json',revisao=sugestoes/'revisao_pendente.json')
        caso('PG revisão pendente bloqueia importação',lambda:erro(ValueError,lambda:silencioso(lambda:aplicacao.executar(b,config,lambda *a,**k:None,esquema))))
        caso('PG revisão bloqueada não cria recibo',lambda:exigir(banco.consultar_recibo(config,'pg-b',esquema) is None))
        b.revisao=PE/'revisoes/decisoes_exemplo.json';bloqueio=raiz/'pg-bloqueio';bloqueio.write_text('preservar');b.destino=bloqueio
        caso('PG revisão confirmada com falha de exportação',lambda:run(b,3))
        rb=banco.consultar_recibo(config,'pg-b',esquema)
        caso('PG cinco / 181.00, duas novas',lambda:exigir(rb['retrato']['quantidade']==5 and rb['retrato']['total']=='181.00' and rb['novas']==2))
        caso('PG proveniência persistida com rejeição e correção',lambda:exigir(rb['proveniencia']['trilha']['rejeitados']==1 and rb['proveniencia']['trilha']['decisoes'][0]['final']['data']=='2026-09-11'))
        def recuperar():
            with patch.object(aplicacao,'preparar_entrada',side_effect=AssertionError),patch.object(aplicacao,'obter_catalogo',side_effect=AssertionError),patch.object(ia_real,'chamar_modelo',side_effect=AssertionError):
                run(args('exportar','pg-b'),0)
        caso('PG recuperação somente de exportação',recuperar)
        caso('PG A mantém retrato anterior',lambda:exigir(banco.consultar_recibo(config,'pg-a',esquema)['retrato']['total']=='127.50'))
        c=args('importar-revisado','pg-c',pacote=sugestoes/'pacote.json',revisao=b.revisao)
        caso('PG nova execução do lote revisado não duplica',lambda:run(c,0))
        caso('PG reimportação registra zero novas, duas existentes',lambda:exigir((lambda r:(r['novas'],r['existentes'],r['retrato']['total']))(banco.consultar_recibo(config,'pg-c',esquema))==(0,2,'181.00')))
        def revisao_trocada():
            q=revisao_padrao();q['revisor']='Outra revisão';p=raiz/'outra-revisao.json';p.write_bytes(json_bytes(q));d=args('importar-revisado','pg-b',pacote=sugestoes/'pacote.json',revisao=p)
            erro(ValueError,lambda:silencioso(lambda:aplicacao.executar(d,config,lambda *a,**k:None,esquema)))
        caso('PG mesmo ID não aceita revisão diferente',revisao_trocada)
        d=args('importar','pg-conflito',entrada=BASE/'dados/conflito_banco.json')
        caso('PG conflito D002 provoca rollback',lambda:erro(ValueError,lambda:silencioso(lambda:aplicacao.executar(d,config,lambda *a,**k:None,esquema))))
        def estado_final():
            with conectar(config) as con:
                exigir(con.execute(sql.SQL('SELECT count(*),sum(valor) FROM {}.despesas').format(nome)).fetchone()==(5,Decimal('181.00')))
                exigir(con.execute(sql.SQL("SELECT count(*) FROM {}.despesas WHERE id IN ('D005','D103')").format(nome)).fetchone()==(0,))
            exigir(banco.consultar_recibo(config,'pg-conflito',esquema) is None)
        caso('PG cinco despesas, D005/D103 e recibo conflitante ausentes',estado_final)
        def consulta_independente():
            with patch.object(banco,'conectar',side_effect=AssertionError):
                exigir(silencioso(lambda:consulta_sintetica('P01',raiz/'pg-rag'))==0)
        caso('RAG após importação não altera o banco',consulta_independente)
        for rotulo,ident,valor,code in [('negativo','D900',Decimal('-1.00'),'23514'),('nulo','D901',None,'23502'),('duplicado','D001',Decimal('12.50'),'23505')]:
            if motor['tipo']!='postgresql_nativo':
                CASOS.append({'nome':'PG restrição '+rotulo,'status':'pendente_nativo'});continue
            def restricao(ident=ident,valor=valor,code=code):
                try:
                    with conectar(config) as con:con.execute(sql.SQL('INSERT INTO {}.despesas VALUES (%s,%s,%s,%s,%s)').format(nome),(ident,date(2026,9,10),'Teste','Materiais',valor))
                except psycopg.Error as e:exigir(e.sqlstate==code);return
                raise AssertionError('Restrição não aplicada')
            caso('PG restrição '+rotulo,restricao)
        if motor['tipo']=='postgresql_nativo':
            def autenticacao():
                try:
                    with conectar({**config,'password':uuid4().hex}):pass
                except psycopg.OperationalError:
                    with conectar(config):pass
                    return
                raise AssertionError('Senha incorreta aceita')
            caso('PG autenticação rejeita senha incorreta',autenticacao)
        else:CASOS.append({'nome':'PG autenticação nativa','status':'pendente_nativo'})
    finally:
        servidor.shutdown();thread.join();servidor.server_close()
        with conectar(config) as con:con.execute(sql.SQL('DROP SCHEMA IF EXISTS {} CASCADE').format(nome))
    return motor

def main():
    p=argparse.ArgumentParser(description=__doc__,color=False);p.add_argument('--com-banco',action='store_true');a=p.parse_args()
    motor=None
    with patch.dict(os.environ,{},clear=False):
        os.environ.pop('OPENAI_API_KEY',None);os.environ.pop('PYTHON_PRATICA_IA_MAX_SAIDA',None)
        with tempfile.TemporaryDirectory(prefix='cap12-') as temp:
            raiz=Path(temp);locais(raiz)
            if a.com_banco:
                try:motor=integracao(configuracao_banco(),raiz)
                except (OSError,ValueError,psycopg.Error,EOFError) as e:CASOS.append({'nome':'Integração disponível','status':'reprovado','tipo':type(e).__name__})
    falhas=sum(c['status']=='reprovado' for c in CASOS);pendentes=sum(c['status']=='pendente_nativo' for c in CASOS);aprovados=sum(c['status']=='aprovado' for c in CASOS)
    status='reprovado' if falhas else 'pendente_postgresql_nativo' if pendentes else 'aprovado' if a.com_banco else 'aprovado_local'
    modo='integracao_nativa' if motor and motor['tipo']=='postgresql_nativo' else 'integracao_complementar_wasm' if motor else 'local_sem_banco'
    agora=datetime.now(timezone.utc)
    doc={'capitulo':12,'revisao':'R01','status':status,'modo':modo,'data_utc':agora.isoformat(),'sistema':platform.system(),'plataforma':platform.platform(),'python':platform.python_version(),'psycopg':version('psycopg'),'sdk_openai':version('openai'),'total':len(CASOS),'aprovados':aprovados,'falhas':falhas,'pendentes':pendentes,'chamadas_ia_reais':0,'motor':motor,'casos':CASOS,'execucoes':EXECUCOES,'sha256_arquivos':ler_json(BASE/'MANIFESTO_SHA256.json'),'nota':'Modelos não foram chamados; envelopes sintéticos e transporte SDK em memória. Integração nativa somente quando indicada no modo.'}
    pasta=BASE/'resultados';pasta.mkdir(exist_ok=True);caminho=pasta/('relatorio-cap12-'+agora.strftime('%Y%m%dT%H%M%S%fZ')+'.json');caminho.write_bytes(json_bytes(doc))
    print(status,str(aprovados)+'/'+str(len(CASOS)),'falhas',falhas,'pendentes',pendentes)
    for c in CASOS:
        if c['status']!='aprovado':print(c['nome'],c['status'],c.get('tipo',''))
    print('Relatório:',caminho)
    return 1 if falhas else 0

if __name__=='__main__':raise SystemExit(main())
