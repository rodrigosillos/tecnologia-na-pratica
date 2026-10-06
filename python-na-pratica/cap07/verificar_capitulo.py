"""Testes locais e do SDK com transporte simulado. Não faz inferência real."""
import contextlib
import copy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from unittest.mock import patch

import httpx2
from openai import APIStatusError, APIConnectionError, APITimeoutError
from openai.types.responses import Response
from configuracao_ia import PASTA, MODELO, SDK, limite_saida, obter_chave
from contexto import preparar_pedido, pedido_exemplo, sha256_texto
from interpretacao import interpretar_resposta, uso_normalizado
from reproducao import carregar_caso, reproduzir, CASOS as NOMES_CASOS
from cliente_ia import criar_cliente, chamar_modelo, diagnosticar_erro
from execucao_real import executar_real, salvar_registro
from conferir_chamada_real import conferir

CASOS = []
EXECUCOES = []
CHAVE_FICTICIA = "chave-sintetica-sem-valor"


def igual(recebido, esperado):
    if recebido != esperado:
        raise AssertionError("Resultado diferente do gabarito: " + repr(recebido) + " / " + repr(esperado))


def exigir(condicao, texto):
    if not condicao:
        raise AssertionError(texto)


def rejeita(funcao, tipo=ValueError):
    try:
        funcao()
    except tipo:
        return
    raise AssertionError("Operação deveria ter sido recusada")


def caso(nome, funcao):
    try:
        evidencia = funcao()
        CASOS.append({"nome": nome, "status": "aprovado", "evidencia": evidencia})
    except Exception as erro:
        CASOS.append({"nome": nome, "status": "reprovado", "tipo": type(erro).__name__, "erro": str(erro)})


def cliente_simulado(handler):
    transporte = httpx2.MockTransport(handler)
    http = httpx2.Client(transport=transporte, trust_env=False)
    return criar_cliente(CHAVE_FICTICIA, http_client=http)


def resposta_base():
    return copy.deepcopy(carregar_caso("concluida")["resposta"])


def dependencias():
    for linha in (PASTA / "requirements.txt").read_text(encoding="utf-8").splitlines():
        nome, versao = linha.split("==")
        igual(importlib.metadata.version(nome), versao)


def conferir_cli(arquivo, argumentos, codigo, trechos):
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)
    env.pop("PYTHON_PRATICA_IA_MAX_SAIDA", None)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    processo = subprocess.run([sys.executable, str(PASTA / arquivo), *argumentos],
                             capture_output=True, text=True, encoding="utf-8", env=env, timeout=15)
    igual(processo.returncode, codigo)
    for trecho in trechos:
        exigir(trecho in processo.stdout, "Saída não contém: " + trecho)
    exigir(not processo.stderr, "Houve saída inesperada em stderr")
    EXECUCOES.append({"programa": arquivo, "argumentos": argumentos,
                      "exit": processo.returncode, "stdout": processo.stdout})


def testes():
    caso("Python 3.14", lambda: igual(sys.version_info[:2], (3, 14)))
    caso("Ambiente virtual", lambda: exigir(sys.prefix != sys.base_prefix, "Use a venv"))
    caso("Dependências fixadas", dependencias)
    with patch.dict(os.environ, {}, clear=True):
        caso("Saída padrão de 256 tokens", lambda: igual(limite_saida(), 256))
        caso("Chave ausente recusada sem revelar valor", lambda: rejeita(obter_chave))
    for valor in ["0", "31", "513", "muito", "2.5"]:
        with patch.dict(os.environ, {"PYTHON_PRATICA_IA_MAX_SAIDA": valor}):
            caso("Limite inválido " + valor, lambda: rejeita(limite_saida))
    for valor in ["32", "128", "512"]:
        with patch.dict(os.environ, {"PYTHON_PRATICA_IA_MAX_SAIDA": valor}):
            caso("Limite permitido " + valor, lambda v=valor: igual(limite_saida(), int(v)))
    for valor in ["", " ", " segredo", "segredo\n", "dois termos"]:
        with patch.dict(os.environ, {"OPENAI_API_KEY": valor}):
            caso("Chave vazia ou malformada " + repr(valor), lambda: rejeita(obter_chave))
    for texto in [None, 5, "", " \n", "a" * 3001]:
        caso("Entrada rejeitada " + str(type(texto).__name__) + " / " + str(len(texto) if isinstance(texto,str) else 0), lambda t=texto: rejeita(lambda: preparar_pedido(t)))
    caso("Entrada de 3000 caracteres aceita", lambda: exigir(preparar_pedido("a" * 3000)["input"].endswith("a" * 3000), "Entrada alterada"))
    pedido = pedido_exemplo()
    caso("Pedido tem snapshot e limite explícitos", lambda: igual((pedido["model"], pedido["max_output_tokens"]), (MODELO, 256)))
    caso("Pedido sem ferramentas, truncamento automático ou armazenamento solicitado", lambda: igual((pedido["tools"], pedido["truncation"], pedido["store"]), ([], "disabled", False)))
    caso("Pedido não contém chave ou estado de conversa", lambda: exigir(all(k not in pedido for k in ["api_key", "previous_response_id", "conversation"]), "Campo indevido no pedido"))
    for nome, esperado in [("concluida","concluida"),("incompleta","incompleta"),("recusada","recusada"),("sem_texto","sem_texto"),("sem_uso","uso_ausente"),("data_inventada","concluida")]:
        caso("Reprodução classifica " + nome, lambda n=nome,e=esperado: igual(reproduzir(n)["estado"], e))
        caso("Envelope sintético compatível com SDK: " + nome, lambda n=nome: exigir(isinstance(Response.model_validate(carregar_caso(n)["resposta"]), Response), "Envelope inválido"))
    for nome in ["incompleta", "recusada", "sem_texto", "sem_uso"]:
        caso("Resultado pendente não libera texto: " + nome, lambda n=nome: igual(reproduzir(n)["texto"], None))
    caso("Estado técnico não aprova data inventada", lambda: exigir("10/09/2026" in reproduzir("data_inventada")["texto"] and "10/09/2026" not in pedido["input"], "Desafio não demonstra divergência semântica"))
    caso("Caso desconhecido não escolhe arquivo arbitrário", lambda: rejeita(lambda: carregar_caso("../segredo")))
    for uso in [None, {}, {"input_tokens":True,"output_tokens":1,"total_tokens":2}, {"input_tokens":1,"output_tokens":-1,"total_tokens":0}, {"input_tokens":1,"output_tokens":2,"total_tokens":9}]:
        caso("Uso inválido recusado " + repr(uso), lambda u=uso: igual(uso_normalizado(u), None))
    for estado in ["queued", "in_progress", "cancelled", "failed"]:
        r=resposta_base();r["status"]=estado
        caso("Status sem conclusão: " + estado, lambda v=r: igual(interpretar_resposta(v)["estado"], "nao_concluida"))
    for nome, mutacao in [
        ("output não é lista", lambda r:r.update(output={})),
        ("papel inesperado", lambda r:r["output"][0].update(role="user")),
        ("mensagem incompleta", lambda r:r["output"][0].update(status="incomplete")),
        ("conteúdo inválido", lambda r:r["output"][0].update(content="texto")),
        ("ferramenta inesperada", lambda r:r["output"].append({"type":"function_call","name":"executar_sql"})),
        ("texto não textual", lambda r:r["output"][0]["content"][0].update(text=123)),
        ("erro junto de completed", lambda r:r.update(error={"code":"falha"})),
    ]:
        r=resposta_base();mutacao(r)
        caso("Envelope bloqueado: " + nome, lambda v=r: igual(interpretar_resposta(v)["estado"], "resposta_invalida"))
    r=resposta_base();r["output"][0]["content"].append({"type":"refusal","refusal":"sintética"})
    caso("Recusa prevalece sobre trecho de texto",lambda:igual(interpretar_resposta(r)["estado"],"recusada"))

    capturados=[]
    def sucesso(req):
        capturados.append(req)
        return httpx2.Response(200,json=resposta_base())
    with cliente_simulado(sucesso) as cli:
        caso("SDK sem retries e com timeout explícito",lambda:igual((cli.max_retries,cli.timeout),(0,30.0)))
        r=chamar_modelo(cli,pedido)
    caso("SDK faz uma requisição",lambda:igual(len(capturados),1))
    req=capturados[0]
    caso("SDK usa endpoint oficial Responses",lambda:igual(str(req.url),"https://api.openai.com/v1/responses"))
    caso("SDK serializa exatamente o pedido",lambda:igual(json.loads(req.content),pedido))
    caso("SDK envia chave em cabeçalho e não no contexto",lambda:exigir(req.headers.get("authorization")=="Bearer "+CHAVE_FICTICIA and CHAVE_FICTICIA not in req.content.decode(),"Autenticação ou separação incorreta"))
    caso("SDK devolve resposta interpretável",lambda:igual(interpretar_resposta(r)["estado"],"concluida"))

    for status,code,trecho in [(400,"invalid_request","requisição recusada"),(401,"invalid_api_key","autenticação recusada"),(403,"permission_denied","acesso não permitido"),(404,"model_not_found","modelo indisponível"),(429,"insufficient_quota","saldo ou quota"),(429,"rate_limit_exceeded","limite ou quota"),(500,"server_error","falha no serviço")]:
        def testar_http(s=status,c=code,t=trecho):
            vezes=[]
            def handler(req):
                vezes.append(1)
                return httpx2.Response(s,json={"error":{"message":"NÃO_EXIBIR_CORPO_NEM_SEGREDO","type":"erro_sintetico","code":c}})
            with cliente_simulado(handler) as cli:
                try:chamar_modelo(cli,pedido)
                except APIStatusError as erro:diagnostico=diagnosticar_erro(erro)
                else:raise AssertionError("HTTP de erro não foi rejeitado")
            igual(len(vezes),1)
            exigir(t in diagnostico and "NÃO_EXIBIR" not in diagnostico,"Diagnóstico incorreto ou corpo exposto")
        caso("SDK trata HTTP " + str(status) + " / " + code + " sem retry",testar_http)
    for tipo,trecho in [(httpx2.ReadTimeout,"tempo de espera"),(httpx2.ConnectError,"falha de comunicação")]:
        def testar_transporte(tipo=tipo,trecho=trecho):
            vezes=[]
            def handler(req):
                vezes.append(1);raise tipo("NÃO_EXIBIR_SEGREDO",request=req)
            with cliente_simulado(handler) as cli:
                try:chamar_modelo(cli,pedido)
                except (APITimeoutError,APIConnectionError) as erro:msg=diagnosticar_erro(erro)
                else:raise AssertionError("Erro não foi propagado pelo SDK")
            igual(len(vezes),1);exigir(trecho in msg and "NÃO_EXIBIR" not in msg,"Mensagem indevida")
        caso("SDK trata transporte: "+tipo.__name__,testar_transporte)

    with tempfile.TemporaryDirectory() as temp:
        pasta=Path(temp);contador=[]
        def fabrica(chave):
            contador.append(1)
            return cliente_simulado(sucesso)
        with patch.dict(os.environ,{"OPENAI_API_KEY":CHAVE_FICTICIA}):
            with contextlib.redirect_stdout(io.StringIO()):
                codigo=executar_real(False,pasta,fabrica)
            caso("Modo real exige confirmação explícita",lambda:igual((codigo,len(contador),list(pasta.iterdir())),(2,0,[])))
            with contextlib.redirect_stdout(io.StringIO()):codigo=executar_real(True,pasta,fabrica)
        arquivos=list(pasta.glob('chamada-real-*.json'))
        caso("Fluxo simulado salva uma resposta sem segunda tentativa",lambda:igual((codigo,len(contador),len(arquivos)),(0,1,1)))
        bruto=arquivos[0].read_text(encoding="utf-8");registro=json.loads(bruto)
        caso("Registro UTF-8 não inclui chave nem cabeçalhos",lambda:exigir(CHAVE_FICTICIA not in bruto and 'authorization' not in bruto and 'reunião' in bruto,"Registro contém segredo ou perdeu acentos"))
        caso("Registro preserva revisão humana pendente",lambda:igual(registro["revisao_do_conteudo"],"pendente"))
        caso("Conferência rejeita identificador sintético",lambda:rejeita(lambda:conferir(registro)))
        # Documento fabricado somente para testar o conferidor, não entregue como evidência real.
        fabricado=copy.deepcopy(registro);fabricado['resposta']['id']='resp_fixture_apenas_teste'
        caso("Conferidor valida forma, sem comprovar origem por si só",lambda:igual(conferir(fabricado)["estado"],"concluida"))
        for campo,valor in [('modo','reproducao'),('tentativas_sdk',2),('sdk_openai','0.0'),('input_sha256','divergente')]:
            alterado=copy.deepcopy(fabricado);alterado[campo]=valor
            caso("Conferidor bloqueia divergência em "+campo,lambda a=alterado:rejeita(lambda:conferir(a)))
        antigo=arquivos[0].read_bytes();salvar_registro(registro,pasta)
        caso("Novo registro preserva anterior",lambda:exigir(len(list(pasta.glob('chamada-real-*.json')))==2 and arquivos[0].read_bytes()==antigo,"Registro anterior alterado"))
        bloqueio=pasta/'arquivo';bloqueio.write_text('preservar',encoding='utf-8')
        with patch.dict(os.environ,{"OPENAI_API_KEY":CHAVE_FICTICIA}):
            with contextlib.redirect_stdout(io.StringIO()) as saida:codigo=executar_real(True,bloqueio,fabrica)
        caso("Falha ao salvar não repete chamada",lambda:igual((codigo,len(contador)),(3,2)))
        caso("Falha ao salvar explica tentativa já ocorrida",lambda:exigir("A tentativa já ocorreu" in saida.getvalue(),"Diagnóstico não protege contra reenvio"))

    for arquivo,args,codigo,trechos in [
        ('01_inspecionar_contexto.py',[],0,['Nenhuma chamada','Chave: ausente']),
        ('02_reproduzir.py',[],0,['origem: sintética','Estado: concluida','data não foi informada']),
        ('02_reproduzir.py',['--caso','incompleta'],2,['Estado: incompleta']),
        ('02_reproduzir.py',['--caso','recusada'],2,['Estado: recusada']),
        ('02_reproduzir.py',['--caso','sem_texto'],2,['Estado: sem_texto']),
        ('02_reproduzir.py',['--caso','sem_uso'],2,['Estado: uso_ausente']),
        ('03_chamada_real.py',[],2,['API real desativada']),
        ('03_chamada_real.py',['--confirmar-envio'],1,['OPENAI_API_KEY não configurada']),
        ('04_comparar_respostas.py',[],0,['10/09/2026','não informa data']),
        ('solucao_desafio.py',[],0,['Pode aceitar como resposta concluída: False','Texto aceito: None']),
    ]:
        caso('Programa '+arquivo+' '+' '.join(args),lambda a=arquivo,b=args,c=codigo,d=trechos:conferir_cli(a,b,c,d))


def main():
    # Os testes escolhem seus próprios limites e nunca usam a chave do leitor.
    with patch.dict(os.environ,{"PYTHON_PRATICA_IA_MAX_SAIDA":"256"}):
        testes()
    arquivos=sorted(p for p in PASTA.rglob('*') if p.is_file() and '__pycache__' not in p.parts and
                    (p.suffix in {'.py','.ps1'} or p.parent.name in {'casos','entradas','prompts'} or p.name=='requirements.txt'))
    hashes={p.relative_to(PASTA).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in arquivos}
    caso('Integridade das fontes e casos',lambda:igual(hashes,json.loads((PASTA/'MANIFESTO_SHA256.json').read_text(encoding='utf-8'))))
    falhas=[c for c in CASOS if c['status']=='reprovado']
    relatorio={"capitulo":7,"revisao":"R01","status":"reprovado" if falhas else "aprovado_local",
               "modo":"local_com_sdk_e_transporte_simulado","data_utc":datetime.now(timezone.utc).isoformat(),
               "sistema":platform.system(),"plataforma":platform.platform(),"python":platform.python_version(),
               "sdk_openai":importlib.metadata.version('openai'),"modelo_fixado":MODELO,
               "total":len(CASOS),"aprovados":len(CASOS)-len(falhas),"falhas":len(falhas),
               "chamadas_reais":0,"integracao_real":"pendente","casos":CASOS,"execucoes":EXECUCOES,"sha256_arquivos":hashes,
               "nota_console":"Subprocessos capturados em UTF-8; legibilidade do console deve ser conferida manualmente."}
    pasta=PASTA/'resultados';pasta.mkdir(exist_ok=True)
    caminho=pasta/('relatorio-cap07-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
    with caminho.open('x',encoding='utf-8') as f:json.dump(relatorio,f,ensure_ascii=False,indent=2)
    print('Status:',relatorio['status'])
    print('Verificações:',str(relatorio['aprovados'])+'/'+str(relatorio['total']))
    print('Chamadas reais: 0 | Integração real: pendente')
    print('Relatório:',caminho)
    for c in falhas:print('FALHA:',c['nome'],c.get('erro'))
    return 1 if falhas else 0


if __name__=='__main__':
    raise SystemExit(main())
