"""Verifica o avaliador e os limites; não mede qualidade de um modelo real."""
from contextlib import redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
import httpx2
from openai.types.responses import Response
from arquivos import ler_json, serializar, resumo, gravar_conjunto
from configuracao_ia import PASTA, MODELO
from conjunto import carregar, selecionar, obter_caso, preparar_pedido, recuperar_caso, identidade
from avaliacao import carregar_execucao, conferir_execucao, avaliar, comparar, modelo_revisao, conferir_revisao, julgar, metrica
from custos import estimar, custo_de_uso, novo_controle, reservar, concluir, retrato, decimal_nao_negativo
from cliente_ia import criar_cliente
from execucao_real import executar_real

CASOS=[]
EXECUCOES=[]

def exigir(condicao, mensagem='Resultado diferente do esperado'):
    if not condicao:raise AssertionError(mensagem)

def recusa(funcao):
    try:funcao()
    except ValueError:return
    raise AssertionError('Esperava ValueError')

def teste(nome,funcao):
    try:
        funcao();CASOS.append({'nome':nome,'status':'aprovado'})
    except Exception as erro:
        CASOS.append({'nome':nome,'status':'falhou','diagnostico':type(erro).__name__+': '+str(erro)})

def executar():
    a,b=[carregar_execucao(v) for v in ['A','B']]
    ra,rb=[ler_json(PASTA/'revisoes'/f'{v}.json') for v in ['A','B']]
    aa,bb=avaliar(a,ra,'todos'),avaliar(b,rb,'todos')
    teste('Python 3.14 em ambiente virtual',lambda:exigir(sys.version_info[:2]==(3,14) and sys.prefix!=sys.base_prefix))
    def deps():
        for l in (PASTA/'requirements.txt').read_text().splitlines():
            if l.strip() and not l.startswith('#'):
                n,v=l.split('==');exigir(importlib.metadata.version(n)==v,n)
    teste('Dependências fixadas',deps)
    teste('Vinte casos: 12 ajuste e 8 reserva',lambda:exigir(len(selecionar('todos'))==20 and len(selecionar('ajuste'))==12 and len(selecionar('reserva'))==8))
    def grupos():
        cs=carregar()['casos'];esperado={'extracao_definida':8,'ausencia_ambiguidade':4,'politica_coberta':4,'sem_cobertura':2,'instrucao_intrusa':2}
        exigir({g:sum(c['grupo']==g for c in cs) for g in esperado}==esperado)
    teste('Distribuição editorial 8/4/4/2/2',grupos)
    teste('Partições sem sobreposição',lambda:exigir(not {c['id'] for c in selecionar('ajuste')} & {c['id'] for c in selecionar('reserva')}))
    teste('Partição inválida recusada',lambda:recusa(lambda:selecionar('teste')))
    teste('Caso desconhecido recusado',lambda:recusa(lambda:obter_caso('X99')))
    for v,e,rev,esperado in [('A',a,ra,12),('B',b,rb,18)]:
        teste('Execução completa '+v,lambda e=e:exigir(len(conferir_execucao(e))==20))
        teste('Gabarito global '+v,lambda e=e,r=rev,n=esperado:exigir(avaliar(e,r,'todos')['metricas']['casos']=={'acertos':n,'total':20,'falhas':20-n,'pendentes':0}))
        for i in e['itens']:
            teste('Envelope sintético compatível com SDK '+v+'/'+i['caso_id'],lambda i=i:Response.model_validate(i['resposta']))
    teste('Campos: denominador 52; casos: 20',lambda:exigir(bb['metricas']['campos']['total']==52 and bb['metricas']['casos']['total']==20))
    teste('Categorias: denominador 13',lambda:exigir(bb['metricas']['categoria']['total']==13))
    teste('Ausências: seis campos, A4/B6 corretos',lambda:exigir(aa['metricas']['ausencias']['acertos']==4 and bb['metricas']['ausencias']=={'acertos':6,'total':6,'falhas':0,'pendentes':0}))
    teste('Formato válido não prova conteúdo correto',lambda:exigir(aa['metricas']['formato']['acertos']==20 and aa['metricas']['casos']['acertos']==12))
    teste('Rubrica distingue sete consultas de cinco fontes exigidas',lambda:exigir(bb['metricas']['fundamentacao']['total']==7 and bb['metricas']['fontes']['total']==5))
    teste('Mesmo indicador de categoria esconde regressão',lambda:exigir(aa['metricas']['categoria']==bb['metricas']['categoria'] and comparar(aa,bb)['regressoes']==['X04']))
    teste('B não promovida por regressão e I02',lambda:exigir(comparar(aa,bb)['decisao']=='nao_promover' and bb['falhas_criticas_ou_pendentes']==['I02']))
    teste('Sete melhorias e uma regressão produzem ganho líquido seis',lambda:exigir(len(comparar(aa,bb)['melhorias'])==7 and len(comparar(aa,bb)['regressoes'])==1))
    def sem_rev():
        rel=avaliar(b,None,'todos')
        exigir(rel['metricas']['fundamentacao']=={'acertos':0,'total':7,'falhas':0,'pendentes':7})
        exigir(rel['metricas']['casos']=={'acertos':12,'total':20,'falhas':1,'pendentes':7})
    teste('Sem revisão, sete pendências não viram acerto',sem_rev)
    teste('Métrica vazia não vira 100%',lambda:exigir(metrica([])=={'acertos':0,'total':0,'falhas':0,'pendentes':0}))
    teste('True/False/null permanecem distintos',lambda:exigir(metrica([True,False,None])=={'acertos':1,'total':3,'falhas':1,'pendentes':1}))
    for nome,mut in [
        ('dataset',lambda e:e.update(dataset_sha256='errado')),
        ('modelo',lambda e:e.update(modelo='outro')),
        ('sdk',lambda e:e.update(sdk='0')),
        ('modo',lambda e:e.update(modo='desconhecido')),
        ('duplicado',lambda e:e['itens'].__setitem__(1,deepcopy(e['itens'][0]))),
        ('pedido',lambda e:e['itens'][0].update(pedido_sha256='errado')),
        ('modelo interno',lambda e:e['itens'][0]['resposta'].update(model='outro')),
        ('duracao negativa',lambda e:e['itens'][0].update(duracao_ms=-1)),
        ('duracao boolean',lambda e:e['itens'][0].update(duracao_ms=True)),
        ('campo ausente',lambda e:e['itens'][0].pop('resposta'))]:
        def ruim(f=mut):
            e=deepcopy(b);f(e);recusa(lambda:conferir_execucao(e))
        teste('Execução inválida: '+nome,ruim)
    for nome,mut in [
        ('execucao antiga',lambda r:r.update(execucao_sha256='outra')),
        ('resposta antiga',lambda r:r['itens'][0].update(resposta_sha256='outra')),
        ('duplicada',lambda r:r['itens'].__setitem__(1,deepcopy(r['itens'][0]))),
        ('responsavel vazio',lambda r:r.update(responsavel='')),
        ('sem justificativa',lambda r:r['itens'][0].update(justificativa='')),
        ('criterio string',lambda r:r['itens'][0].update(atende_pergunta='sim')),
        ('item faltante',lambda r:r['itens'].pop())]:
        def ruim(f=mut):
            rev=deepcopy(rb);f(rev);recusa(lambda:conferir_revisao(rev,b))
        teste('Revisão inválida: '+nome,ruim)
    def nao_usar_ref_em_real():
        e=deepcopy(b);e['modo']='api_real';r=deepcopy(rb);r['execucao_sha256']=resumo(e)
        recusa(lambda:avaliar(e,r,'todos'))
    teste('Rubrica sintética não avaliza inferência real',nao_usar_ref_em_real)
    def parcial():
        e=deepcopy(b);e['itens']=[e['itens'][0]]
        recusa(lambda:avaliar(e,None,'todos'))
        r=avaliar(e,None,'todos',True);exigir(len(r['casos_ausentes'])==19 and r['metricas']['casos']['total']==1)
        recusa(lambda:comparar(r,bb))
    teste('Amostra de um caso fica 1/20 de cobertura, não avaliação completa',parcial)
    def modos():
        r=deepcopy(bb);r['modo']='api_real';recusa(lambda:comparar(aa,r))
    teste('Comparação entre real e sintético bloqueada',modos)
    teste('Comparação entre partições bloqueada',lambda:recusa(lambda:comparar(avaliar(a,ra,'ajuste'),avaliar(b,rb,'reserva'))))
    teste('Ajuste isolado não permite decisão final',lambda:exigir(any('parcial' in x for x in comparar(avaliar(a,ra,'ajuste'),avaliar(b,rb,'ajuste'))['razoes'])))
    for nome in ['X02','A01','R01','S01','I01','I02']:
        def sem_gold(n=nome):
            p,r=preparar_pedido(obter_caso(n),'B');txt=serializar(p)
            exigir('gabarito' not in txt and 'evidencias_referencia' not in txt and 'criterio' not in txt and p['tools']==[] and p['store'] is False)
            if n.startswith('I'):exigir('ignore as instruções' in txt)
        teste('Pedido sem gabarito/ferramentas: '+nome,sem_gold)
    teste('Prompt A e B geram identidades diferentes',lambda:exigir(identidade(obter_caso('X01'),'A')!=identidade(obter_caso('X01'),'B')))
    for kw in [{'limite_saida':0},{'limite_saida':True},{'limite_saida':1025},{'limite_caracteres':0},{'limite_caracteres':1}]:
        teste('Pedido bloqueia limite '+str(kw),lambda kw=kw:recusa(lambda:preparar_pedido(obter_caso('X01'),'B',**kw)))
    teste('Corpus-base sem nota intrusa',lambda:exigir('Nota intrusa' not in (PASTA/'corpus/politica.md').read_text(encoding='utf-8')))
    teste('I02 coloca nota apenas na cópia do contexto',lambda:exigir(any('Nota intrusa' in t['texto'] for t in recuperar_caso(obter_caso('I02'))['trechos'])))
    teste('Fórmula de 1000 entrada e 500 saída resulta 0.0012 USD',lambda:exigir(estimar(1000,500)==Decimal('0.0012')))
    teste('Custo total sintético A/B',lambda:exigir(Decimal(aa['custo_estimado_usd'])==Decimal('0.009160') and Decimal(bb['custo_estimado_usd'])==Decimal('0.010440')))
    teste('Mediana sintética A/B',lambda:exigir(aa['mediana_ms']=='1110' and bb['mediana_ms']=='1230'))
    for uso in [None,{}, {'input_tokens':1,'output_tokens':2,'total_tokens':4},{'input_tokens':True,'output_tokens':2,'total_tokens':3},{'input_tokens':-1,'output_tokens':2,'total_tokens':1}]:
        teste('Uso ausente/inválido não vira zero '+str(uso),lambda u=uso:exigir(custo_de_uso(u) is None))
    for v in ['NaN','Infinity','-1',True,'abc']:
        teste('Dinheiro inválido '+str(v),lambda v=v:recusa(lambda:decimal_nao_negativo(v)))
    for v in [-1,True,1.5,10000001]:
        teste('Tokens inválidos '+str(v),lambda v=v:recusa(lambda:estimar(v,100)))
    def reserva_ok():
        c=novo_controle(2,'0.01');exigir(reservar(c,1000,768)==Decimal('0.0016288'))
        exigir(concluir(c,{'input_tokens':1000,'output_tokens':500,'total_tokens':1500})==Decimal('0.0012'))
        exigir(c['tentativas']==1 and c['reserva'] is None and not c['incerto'])
    teste('Reserva substituída pelo custo estimado do uso informado',reserva_ok)
    def limite_chamadas():
        c=novo_controle(1);reservar(c,1000,768);concluir(c,{'input_tokens':1000,'output_tokens':500,'total_tokens':1500});recusa(lambda:reservar(c,1000,768));exigir(c['tentativas']==1)
    teste('Contador impede segunda chamada',limite_chamadas)
    def limite_custo():
        c=novo_controle(3,'0.002');reservar(c,1000,768);concluir(c,{'input_tokens':1000,'output_tokens':500,'total_tokens':1500});recusa(lambda:reservar(c,1000,768));exigir(c['tentativas']==1)
    teste('Orçamento impede próxima reserva',limite_custo)
    def incerto():
        c=novo_controle();reservar(c,1000,768);exigir(concluir(c,None) is None);recusa(lambda:reservar(c,1,1));exigir(c['reserva']==Decimal('0.0016288') and c['incerto'])
    teste('Uso desconhecido conserva reserva e interrompe',incerto)
    def estourou():
        c=novo_controle();reservar(c,100,100);concluir(c,{'input_tokens':200,'output_tokens':200,'total_tokens':400});exigir(c['incerto']);recusa(lambda:reservar(c,1,1))
    teste('Consumo maior que previsão interrompe novas tentativas',estourou)
    def sobreposta():
        c=novo_controle();reservar(c,1,1);recusa(lambda:reservar(c,1,1));exigir(c['tentativas']==1)
    teste('Reserva pendente não permite sobreposição',sobreposta)
    teste('Concluir sem reserva bloqueado',lambda:recusa(lambda:concluir(novo_controle(),None)))
    for m in [0,21,True]:teste('Limite de chamadas inválido '+str(m),lambda m=m:recusa(lambda:novo_controle(m)))
    def faltou_uso():
        e=deepcopy(b);e['itens'][0]['resposta']['usage']=None
        r=avaliar(e,None,'todos');exigir(r['usos_ausentes']==1 and r['usos_conhecidos']==19 and r['metricas']['casos']['falhas']>=2)
    teste('Agregado sinaliza custo parcial com uso ausente',faltou_uso)
    def sem_confirmar():
        with TemporaryDirectory() as td,patch.dict(os.environ,{'OPENAI_API_KEY':'ficticia-inutilizavel'}),redirect_stdout(io.StringIO()):
            exigir(executar_real('R01',Path(td)/'s')==2 and not (Path(td)/'s').exists())
    teste('Sem confirmação não usa nem chave presente',sem_confirmar)
    def bloqueio_previo(tipo):
        with TemporaryDirectory() as td,patch.dict(os.environ,{'OPENAI_API_KEY':''}),redirect_stdout(io.StringIO()):
            d=Path(td)/'s';kw={}
            if tipo=='destino':d.mkdir();(d/'preservar.md').write_text('original')
            if tipo=='custo':kw['orcamento_usd']='0'
            if tipo=='tamanho':kw['limite_caracteres']=1
            exigir(executar_real('R01',d,True,**kw)==1)
            if tipo=='destino':exigir((d/'preservar.md').read_text()=='original')
            else:exigir(not d.exists())
    for t in ['chave','destino','custo','tamanho']:teste('Antes da API: '+t,lambda t=t:bloqueio_previo(t))
    base=next(i['resposta'] for i in b['itens'] if i['caso_id']=='R01')
    def mock(tipo):
        chamadas=[]
        def transporte(req):
            chamadas.append(json.loads(req.content))
            if tipo=='timeout':raise httpx2.ReadTimeout('nao_expor',request=req)
            if tipo=='conexao':raise httpx2.ConnectError('nao_expor',request=req)
            if isinstance(tipo,int):return httpx2.Response(tipo,json={'error':{'message':'nao_expor','type':'invalid_request_error','code':'teste'}})
            rr=deepcopy(base)
            if tipo=='sem_uso':rr['usage']=None
            if tipo=='incompleta':rr.update(status='incomplete',incomplete_details={'reason':'max_output_tokens'})
            if tipo=='recusada':rr['output'][0]['content']=[{'type':'refusal','refusal':'Recusa sintética'}]
            return httpx2.Response(200,json=rr)
        def fabrica(k):return criar_cliente(k,http_client=httpx2.Client(transport=httpx2.MockTransport(transporte)))
        with TemporaryDirectory() as td,patch.dict(os.environ,{'OPENAI_API_KEY':'ficticia-inutilizavel'}):
            d=Path(td)/'s';out=io.StringIO()
            with redirect_stdout(out):codigo=executar_real('R01',d,True,fabrica_cliente=fabrica)
            exigir(codigo==(0 if tipo in ['ok','sem_uso','incompleta','recusada'] else 1));exigir(len(chamadas)==1 and 'nao_expor' not in out.getvalue())
            meta=ler_json(d/'metadados.json');exigir(meta['tentativas_sdk']==1 and meta['max_retries']==0)
            if codigo==0:
                rel=avaliar(ler_json(d/'execucao.json'),None,'todos',True)
                exigir(len(rel['casos_ausentes'])==19 and rel['metricas']['casos']['total']==1)
                if tipo=='ok':exigir(rel['metricas']['casos']['pendentes']==1)
                else:exigir(rel['metricas']['casos']['falhas']==1)
            if tipo in ['sem_uso','timeout','conexao',401,429,500]:exigir(meta['controle_local']['incerto'])
    for t in ['ok','sem_uso','incompleta','recusada',401,429,500,'timeout','conexao']:
        teste('SDK com transporte simulado: '+str(t),lambda t=t:mock(t))
    def erro_gravar():
        calls=[]
        def transporte(req):calls.append(1);return httpx2.Response(200,json=base)
        def fabrica(k):return criar_cliente(k,http_client=httpx2.Client(transport=httpx2.MockTransport(transporte)))
        with TemporaryDirectory() as td,patch.dict(os.environ,{'OPENAI_API_KEY':'ficticia-inutilizavel'}),patch('execucao_real.gravar_conjunto',side_effect=OSError('teste')),redirect_stdout(io.StringIO()):
            exigir(executar_real('R01',Path(td)/'s',True,fabrica_cliente=fabrica)==3 and len(calls)==1)
    teste('Falha de gravação após chamada não a repete',erro_gravar)
    with TemporaryDirectory() as td:
        raiz=Path(td)
        def cli(n,args,codigo,contem=''):
            env=os.environ.copy();env['OPENAI_API_KEY']='';env['PYTHONIOENCODING']='utf-8'
            p=subprocess.run([sys.executable,str(PASTA/n),*args],cwd=raiz,env=env,capture_output=True,text=True,encoding='utf-8',timeout=60)
            EXECUCOES.append({'programa':n,'argumentos':args,'saida':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
            exigir(p.returncode==codigo and contem in p.stdout,p.stdout+p.stderr)
        for v in ['A','B']:
            teste('CLI avaliação '+v,lambda v=v:cli('01_avaliar.py',['--versao',v,'--particao','todos','--destino',str(raiz/v)],0))
        teste('CLI revisão pendente',lambda:cli('01_avaliar.py',['--versao','B','--particao','todos','--sem-revisao','--destino',str(raiz/'pendente')],0,'fundamentacao: 0/7'))
        for part in ['ajuste','reserva','todos']:
            teste('CLI comparação '+part,lambda p=part:cli('02_comparar.py',['--particao',p,'--destino',str(raiz/p)],0,'nao_promover'))
        for c in ['orcamento','chamadas','incerto']:
            teste('CLI limite '+c,lambda c=c:cli('03_simular_limites.py',['--cenario',c],0,'bloqueada'))
        teste('CLI inspeção X02',lambda:cli('06_inspecionar.py',['--caso','X02'],0,'18.50'))
        teste('CLI inspeção I02',lambda:cli('06_inspecionar.py',['--caso','I02','--versao','B'],0,'Nota intrusa'))
        teste('CLI desafio',lambda:cli('solucao_desafio.py',[],0,'nao_promover'))
        teste('CLI pasta existente preservada',lambda:cli('01_avaliar.py',['--destino',str(raiz/'A')],1,'Destino já existe'))
        teste('CLI API sem confirmação',lambda:cli('04_amostra_real.py',[],2))
        teste('CLI API sem chave',lambda:cli('04_amostra_real.py',['--confirmar-envio','--destino',str(raiz/'real')],1,'OPENAI_API_KEY'))
        teste('CLI avaliar arquivo sem revisão',lambda:cli('05_avaliar_arquivo.py',['--execucao',str(PASTA/'execucoes/B.json'),'--destino',str(raiz/'arquivo')],0,'fundamentacao: 0/7'))
    def manifesto():
        for n,v in ler_json(PASTA/'MANIFESTO_SHA256.json').items():exigir(hashlib.sha256((PASTA/n).read_bytes()).hexdigest()==v,'Arquivo divergente: '+n)
    teste('Manifesto corresponde aos arquivos técnicos',manifesto)

def main():
    with patch.dict(os.environ,{'OPENAI_API_KEY':''}):executar()
    agora=datetime.now(timezone.utc);total=len(CASOS);ok=sum(c['status']=='aprovado' for c in CASOS)
    rel={'capitulo':10,'revisao':'R01','status':'aprovado_local' if ok==total else 'reprovado',
         'modo':'local_com_sdk_e_transporte_simulado','data_utc':agora.isoformat(),
         'sistema':platform.system(),'plataforma':platform.platform(),'python':platform.python_version(),
         'sdk_openai':importlib.metadata.version('openai'),'modelo_fixado':MODELO,
         'total':total,'aprovados':ok,'falhas':total-ok,'chamadas_reais':0,'integracao_real':'nao_executada_opcional',
         'persistencia':'nao_executada','casos':CASOS,'execucoes':EXECUCOES,
         'sha256_arquivos':ler_json(PASTA/'MANIFESTO_SHA256.json'),
         'nota':'Testes do programa não são taxa de acerto de um modelo real; corpus avaliado é sintético.'}
    p=PASTA/'resultados'/('relatorio-cap10-'+agora.strftime('%Y%m%dT%H%M%S%fZ')+'.json');p.parent.mkdir(exist_ok=True);p.write_text(serializar(rel),encoding='utf-8')
    print(rel['status'],f'{ok}/{total}','| chamadas reais: 0 | banco: não utilizado');print('Relatório:',p)
    for c in CASOS:
        if c['status']!='aprovado':print(c)
    return 0 if ok==total else 1

if __name__=='__main__':raise SystemExit(main())
