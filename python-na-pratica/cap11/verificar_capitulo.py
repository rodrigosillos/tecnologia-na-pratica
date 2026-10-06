"""Verificações locais e, com --com-banco, integração isolada no PostgreSQL 18."""
import argparse
from contextlib import redirect_stdout
from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
from importlib import metadata
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4
import psycopg
from psycopg import sql
import requests
import app
import aplicacao
import banco
import catalogo
from arquivos import ler_entrada, json_bytes, carregar_json
from conexao import configuracao_banco, conectar
from eventos import abrir_log
import exportacao
from recibos import conferir_recibo, criar_retrato, validar_id
from regras import validar_lote
from solucao_desafio import decidir
from tentativas import tentar_leitura, FalhaTransitoria

BASE = Path(__file__).resolve().parent
CASOS = []
EXECUCOES = []
CATEGORIAS = ["Alimentação", "Transporte", "Materiais"]


def exigir(condicao, motivo="Resultado diferente do esperado"):
    if not condicao:
        raise AssertionError(motivo)


def erro(tipo, funcao):
    try:
        funcao()
    except tipo:
        return
    raise AssertionError("Erro esperado não ocorreu")


def caso(nome, funcao):
    try:
        funcao()
        CASOS.append({"nome": nome, "status": "aprovado"})
    except Exception as exc:
        # Não registra exceções brutas, credenciais ou caminhos privados.
        CASOS.append({"nome": nome, "status": "reprovado", "tipo": type(exc).__name__})


def cli(arquivo, argumentos, codigo, trecho):
    ambiente = os.environ.copy()
    ambiente.pop("OPENAI_API_KEY", None)
    ambiente["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, str(BASE / arquivo), *argumentos],
                       cwd=BASE, env=ambiente, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=30)
    EXECUCOES.append({"arquivo": arquivo, "argumentos": argumentos,
                      "exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr})
    exigir(r.returncode == codigo and trecho in r.stdout + r.stderr)


def recibo_exemplo():
    registros, h = ler_entrada(BASE / "dados/validas.json")
    despesas = validar_lote(registros, CATEGORIAS)["despesas"]
    linhas = [(d["id"], d["data"], d["descricao"], d["categoria"], d["valor"]) for d in despesas]
    return {"execucao": "ensaio-01", "entrada_sha256": h,
            "novas": 3, "existentes": 0, "retrato": criar_retrato(linhas)}


def locais(raiz):
    caso("Python 3.14 em ambiente virtual", lambda: exigir(sys.version_info[:2] == (3,14) and sys.prefix != sys.base_prefix))
    def dependencias():
        for linha in (BASE / "requirements.txt").read_text().splitlines():
            if "==" in linha:
                nome, versao = linha.split("==")
                exigir(metadata.version(nome) == versao)
    caso("Dependências fixadas", dependencias)
    manifesto = json.loads((BASE / "MANIFESTO_SHA256.json").read_text())
    caso("Hashes técnicos do pacote", lambda: exigir(all(hashlib.sha256((BASE/f).read_bytes()).hexdigest() == h for f,h in manifesto.items())))
    registro, entrada_hash = ler_entrada(BASE / "dados/validas.json")
    caso("CSV e JSON representam as mesmas despesas", lambda: exigir(ler_entrada(BASE / "dados/validas.csv")[0] == registro))
    caso("Hash dos bytes efetivamente lidos", lambda: exigir(entrada_hash == hashlib.sha256((BASE / "dados/validas.json").read_bytes()).hexdigest()))
    for nome, conteudo in [("chave", '[{"id":"D001","id":"D002"}]'), ("constante", '[NaN]'), ("vazio", '[]'), ("raiz", '{}')]:
        p = raiz / (nome + ".json"); p.write_text(conteudo)
        caso("Entrada rejeitada: " + nome, lambda p=p: erro(ValueError, lambda: ler_entrada(p)))
    p = raiz / "grande.json"; p.write_bytes(b' ' * 1_048_577)
    caso("Limite de entrada", lambda: erro(ValueError, lambda: ler_entrada(p)))
    caso("JSON com tipo numérico de valor recusado", lambda: exigir(bool(validar_lote([{**registro[0], "valor": 12.5}], CATEGORIAS)["erros"])))
    caso("Lote conflitante não retorna despesas parciais", lambda: exigir(validar_lote([registro[0], {**registro[0], "valor": "99.00"}], CATEGORIAS)["despesas"] == []))
    for ident in ["../outra", "ABC", "", "a"*41, "ação", "a/b"]:
        caso("Identificação bloqueada: " + repr(ident), lambda ident=ident: erro(ValueError, lambda: validar_id(ident)))
    r = recibo_exemplo()
    caso("Retrato inicial 3 / 127.50", lambda: exigir(r["retrato"]["quantidade"] == 3 and r["retrato"]["total"] == "127.50"))
    for campo, valor in [("quantidade", True), ("total", "127.51"), ("despesas", list(reversed(r["retrato"]["despesas"]))), ("despesas", [])]:
        alterado = deepcopy(r); alterado["retrato"][campo] = valor
        caso("Recibo divergente rejeitado: " + campo + str(len(CASOS)), lambda alterado=alterado: erro(ValueError, lambda: conferir_recibo(alterado)))
    def repeticao():
        chamadas=[]; pausas=[]; eventos=[]
        def op():
            chamadas.append(1)
            if len(chamadas) < 3: raise FalhaTransitoria()
            return "ok"
        exigir(tentar_leitura(op, 3, .2, lambda e,**c: eventos.append((e,c)), pausas.append) == "ok")
        exigir(len(chamadas) == 3 and pausas == [.2,.4] and eventos[-1][1] == {"tentativa":3})
    caso("Falha transitória: 3 tentativas e esperas 0.2/0.4", repeticao)
    for maximo in (1,3,5):
        def esgota(maximo=maximo):
            chamadas=[]; pausas=[]
            def op(): chamadas.append(1); raise FalhaTransitoria()
            erro(FalhaTransitoria, lambda: tentar_leitura(op,maximo, .1, dormir=pausas.append))
            exigir(len(chamadas)==maximo and len(pausas)==maximo-1)
        caso("Limite exato de tentativas " + str(maximo), esgota)
    def permanente():
        chamadas=[]
        def op(): chamadas.append(1); raise ValueError()
        erro(ValueError, lambda: tentar_leitura(op, dormir=lambda _: exigir(False)))
        exigir(len(chamadas)==1)
    caso("Erro permanente não é repetido", permanente)
    for n in (0,6,True,2.5):
        caso("Número inválido de tentativas " + str(n), lambda n=n: erro(ValueError,lambda: tentar_leitura(lambda: 1,n)))
    caso("Espera NaN rejeitada", lambda: erro(ValueError, lambda: tentar_leitura(lambda: 1,espera=float('nan'))))
    for url in ["https://127.0.0.1:8765/categorias", "http://example.com:80/", "http://a:b@127.0.0.1:8765/", "http://127.0.0.1:8765/?x=1"]:
        caso("URL fora do contrato bloqueada: " + str(len(CASOS)), lambda url=url: erro(ValueError, lambda: catalogo.validar_url(url)))
    for exc in (requests.ConnectTimeout, requests.ReadTimeout, requests.ConnectionError):
        def transporte(exc=exc):
            with patch('requests.Session.get', side_effect=exc):
                erro(FalhaTransitoria, lambda: catalogo.obter_uma_vez("http://127.0.0.1:8765/categorias"))
        caso("Transporte classificado: " + exc.__name__, transporte)
    def resposta_http(status, corpo=b'{}', tipo="application/json"):
        class Resposta:
            status_code=status; headers={"Content-Type":tipo}
            def __enter__(self): return self
            def __exit__(self,*a): pass
            def iter_content(self,*a): yield corpo
        return Resposta()
    for status in [502,503,504,400,401,429,302]:
        def http(status=status):
            with patch('requests.Session.get', return_value=resposta_http(status)) as get:
                tipo = FalhaTransitoria if status in {502,503,504} else ValueError
                erro(tipo,lambda: catalogo.obter_uma_vez("http://127.0.0.1:8765/categorias"))
                exigir(get.call_count==1 and get.call_args.kwargs["allow_redirects"] is False)
        caso("HTTP " + str(status) + " classificado", http)
    for nome, corpo, mime in [("JSON",b'{',"application/json"),("tamanho",b' '*32769,"application/json"),("UTF8",b'\xff',"application/json"),("tipo",b'{}',"text/plain"),("contrato",b'{"versao":1,"categorias":"x"}',"application/json")]:
        def contrato(corpo=corpo,mime=mime):
            with patch('requests.Session.get',return_value=resposta_http(200,corpo,mime)):
                erro(ValueError,lambda: catalogo.obter_uma_vez("http://127.0.0.1:8765/categorias"))
        caso("Resposta não repetível: " + nome,contrato)
    destino=raiz/'relatorios'
    caso("Destino ausente é pendente",lambda: exigir(exportacao.conferir_destino(r,destino)=="pendente"))
    caso("Primeira exportação criada",lambda: exigir(exportacao.exportar(r,destino)=="criada"))
    def reutilizar():
        antes={p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in (destino/r['execucao']).iterdir()}
        exigir(exportacao.exportar(r,destino)=="reutilizada")
        depois={p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in (destino/r['execucao']).iterdir()}
        exigir(antes==depois)
    caso("Reexportação preserva bytes e datas",reutilizar)
    caso("CSV UTF-8 com BOM",lambda: exigir((destino/r['execucao']/'despesas.csv').read_bytes().startswith(b'\xef\xbb\xbf')))
    caso("HTML informa retrato e total",lambda: exigir('127.50' in (destino/r['execucao']/'despesas.html').read_text(encoding='utf-8')))
    def protecao():
        alterado=deepcopy(r); alterado['retrato']['despesas'][0]['descricao']='=1+1 <script>'
        arquivos=exportacao.renderizar(alterado)
        exigir(b"'=1+1" in arquivos['despesas.csv'] and b'&lt;script&gt;' in arquivos['despesas.html'])
    caso("Texto escapado no HTML e início de fórmula protegido",protecao)
    def adulterado():
        p=destino/r['execucao']/'despesas.csv'; p.write_bytes(b'meu arquivo')
        erro(ValueError,lambda: exportacao.exportar(r,destino))
        exigir(p.read_bytes()==b'meu arquivo')
    caso("Destino divergente preservado",adulterado)
    def falha_arquivo():
        local=raiz/'falha-escrita'
        with patch.object(Path,'write_bytes',side_effect=OSError):
            erro(OSError,lambda: exportacao.exportar(r,local))
        exigir(local.is_dir() and list(local.iterdir())==[])
    caso("Falha ao escrever não publica pasta parcial",falha_arquivo)
    def logs():
        registrar,fechar,p=abrir_log(raiz/'logs','ensaio-01','exportar')
        try:
            registrar('inicio'); erro(ValueError,lambda: registrar('x',senha='segredo'))
        finally: fechar()
        dados=carregar_json(p.read_text(encoding='utf-8'))
        exigir(dados['execucao']=='ensaio-01' and dados['evento']=='inicio' and 'segredo' not in p.read_text())
    caso("Log UTF-8 identifica tentativa e bloqueia campo senha",logs)
    args=SimpleNamespace(comando='exportar',execucao='ensaio-01',destino=raiz/'retomada')
    def retomar():
        with patch.object(banco,'consultar_recibo',return_value=r), patch.object(banco,'importar',side_effect=AssertionError), patch.object(aplicacao,'obter_catalogo',side_effect=AssertionError), patch.object(aplicacao,'ler_entrada',side_effect=AssertionError), redirect_stdout(io.StringIO()):
            exigir(aplicacao.executar(args,{},lambda *a,**k:None)==0)
    caso("Exportar não lê entrada nem catálogo e não importa",retomar)
    def ausente():
        with patch.object(banco,'consultar_recibo',return_value=None),patch.object(aplicacao,'exportar',side_effect=AssertionError),redirect_stdout(io.StringIO()):
            exigir(aplicacao.executar(args,{},lambda *a,**k:None)==1)
    caso("Recibo ausente impede exportação",ausente)
    def reexecutar():
        a=SimpleNamespace(**{**vars(args),'comando':'executar','entrada':BASE/'dados/validas.json','catalogo':'http://127.0.0.1:8765/categorias','tentativas':3})
        with patch.object(banco,'consultar_recibo',return_value=r),patch.object(banco,'importar',side_effect=AssertionError),patch.object(aplicacao,'obter_catalogo',side_effect=AssertionError),redirect_stdout(io.StringIO()):
            exigir(aplicacao.executar(a,{},lambda *a,**k:None)==0)
            a.entrada=BASE/'dados/quarta_despesa.json'
            erro(ValueError,lambda: aplicacao.executar(a,{},lambda *a,**k:None))
    caso("Execução existente dispensa catálogo e bloqueia outra entrada",reexecutar)
    def incerta():
        argumentos=['executar','--execucao','nova','--entrada',str(BASE/'dados/validas.json'),'--logs',str(raiz/'logs-incerta')]
        with patch.object(app,'configuracao_banco',return_value={}),patch.object(banco,'consultar_recibo',return_value=None),patch.object(aplicacao,'obter_catalogo',return_value=CATEGORIAS),patch.object(banco,'importar',side_effect=psycopg.OperationalError),patch.object(aplicacao,'exportar',side_effect=AssertionError),redirect_stdout(io.StringIO()):
            exigir(app.main(argumentos)==4)
    caso("Falha na confirmação exige consulta e não exporta",incerta)
    def confirmada_pendente():
        a=SimpleNamespace(**{**vars(args),'comando':'executar','entrada':BASE/'dados/validas.json','catalogo':'http://127.0.0.1:8765/categorias','tentativas':3})
        with patch.object(banco,'consultar_recibo',return_value=None),patch.object(aplicacao,'obter_catalogo',return_value=CATEGORIAS),patch.object(banco,'importar',return_value=r) as imp,patch.object(aplicacao,'exportar',side_effect=OSError),redirect_stdout(io.StringIO()):
            exigir(aplicacao.executar(a,{},lambda *a,**k:None)==3 and imp.call_count==1)
    caso("Falha de exportação após importação retorna 3",confirmada_pendente)
    for estados,esperado in [(("ausente","pendente"),"importar"),(("confirmada","pendente"),"exportar"),(("confirmada","concluida"),"conferir"),(("incerta","pendente"),"consultar")]:
        caso("Decisão " + '/'.join(estados),lambda estados=estados,esperado=esperado: exigir(decidir(*estados)==esperado))
    caso("Arquivo sem recibo não prova confirmação",lambda: erro(ValueError,lambda: decidir('ausente','concluida')))
    for arquivo, argumentos, codigo, trecho in [
        ('app.py',['--help'],0,'exportar'),
        ('app.py',['executar'],2,'required'),
        ('app.py',['executar','--execucao','x','--entrada','dados/validas.json','--tentativas','0'],2,'invalid choice'),
        ('app.py',['status','--execucao','../x'],1,'inválida'),
        ('01_tentativas.py',['--cenario','recupera'],0,'Tentativas HTTP: 3'),
        ('01_tentativas.py',['--cenario','esgota'],1,'Tentativas HTTP: 3'),
        ('01_tentativas.py',['--cenario','contrato'],1,'Tentativas HTTP: 1'),
        ('02_erro_intencional.py',[],1,'Erro detectado'),
        ('solucao_desafio.py',[],0,'confirmada / pendente -> exportar')]:
        caso("CLI " + arquivo + ' ' + ' '.join(argumentos),lambda a=arquivo,b=argumentos,c=codigo,d=trecho: cli(a,b,c,d))


def integracao(config, raiz):
    esquema='tnp_c11_t_'+uuid4().hex[:16]
    nome=banco.nome_esquema(esquema)
    motor={}
    with conectar(config) as con:
        completo=con.execute('SELECT version()').fetchone()[0]
        motor={'versao':con.info.server_version,'descricao':completo,
               'tipo':'complementar_wasm' if any(t in completo.lower() for t in ['pglite','wasm','emscripten']) else 'postgresql_nativo'}
    try:
        caso("PG preparar esquema isolado",lambda: banco.preparar(config,esquema))
        caso("PG preparar novamente preserva esquema",lambda: banco.preparar(config,esquema))
        registros,h=ler_entrada(BASE/'dados/validas.json')
        recibos={}
        def importar_inicial():
            r=banco.importar(config,'pg-01',h,registros,CATEGORIAS,esquema)
            exigir(r['novas']==3 and r['retrato']['total']=='127.50')
            recibos['primeiro']=r
        caso("PG importação e recibo 3 / 127.50",importar_inicial)
        caso("PG mesmo ID recupera o mesmo recibo",lambda: exigir(banco.importar(config,'pg-01',h,registros,CATEGORIAS,esquema)==recibos['primeiro']))
        caso("PG outro conteúdo para mesma execução bloqueado",lambda: erro(ValueError,lambda: banco.importar(config,'pg-01','f'*64,registros,CATEGORIAS,esquema)))
        def reimportar():
            r=banco.importar(config,'pg-repetida',h,registros,CATEGORIAS,esquema)
            exigir(r['novas']==0 and r['existentes']==3 and r['retrato']['quantidade']==3)
        caso("PG nova execução não duplica despesas idênticas",reimportar)
        conflitos,ch=ler_entrada(BASE/'dados/conflito_banco.json')
        caso("PG conflito D002 reverte lote com D005",lambda: erro(ValueError,lambda: banco.importar(config,'pg-conflito',ch,conflitos,CATEGORIAS,esquema)))
        def conferir_rollback():
            exigir(banco.consultar_recibo(config,'pg-conflito',esquema) is None)
            with conectar(config) as con:
                exigir(con.execute(sql.SQL("SELECT count(*) FROM {}.despesas WHERE id='D005'").format(nome)).fetchone()==(0,))
        caso("PG rollback não deixa D005 nem recibo",conferir_rollback)
        quarta,qh=ler_entrada(BASE/'dados/quarta_despesa.json')
        caso("PG importação posterior 4 / 147.50",lambda: exigir(banco.importar(config,'pg-02',qh,quarta,CATEGORIAS,esquema)['retrato']['total']=='147.50'))
        caso("PG retrato anterior permanece 127.50",lambda: exigir(banco.consultar_recibo(config,'pg-01',esquema)==recibos['primeiro']))
        def recuperar():
            bloqueio=raiz/'bloqueio-pg';bloqueio.write_text('preservar')
            r=banco.consultar_recibo(config,'pg-01',esquema)
            erro(OSError,lambda: exportacao.exportar(r,bloqueio))
            exigir(exportacao.exportar(r,raiz/'exportacao-pg')=='criada')
            exigir(bloqueio.read_text()=='preservar')
        caso("PG exportação falha e é recuperada do recibo antigo",recuperar)
        def falha_recibo():
            nova=[{**registros[0],'id':'D006'}]
            with patch.object(banco,'criar_retrato',side_effect=ValueError):
                erro(ValueError,lambda:banco.importar(config,'pg-sem-recibo','e'*64,nova,CATEGORIAS,esquema))
            with conectar(config) as con:
                exigir(con.execute(sql.SQL("SELECT count(*) FROM {}.despesas WHERE id='D006'").format(nome)).fetchone()==(0,))
            exigir(banco.consultar_recibo(config,'pg-sem-recibo',esquema) is None)
        caso("PG falha antes do recibo também reverte a despesa",falha_recibo)
        def confirmacao_perdida():
            # Commit REAL seguido de falha SIMULADA de confirmação ao cliente.
            # Não simula fisicamente queda de rede no protocolo PostgreSQL.
            original=banco.conectar
            class Conexao:
                def __enter__(self):
                    self.con=original(config)
                    return self.con.__enter__()
                def __exit__(self,*args):
                    retorno=self.con.__exit__(*args)
                    if args[0] is None: raise psycopg.OperationalError('simulada')
                    return retorno
            with patch.object(banco,'conectar',side_effect=lambda _:Conexao()):
                erro(psycopg.OperationalError,lambda:banco.importar(config,'pg-incerta',h,registros,CATEGORIAS,esquema))
            r=banco.consultar_recibo(config,'pg-incerta',esquema)
            exigir(r is not None and r['novas']==0 and r['retrato']['total']=='147.50')
        caso("PG consulta resolve confirmação perdida simulada após commit",confirmacao_perdida)
        # Restrições verificadas diretamente, sem a validação Python.
        for rotulo,ident,valor,sqlstate in [('negativo','D090',Decimal('-1.00'),'23514'),('nulo','D091',None,'23502'),('duplicado','D001',Decimal('12.50'),'23505')]:
            if motor['tipo'] != 'postgresql_nativo':
                CASOS.append({'nome':'PG restrição SQL '+rotulo,'status':'pendente_nativo',
                              'motivo':'O socket WASM não homologou a recuperação após erros SQL; testar no servidor nativo.'})
                continue
            def restricao(ident=ident,valor=valor,sqlstate=sqlstate):
                try:
                    with conectar(config) as con:
                        con.execute(sql.SQL('INSERT INTO {}.despesas VALUES (%s,%s,%s,%s,%s)').format(nome),(ident,date(2026,9,10),'Teste','Materiais',valor))
                except psycopg.Error as exc:
                    exigir(exc.sqlstate==sqlstate)
                    return
                raise AssertionError('Restrição não aplicada')
            caso('PG restrição SQL '+rotulo,restricao)
        if motor['tipo']=='postgresql_nativo':
            def autenticacao():
                invalida={**config,'password':uuid4().hex}
                try:
                    with conectar(invalida): pass
                except psycopg.OperationalError:
                    # Confirma que a rejeição não decorreu de indisponibilidade geral.
                    with conectar(config): pass
                    return
                raise AssertionError('Senha incorreta aceita')
            caso('PG rejeita senha incorreta com servidor disponível',autenticacao)
        else:
            CASOS.append({'nome':'PG autenticação nativa','status':'pendente_nativo'})
    finally:
        with conectar(config) as con:
            con.execute(sql.SQL('DROP SCHEMA IF EXISTS {} CASCADE').format(nome))
    return motor


def main():
    p=argparse.ArgumentParser(description=__doc__,color=False)
    p.add_argument('--com-banco',action='store_true')
    args=p.parse_args()
    motor=None
    with tempfile.TemporaryDirectory(prefix='tnp-cap11-') as temp:
        raiz=Path(temp)
        locais(raiz)
        if args.com_banco:
            try:
                motor=integracao(configuracao_banco(),raiz)
            except (psycopg.Error,ValueError,OSError,EOFError) as exc:
                CASOS.append({'nome':'Integração PostgreSQL disponível','status':'reprovado','tipo':type(exc).__name__})
    falhas=sum(c['status']=='reprovado' for c in CASOS)
    pendentes=sum(c['status']=='pendente_nativo' for c in CASOS)
    aprovados=sum(c['status']=='aprovado' for c in CASOS)
    status='reprovado' if falhas else 'pendente_postgresql_nativo' if pendentes else 'aprovado' if args.com_banco else 'aprovado_local'
    agora=datetime.now(timezone.utc)
    documento={'capitulo':11,'revisao':'R01','status':status,
        'modo':'integracao_nativa' if motor and motor['tipo']=='postgresql_nativo' else 'integracao_complementar_wasm' if motor else 'local_sem_banco',
        'data_utc':agora.isoformat(),'sistema':platform.system(),'plataforma':platform.platform(),
        'python':platform.python_version(),'psycopg':metadata.version('psycopg'),
        'total':len(CASOS),'aprovados':aprovados,'falhas':falhas,'pendentes':pendentes,
        'chamadas_ia_reais':0,'motor':motor,'casos':CASOS,'execucoes':EXECUCOES,
        'sha256_arquivos':json.loads((BASE/'MANIFESTO_SHA256.json').read_text()),
        'nota':'Testes de controle e integração não provam qualidade de modelo. Sem chamadas de IA. Uma execução ativa por vez.'}
    pasta=BASE/'resultados';pasta.mkdir(exist_ok=True)
    caminho=pasta/('relatorio-cap11-'+agora.strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    caminho.write_bytes(json_bytes(documento))
    print(status, str(aprovados)+'/'+str(len(CASOS)), 'falhas',falhas,'pendentes',pendentes)
    for c in CASOS:
        if c['status']!='aprovado': print(c['nome'],c['status'],c.get('tipo',''))
    print('Relatório:',caminho)
    return 1 if falhas else 0


if __name__=='__main__':
    raise SystemExit(main())
