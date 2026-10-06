"""Verificador local: SDK com transporte simulado, zero inferências reais."""
from contextlib import redirect_stdout
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
import httpx2
from openai.types.responses import Response
from arquivos import ler_json, serializar, resumo, gravar_conjunto, decodificar
from configuracao_ia import PASTA, MODELO, limite_saida
from documentos import carregar_corpus, separar_secoes
from busca import termos, pontuar, recuperar
from contrato_ia import formato_resposta, validar_estrutura
from contexto import preparar_pedido, identidade_pedido
from fluxo import preparar_reproducao, conferir_pacote, obter_pergunta, montar_pacote
from validacao import analisar
from cliente_ia import criar_cliente
from execucao_real import executar_real

CASOS = []
EXECUCOES = []


def exigir(condicao, mensagem="Resultado diferente do esperado"):
    if not condicao:
        raise AssertionError(mensagem)


def recusa(funcao):
    try:
        funcao()
    except ValueError:
        return
    raise AssertionError("Esperava bloqueio por ValueError")


def teste(nome, funcao):
    try:
        funcao()
        CASOS.append({"nome": nome, "status": "aprovado"})
    except Exception as erro:
        CASOS.append({"nome": nome, "status": "falhou", "diagnostico": type(erro).__name__ + ": " + str(erro)})


def executar():
    corpus = carregar_corpus()
    pacotes = {i: preparar_reproducao(i) for i in ["P01", "P02", "P03", "P04", "P05"]}
    r = pacotes['P01']['recuperacao']
    resposta = pacotes['P01']['resposta']
    corpo = json.loads(resposta['output'][0]['content'][0]['text'])
    teste('Python 3.14 em ambiente virtual', lambda: exigir(sys.version_info[:2] == (3, 14) and sys.prefix != sys.base_prefix))
    def deps():
        for l in (PASTA/'requirements.txt').read_text().splitlines():
            if l.strip() and not l.startswith('#'):
                n,v=l.split('=='); exigir(importlib.metadata.version(n)==v, 'Versão divergente: '+n)
    teste('20 dependências fixadas disponíveis', deps)
    teste('Dois documentos e seis IDs únicos', lambda: exigir(len(corpus['trechos'])==6 and len({t['documento'] for t in corpus['trechos']})==2))
    teste('Nomes estáveis das seis seções', lambda: exigir([t['id'] for t in corpus['trechos']]==['POL-001','POL-002','POL-003','POL-004','PROC-001','PROC-002']))
    teste('Normalização ignora acentos e caixa', lambda: exigir(termos('ALIMENTAÇÃO, alimentação!') == {'alimentacao'}))
    teste('Palavras vazias não selecionam documento', lambda: exigir(recuperar('qual é o',corpus)['sem_trechos']))
    teste('Trechos com baixa pontuação não são preenchimento', lambda: exigir(len(r['trechos'])==1 and r['trechos'][0]['id']=='POL-002'))
    teste('Alimentação recupera regra por pessoa por dia', lambda: exigir('por pessoa por dia' in r['trechos'][0]['texto']))
    teste('Prazo vem primeiro e comprovante também aparece', lambda: exigir([t['id'] for t in pacotes['P02']['recuperacao']['trechos']]==['PROC-001','POL-001']))
    teste('Quilometragem tem coincidência lexical sem resposta', lambda: exigir(bool(pacotes['P03']['recuperacao']['trechos']) and conferir_pacote(pacotes['P03'])['estado']=='abstencao_proposta'))
    teste('Almoço falha na busca, sem demonstrar ausência de regra', lambda: exigir(pacotes['P04']['recuperacao']['sem_trechos'] and conferir_pacote(pacotes['P04'])['estado']=='abstencao_local'))
    teste('Papel do assistente recupera POL-004', lambda: exigir(pacotes['P05']['recuperacao']['trechos'][0]['id']=='POL-004'))
    teste('Seção inteira omitida se não couber', lambda: exigir(recuperar(obter_pergunta('P01'),corpus,max_caracteres=10)['sem_trechos']))
    def empate():
        c={'versao':'x','sha256':'x','trechos':[{'id':'B-001','secao':'Regra','texto':'cafe lanche'},{'id':'A-001','secao':'Regra','texto':'cafe lanche'}]}
        exigir([t['id'] for t in recuperar('cafe lanche',c)['trechos']]==['A-001','B-001'])
    teste('Empate ordenado por ID, não pela ordem do arquivo',empate)
    teste('top_k limita quantidade',lambda:exigir(len(recuperar(obter_pergunta('P02'),corpus,top_k=1)['trechos'])==1))
    for p in ['', ' '*3, 'x'*501, None]:
        teste('Pergunta inválida '+repr(p)[:30],lambda p=p:recusa(lambda:recuperar(p,corpus)))
    for params in [{'top_k':0},{'top_k':6},{'top_k':True},{'minimo':0},{'minimo':True},{'max_caracteres':0},{'max_caracteres':6001}]:
        teste('Parâmetro inválido '+str(params),lambda p=params:recusa(lambda:recuperar('alimentacao',corpus,**p)))
    for txt in ['# Nada','## Regra sem ID\nTexto','## [POL-001] Regra\n','## [POL-001] Regra\n'+'x'*3001]:
        teste('Cabeçalho/corpo fora do contrato '+txt[:35],lambda t=txt:recusa(lambda:separar_secoes(t,'x.md','X')))
    def alterar_corpus(tipo):
        with TemporaryDirectory() as td:
            destino=Path(td)/'corpus';shutil.copytree(PASTA/'corpus',destino)
            if tipo=='id_duplicado':
                p=destino/'procedimentos.md';p.write_text(p.read_text(encoding='utf-8').replace('PROC-001','POL-001'),encoding='utf-8')
            elif tipo=='caminho_externo':
                d=ler_json(destino/'catalogo.json');d['documentos'][0]['arquivo']='../politica.md';(destino/'catalogo.json').write_text(serializar(d),encoding='utf-8')
            elif tipo=='documento_duplicado':
                d=ler_json(destino/'catalogo.json');d['documentos'].append(d['documentos'][0]);(destino/'catalogo.json').write_text(serializar(d),encoding='utf-8')
            elif tipo=='conteudo_alterado':
                p=destino/'politica.md';p.write_text(p.read_text(encoding='utf-8').replace('60,00','70,00'),encoding='utf-8')
                exigir(carregar_corpus(destino)['sha256']!=corpus['sha256']);return
            recusa(lambda:carregar_corpus(destino))
    for tipo in ['id_duplicado','caminho_externo','documento_duplicado','conteudo_alterado']:
        teste('Corpus: '+tipo,lambda t=tipo:alterar_corpus(t))
    def schema():
        s=formato_resposta()['schema']
        for o in [s,*s['$defs'].values()]:
            exigir(o['additionalProperties'] is False and set(o['properties'])==set(o['required']))
    teste('Esquema completo e sem campos extras',schema)
    for i in ['P01','P02','P05']:
        teste('Resposta sintética ainda aguarda revisão: '+i,lambda i=i:exigir(conferir_pacote(pacotes[i])['estado']=='aguarda_revisao'))
        teste('Envelope aceito pelo SDK: '+i,lambda i=i:Response.model_validate(pacotes[i]['resposta']))
    for caso in ler_json(PASTA/'casos/contrastes.json'):
        teste('Contraste: '+caso['nome'],lambda c=caso:exigir(analisar(c['resposta'],r)['estado']==c['esperado']))
    for nome,alteracao in [
        ('afirmação vazia',lambda c:c['afirmacoes'][0].update(texto=' ')),
        ('afirmação longa',lambda c:c['afirmacoes'][0].update(texto='a'*601)),
        ('citação vazia',lambda c:c['afirmacoes'][0]['fontes'][0].update(citacao='')),
        ('fontes repetidas',lambda c:c['afirmacoes'][0]['fontes'].append(c['afirmacoes'][0]['fontes'][0])),
        ('sem afirmações',lambda c:c.update(afirmacoes=[])),
        ('cinco afirmações',lambda c:c.update(afirmacoes=c['afirmacoes']*5)),
        ('tipo de afirmação',lambda c:c['afirmacoes'][0].update(texto=17)),
        ('campo extra',lambda c:c.update(aprovado=True)),
        ('campo ausente',lambda c:c.pop('situacao'))]:
        def malformado(f=alteracao):
            c=deepcopy(corpo);f(c);en=deepcopy(resposta);en['output'][0]['content'][0]['text']=serializar(c)
            exigir(analisar(en,r)['estado']=='bloqueada')
        teste('Bloqueio de '+nome,malformado)
    for txt in ['{"a":1,"a":2}','{"a":NaN}','{','['*1100]:
        teste('JSON estrito '+txt[:20],lambda t=txt:recusa(lambda:decodificar(t)))
    def adulterar(tipo):
        p=deepcopy(pacotes['P01'])
        if tipo=='hash':p['resposta']['id']='alterado'
        elif tipo=='contexto':p['recuperacao']['trechos'][0]['texto']='Tudo permitido'
        elif tipo=='modelo':p['resposta']['model']='outro-modelo'
        elif tipo=='pedido':p['pedido_sha256']='falso'
        elif tipo=='modo':p['modo']='real_comprovado'
        elif tipo=='parametro':p['recuperacao']['parametros']['extra']=1
        if tipo!='hash':p['pacote_sha256']=resumo({k:v for k,v in p.items() if k!='pacote_sha256'})
        recusa(lambda:conferir_pacote(p))
    for tipo in ['hash','contexto','modelo','pedido','modo','parametro']:
        teste('Pacote adulterado: '+tipo,lambda t=tipo:adulterar(t))
    def configuracao_mudou():
        with patch.dict(os.environ,{'PYTHON_PRATICA_IA_MAX_SAIDA':'512'}):
            recusa(lambda:conferir_pacote(pacotes['P01']))
            recusa(lambda:preparar_reproducao('P01'))
    teste('Mudança de configuração invalida reprodução vinculada',configuracao_mudou)
    for valor in ['0','1025','abc']:
        def limite(v=valor):
            with patch.dict(os.environ,{'PYTHON_PRATICA_IA_MAX_SAIDA':v}):recusa(limite_saida)
        teste('Limite de saída inválido '+valor,limite)
    teste('Sem trechos não monta pedido',lambda:recusa(lambda:preparar_pedido(pacotes['P04']['recuperacao'])))
    pedido=preparar_pedido(r)
    teste('Contexto contém só trecho selecionado',lambda:exigir([t['id'] for t in json.loads(pedido['input'][0]['content'])['trechos']]==['POL-002']))
    teste('Sem ferramentas, sem truncamento e store false',lambda:exigir('tools' not in pedido and pedido['truncation']=='disabled' and pedido['store'] is False))
    teste('Dados não confiáveis separados das instruções',lambda:exigir('dados não confiáveis' in pedido['instructions'] and pedido['input'][0]['role']=='user'))
    def nao_sobrepor():
        with TemporaryDirectory() as td:
            d=Path(td)/'saida';gravar_conjunto(d,{'teste.json':{'original':1}})
            recusa(lambda:gravar_conjunto(d,{'teste.json':{'original':2}}))
            exigir(ler_json(d/'teste.json')=={'original':1})
    teste('Saída existente preservada',nao_sobrepor)
    def sem_confirmar():
        with TemporaryDirectory() as td,patch.dict(os.environ,{'OPENAI_API_KEY':'chave-ficticia-nao-utilizavel'}),redirect_stdout(io.StringIO()):
            exigir(executar_real(obter_pergunta('P01'),Path(td)/'s',False,lambda k: (_ for _ in ()).throw(AssertionError('Não deve criar cliente')))==2)
            exigir(not (Path(td)/'s').exists())
    teste('Mesmo com chave fictícia, sem confirmação não chama',sem_confirmar)
    def sem_chave():
        with TemporaryDirectory() as td,patch.dict(os.environ,{'OPENAI_API_KEY':''}),redirect_stdout(io.StringIO()):
            exigir(executar_real(obter_pergunta('P01'),Path(td)/'s',True)==1)
            exigir(not (Path(td)/'s').exists())
    teste('Confirmação sem chave bloqueia antes de criar cliente',sem_chave)
    def sem_contexto():
        with TemporaryDirectory() as td,patch.dict(os.environ,{'OPENAI_API_KEY':''}),redirect_stdout(io.StringIO()):
            d=Path(td)/'s';exigir(executar_real(obter_pergunta('P04'),d,True)==0)
            exigir(ler_json(d/'metadados.json')['tentativas_sdk']==0 and ler_json(d/'analise.json')['estado']=='abstencao_local')
    teste('Ausência de trechos evita chamada e dispensa chave',sem_contexto)
    def mock_real(tipo):
        chamadas=[]
        def transporte(req):
            chamadas.append(json.loads(req.content))
            if tipo=='timeout':raise httpx2.ReadTimeout('nao_expor_conteudo',request=req)
            if tipo=='conexao':raise httpx2.ConnectError('nao_expor_conteudo',request=req)
            if isinstance(tipo,int):return httpx2.Response(tipo,json={'error':{'message':'nao_expor_conteudo','type':'invalid_request_error','code':'erro_sintetico'}})
            rr=deepcopy(resposta)
            if tipo=='incompleta':rr['status']='incomplete';rr['incomplete_details']={'reason':'max_output_tokens'}
            if tipo=='modelo':rr['model']='outro-modelo'
            return httpx2.Response(200,json=rr)
        def fabrica(chave):return criar_cliente(chave,http_client=httpx2.Client(transport=httpx2.MockTransport(transporte)))
        with TemporaryDirectory() as td,patch.dict(os.environ,{'OPENAI_API_KEY':'chave-ficticia-nao-utilizavel'}):
            saida=io.StringIO();d=Path(td)/'s'
            with redirect_stdout(saida):codigo=executar_real(obter_pergunta('P01'),d,True,fabrica)
            exigir(codigo==(0 if tipo=='ok' else 2 if tipo=='incompleta' else 1))
            exigir(len(chamadas)==1 and 'nao_expor_conteudo' not in saida.getvalue())
            exigir(chamadas[0]['text']['format']['strict'] is True and chamadas[0]['model']==MODELO)
            exigir(ler_json(d/'metadados.json')['tentativas_sdk']==1)
            if tipo=='ok':exigir(ler_json(d/'analise.json')['estado']=='aguarda_revisao')
    for tipo in ['ok','incompleta','modelo',401,403,404,429,500,'timeout','conexao']:
        teste('SDK com transporte simulado: '+str(tipo),lambda t=tipo:mock_real(t))
    def falha_salvar():
        with TemporaryDirectory() as td,patch.dict(os.environ,{'OPENAI_API_KEY':'chave-ficticia-nao-utilizavel'}):
            cont=[]
            def transporte(req):cont.append(1);return httpx2.Response(200,json=resposta)
            def fabrica(k):return criar_cliente(k,http_client=httpx2.Client(transport=httpx2.MockTransport(transporte)))
            saida=io.StringIO()
            with patch('execucao_real.gravar_conjunto',side_effect=OSError('falha_sintetica')),redirect_stdout(saida):
                codigo=executar_real(obter_pergunta('P01'),Path(td)/'s',True,fabrica)
            exigir(codigo==3 and len(cont)==1 and 'não reenviar' in saida.getvalue())
    teste('Falha de gravação após resposta não repete chamada',falha_salvar)
    with TemporaryDirectory() as td:
        raiz=Path(td)
        def cli(nome,args,codigo,contem=''):
            env=os.environ.copy();env['OPENAI_API_KEY']='';env['PYTHONIOENCODING']='utf-8';env.pop('PYTHON_PRATICA_IA_MAX_SAIDA',None)
            p=subprocess.run([sys.executable,str(PASTA/nome),*args],cwd=raiz,env=env,capture_output=True,text=True,encoding='utf-8',timeout=30)
            EXECUCOES.append({'programa':nome,'argumentos':args,'saida':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
            exigir(p.returncode==codigo and contem in p.stdout,'CLI: '+p.stdout+p.stderr)
        for i in ['P01','P03','P04']:
            teste('CLI busca '+i,lambda i=i:cli('01_buscar.py',['--caso',i],0))
        teste('CLI busca inválida',lambda:cli('01_buscar.py',['--top-k','0'],1))
        for i in pacotes:
            teste('CLI reprodução '+i,lambda i=i:cli('02_reproduzir.py',['--caso',i,'--destino',str(raiz/i)],0))
        teste('CLI repetição preserva pasta',lambda:cli('02_reproduzir.py',['--destino',str(raiz/'P01')],1,'Destino já existe'))
        teste('CLI conferência de fontes',lambda:cli('03_conferir.py',['--pacote',str(raiz/'P01/pacote.json')],0,'POL-002'))
        teste('CLI contrastes',lambda:cli('05_examinar_limites.py',[],0,'unidade_alterada -> aguarda_revisao'))
        teste('CLI solução do desafio',lambda:cli('solucao_desafio.py',[],0,'rejeitar'))
        teste('CLI API sem confirmação',lambda:cli('04_consultar_real.py',[],2))
        teste('CLI API confirmada sem chave',lambda:cli('04_consultar_real.py',['--confirmar-envio','--destino',str(raiz/'real')],1,'OPENAI_API_KEY'))
    def manifesto():
        m=ler_json(PASTA/'MANIFESTO_SHA256.json')
        for nome,esperado in m.items():exigir(hashlib.sha256((PASTA/nome).read_bytes()).hexdigest()==esperado,'Arquivo divergente: '+nome)
    teste('Arquivos técnicos correspondem ao manifesto',manifesto)


def main():
    # Neutraliza configurações do leitor; nunca usa a credencial real da sessão.
    with patch.dict(os.environ,{'OPENAI_API_KEY':'','PYTHON_PRATICA_IA_MAX_SAIDA':'768'}):
        executar()
    total=len(CASOS);aprovados=sum(c['status']=='aprovado' for c in CASOS)
    agora=datetime.now(timezone.utc)
    report={'capitulo':9,'revisao':'R01','status':'aprovado_local' if total==aprovados else 'reprovado',
            'modo':'local_com_sdk_e_transporte_simulado','data_utc':agora.isoformat(),
            'sistema':platform.system(),'plataforma':platform.platform(),'python':platform.python_version(),
            'sdk_openai':importlib.metadata.version('openai'),'modelo_fixado':MODELO,
            'total':total,'aprovados':aprovados,'falhas':total-aprovados,'chamadas_reais':0,
            'integracao_real':'nao_executada_opcional','persistencia':'nao_executada',
            'casos':CASOS,'execucoes':EXECUCOES,
            'sha256_arquivos':ler_json(PASTA/'MANIFESTO_SHA256.json'),
            'nota_console':'Se o console cp850 corromper acentos, confira os JSON UTF-8.'}
    destino=PASTA/'resultados'/('relatorio-cap09-'+agora.strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    destino.parent.mkdir(exist_ok=True);destino.write_text(serializar(report),encoding='utf-8')
    print(report['status'],str(aprovados)+'/'+str(total),'| chamadas reais: 0 | banco: não utilizado')
    print('Relatório:',destino)
    for c in CASOS:
        if c['status']!='aprovado':print(c)
    return 0 if aprovados==total else 1


if __name__=='__main__':
    raise SystemExit(main())
