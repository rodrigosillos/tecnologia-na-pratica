"""Verificação local: não faz inferência, não lê a chave do leitor e não usa banco."""
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
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
import httpx2
from openai.types.responses import Response
from configuracao_ia import PASTA, MODELO, limite_saida
from arquivos import decodificar, ler_json, serializar, resumo, gravar_conjunto
from contexto import origens, categorias, preparar_pedido
from contrato_ia import validar_estrutura, formato_resposta
from validacao import analisar, conferir_campos
from fluxo import preparar_reproducao, conferir_pacote, modelo_revisao, revisar, montar_pacote
from cliente_ia import criar_cliente
from execucao_real import executar_real
from regras import validar_lote

CASOS = []
EXECUCOES = []


def exigir(condicao, mensagem="Resultado diferente do esperado"):
    if not condicao:
        raise AssertionError(mensagem)


def recusa(funcao, trecho=None):
    try:
        funcao()
    except ValueError as erro:
        if trecho:
            exigir(trecho in str(erro))
        return
    raise AssertionError("Esperava ValueError")


def teste(nome, funcao):
    try:
        funcao()
        CASOS.append({"nome": nome, "status": "aprovado"})
    except Exception as erro:
        CASOS.append({"nome": nome, "status": "falhou",
                      "diagnostico": type(erro).__name__ + ": " + str(erro)})


def executar():
    pacote = preparar_reproducao()
    revisao = ler_json(PASTA / "revisoes/decisoes_exemplo.json")
    fontes = origens()
    nomes = categorias()
    base = conferir_pacote(pacote)["T002"]["sugestao"]

    teste("Python 3.14 e ambiente virtual", lambda: exigir(sys.version_info[:2] == (3, 14) and sys.prefix != sys.base_prefix))
    def dependencias():
        for linha in (PASTA / "requirements.txt").read_text().splitlines():
            if linha.strip() and not linha.startswith("#"):
                nome, versao = linha.split("==")
                exigir(importlib.metadata.version(nome) == versao, "Versão divergente: " + nome)
    teste("Dependências fixadas", dependencias)
    teste("Três origens e IDs controlados pela aplicação", lambda: exigir([r["id_destino"] for r in fontes.values()] == ["D101", "D102", "D103"]))
    teste("Esquema não solicita ID ou aprovação", lambda: exigir(not {"id", "aprovado"} & set(formato_resposta()["schema"]["properties"])))
    def esquema_estrito():
        esquema = formato_resposta()["schema"]
        for obj in [esquema, *esquema["$defs"].values()]:
            exigir(obj["additionalProperties"] is False)
            exigir(set(obj["required"]) == set(obj["properties"]))
        exigir(formato_resposta()["strict"] is True)
    teste("Esquema exige campos e proíbe extras, inclusive nas evidências", esquema_estrito)
    teste("Campos ausentes representados por null", lambda: exigir(conferir_pacote(pacote)["T001"]["sugestao"]["data"] is None))
    teste("Data ausente mantém pendência", lambda: exigir(conferir_pacote(pacote)["T001"]["pendencias"] == ["data"]))
    teste("Categoria ambígua mantém pendência", lambda: exigir(conferir_pacote(pacote)["T003"]["pendencias"] == ["categoria"]))
    teste("Sugestão completa ainda aguarda revisão", lambda: exigir(conferir_pacote(pacote)["T002"]["estado"] == "aguarda_revisao"))
    for entrada in ['{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}', '{"x":', '[' * 1100]:
        teste("JSON rejeitado: " + entrada[:24], lambda t=entrada: recusa(lambda: decodificar(t)))
    for campo, valor in [("valor", 18.5), ("data", 20260912), ("categoria", "Outros"), ("descricao", True), ("valor", False)]:
        def forma(c=campo, v=valor):
            alterada = deepcopy(base); alterada[c] = v
            recusa(lambda: validar_estrutura(serializar(alterada)))
        teste("Esquema bloqueia tipo/categoria em " + campo + " / " + repr(valor), forma)
    for onde in ["raiz", "evidencias"]:
        def extra(lugar=onde):
            s = deepcopy(base)
            (s if lugar == "raiz" else s["evidencias"])["id"] = "D999"
            recusa(lambda: validar_estrutura(serializar(s)))
        teste("Esquema bloqueia campo extra: " + onde, extra)
    teste("Esquema bloqueia campo omitido", lambda: recusa(lambda: validar_estrutura(serializar({k: v for k, v in base.items() if k != "data"}))))
    for nome, resposta in [(i["origem_id"], i["resposta"]) for i in pacote["itens"]]:
        teste("Caso sintético compatível com SDK: " + nome, lambda r=resposta: Response.model_validate(r))
    for caso in ler_json(PASTA / "casos/erros.json"):
        esperado = "aguarda_revisao" if caso["nome"] in {"categoria_sem_suporte", "subtotal_como_total"} else "bloqueada"
        teste("Contraste: " + caso["nome"], lambda c=caso, e=esperado: exigir(analisar(c["resposta"], fontes[c["origem_id"]]["texto"], nomes)["estado"] == e))
    for valor in ["0.00", "-1.00", "NaN", "Infinity", "18.500", "18,50", "10000000.00"]:
        def dominio(v=valor):
            s = deepcopy(base); s["valor"] = v
            exigir(bool(conferir_campos(s, fontes["T002"]["texto"], nomes)["erros"]))
        teste("Valor fora do domínio: " + valor, dominio)
    def evidencia_nula():
        s = deepcopy(base); s["data"] = None
        exigir(bool(conferir_campos(s, fontes["T002"]["texto"], nomes)["erros"]))
    teste("Valor null não aceita evidência preenchida", evidencia_nula)
    def data_divergente():
        s = deepcopy(base); s["data"] = "2026-09-13"
        exigir(bool(conferir_campos(s, fontes["T002"]["texto"], nomes)["erros"]))
    teste("Data válida, mas diferente do trecho, bloqueada", data_divergente)
    def descricao_alterada():
        s = deepcopy(base); s["descricao"] = "Compra de computador"
        exigir(bool(conferir_campos(s, fontes["T002"]["texto"], nomes)["erros"]))
    teste("Descrição não pode acrescentar fatos ao trecho", descricao_alterada)

    def revisao_ok():
        lote, trilha = revisar(pacote, revisao)
        exigir(len(lote) == 2 and trilha["rejeitados"] == 1 and trilha["total_lote_revisado"] == "53.50")
        exigir(lote[0]["id"] == "D101" and lote[0]["data"] == "2026-09-11")
        exigir(lote[1]["id"] == "D102" and lote[1]["valor"] == "18.50")
        exigir(trilha["persistencia"] == "nao_executada")
        exigir(not validar_lote(lote, nomes)["erros"])
        exigir(trilha["decisoes"][0]["original"]["data"] is None)
        exigir(trilha["decisoes"][0]["complemento"]["id"] == "mensagem_T001")
    teste("Correção, aceite e rejeição: dois registros / 53.50 / contrato cap06", revisao_ok)
    def preserva():
        p, r = deepcopy(pacote), deepcopy(revisao)
        revisar(pacote, revisao)
        exigir(pacote == p and revisao == r)
    teste("Revisar não altera entrada nem sugestão original", preserva)
    teste("Revisão pendente bloqueia exportação", lambda: recusa(lambda: revisar(pacote, modelo_revisao(pacote))))
    teste("Aceite não resolve data ausente", lambda: recusa(lambda: revisar(pacote, ler_json(PASTA / "revisoes/aceite_invalido.json")), "data"))
    def rejeitar_todos():
        r = deepcopy(revisao)
        for d in r["decisoes"]:
            d.update(acao="rejeitar", correcoes={}, complemento=None)
        lote, trilha = revisar(pacote, r)
        exigir(lote == [] and trilha["total_lote_revisado"] == "0.00" and trilha["rejeitados"] == 3)
    teste("Todas rejeitadas geram lote vazio sem despesa inventada", rejeitar_todos)
    mutacoes = [
        ("revisor vazio", lambda r: r.update(revisor="")),
        ("hash de outro pacote", lambda r: r.update(pacote_sha256="0" * 64)),
        ("decisão omitida", lambda r: r["decisoes"].pop()),
        ("decisão duplicada", lambda r: r["decisoes"].__setitem__(1, deepcopy(r["decisoes"][0]))),
        ("origem desconhecida", lambda r: r["decisoes"][0].update(origem_id="T999")),
        ("ação pendente", lambda r: r["decisoes"][1].update(acao="pendente")),
        ("ação tipo inválido", lambda r: r["decisoes"][1].update(acao=[])),
        ("motivo vazio", lambda r: r["decisoes"][1].update(motivo="")),
        ("correção oculta no aceite", lambda r: r["decisoes"][1].update(correcoes={"valor": {"valor": "1.00", "trecho": "R$ 1,00"}})),
        ("correção de id proibida", lambda r: r["decisoes"][0]["correcoes"].update(id={"valor": "D999", "trecho": "D999"})),
        ("complemento desconhecido", lambda r: r["decisoes"][0].update(complemento="../../segredo")),
        ("data corrigida sem fonte complementar", lambda r: r["decisoes"][0].update(complemento=None)),
        ("data corrigida divergente do complemento", lambda r: r["decisoes"][0]["correcoes"]["data"].update(valor="2026-09-12")),
        ("correção sem campos", lambda r: r["decisoes"][0].update(correcoes={})),
        ("versão bool recusada", lambda r: r.update(versao=True)),
    ]
    for nome, mutar in mutacoes:
        def mutacao(m=mutar):
            r = deepcopy(revisao); m(r)
            recusa(lambda: revisar(pacote, r))
        teste("Revisão bloqueada: " + nome, mutacao)
    for nome, mutar in [
        ("hash de contexto", lambda p: p["itens"][0].update(pedido_sha256="0" * 64)),
        ("origem repetida", lambda p: p["itens"].__setitem__(1, deepcopy(p["itens"][0]))),
        ("modo inválido", lambda p: p.update(modo=[])),
        ("sintético rotulado como real", lambda p: p.update(modo="api_real", origem="execucao_sdk")),
    ]:
        def adulterado(m=mutar):
            p = deepcopy(pacote); m(p)
            recusa(lambda: conferir_pacote(p))
        teste("Pacote bloqueado: " + nome, adulterado)
    def corrigir_categoria():
        p = deepcopy(pacote)
        erro = next(c for c in ler_json(PASTA / "casos/erros.json") if c["nome"] == "categoria_sem_suporte")
        p["itens"][1]["resposta"] = erro["resposta"]
        r = deepcopy(revisao); r["pacote_sha256"] = resumo(p)
        r["decisoes"][1].update(acao="corrigir", correcoes={"categoria": {"valor": "Alimentação", "trecho": "Café e lanche"}})
        lote, trilha = revisar(p, r)
        exigir(lote[1]["categoria"] == "Alimentação")
        exigir(trilha["decisoes"][1]["original"]["categoria"] == "Materiais")
    teste("Revisor corrige categoria com trilha original/final", corrigir_categoria)
    def invalido_nao_passa():
        p = deepcopy(pacote); p["itens"][1]["resposta"]["status"] = "incomplete"
        r = deepcopy(revisao); r["pacote_sha256"] = resumo(p)
        recusa(lambda: revisar(p, r), "bloqueada")
    teste("Aceite não contorna resposta incompleta", invalido_nao_passa)
    def rejeita_bloqueada():
        p = deepcopy(pacote); p["itens"][1]["resposta"]["status"] = "incomplete"
        r = deepcopy(revisao); r["pacote_sha256"] = resumo(p)
        r["decisoes"][1]["acao"] = "rejeitar"
        lote, trilha = revisar(p, r)
        exigir(len(lote) == 1 and trilha["total_lote_revisado"] == "35.00")
    teste("Revisor pode rejeitar item bloqueado sem aceitar seu conteúdo", rejeita_bloqueada)

    with TemporaryDirectory(prefix="cap08-verificacao-") as tmp:
        raiz = Path(tmp)
        def grava():
            dest = raiz / "unicode"
            gravar_conjunto(dest, {"exemplo.json": {"texto": "Revisão — alimentação"}})
            exigir(ler_json(dest / "exemplo.json")["texto"] == "Revisão — alimentação")
            recusa(lambda: gravar_conjunto(dest, {"exemplo.json": {"texto": "alterado"}}), "já existe")
            exigir(ler_json(dest / "exemplo.json")["texto"] == "Revisão — alimentação")
        teste("Gravação UTF-8 preserva pasta existente", grava)
        def falha_gravar():
            dest = raiz / "invalida"
            recusa(lambda: gravar_conjunto(dest, {"ok.json": {}, "../escape.json": {}}))
            exigir(not dest.exists() and not (raiz / "escape.json").exists())
        teste("Falha no conjunto não publica lote parcial", falha_gravar)
        def real_sem_confirmacao():
            with patch.dict(os.environ, {"OPENAI_API_KEY": "chave_ficticia_cap08"}):
                codigo = executar_real("T001", raiz / "sem-envio", False, lambda _: (_ for _ in ()).throw(AssertionError("Cliente criado")))
            exigir(codigo == 2 and not (raiz / "sem-envio").exists())
        teste("Chave presente não autoriza envio sozinha", real_sem_confirmacao)
        def real_sem_chave():
            with patch.dict(os.environ):
                os.environ.pop("OPENAI_API_KEY", None)
                exigir(executar_real("T001", raiz / "sem-chave", True) == 1)
            exigir(not (raiz / "sem-chave").exists())
        teste("Modo real sem chave bloqueia antes do SDK", real_sem_chave)
        def sdk_estruturado():
            chamadas = []
            resposta = deepcopy(pacote["itens"][0]["resposta"])
            resposta["id"] = "resp_mock_transporte_cap08"
            def handler(req):
                chamadas.append(req)
                corpo = json.loads(req.content)
                exigir(corpo == preparar_pedido(fontes["T001"]))
                exigir(corpo["text"]["format"]["strict"] is True)
                exigir("chave_ficticia_cap08" not in req.content.decode())
                return httpx2.Response(200, json=resposta)
            def fabrica(chave):
                return criar_cliente(chave, httpx2.Client(transport=httpx2.MockTransport(handler)))
            dest = raiz / "sdk"
            with patch.dict(os.environ, {"OPENAI_API_KEY": "chave_ficticia_cap08"}):
                exigir(executar_real("T001", dest, True, fabrica) == 0)
            exigir(len(chamadas) == 1)
            p = ler_json(dest / "pacote.json")
            exigir(conferir_pacote(p)["T001"]["pendencias"] == ["data"])
            exigir(ler_json(dest / "revisao_pendente.json")["decisoes"][0]["acao"] == "pendente")
            for path in dest.glob("*.json"):
                exigir("chave_ficticia_cap08" not in path.read_text(encoding="utf-8"))
            with patch.dict(os.environ, {"OPENAI_API_KEY": "chave_ficticia_cap08"}):
                exigir(executar_real("T001", dest, True, fabrica) == 1)
            exigir(len(chamadas) == 1, "Destino existente provocou segunda chamada")
        teste("SDK envia esquema, salva sugestão pendente e não reenvia para pasta existente", sdk_estruturado)
        def sdk_quota():
            contagem = []
            def handler(req):
                contagem.append(1)
                return httpx2.Response(429, json={"error": {"code": "insufficient_quota", "message": "conteudo_sigilo_teste", "type": "insufficient_quota"}})
            fabrica = lambda chave: criar_cliente(chave, httpx2.Client(transport=httpx2.MockTransport(handler)))
            dest = raiz / "quota"
            with patch.dict(os.environ, {"OPENAI_API_KEY": "chave_ficticia_cap08"}):
                exigir(executar_real("T001", dest, True, fabrica) == 1)
            exigir(len(contagem) == 1 and not (dest / "pacote.json").exists())
            exigir("conteudo_sigilo_teste" not in (dest / "metadados.json").read_text())
        teste("Quota simulada: uma tentativa, diagnóstico sem corpo bruto e sem fallback", sdk_quota)
        def sdk_falha_local():
            chamadas = []
            resposta = deepcopy(pacote["itens"][0]["resposta"]); resposta["id"] = "resp_mock_falha_gravacao"
            def handler(req):
                chamadas.append(1)
                return httpx2.Response(200, json=resposta)
            fabrica = lambda chave: criar_cliente(chave, httpx2.Client(transport=httpx2.MockTransport(handler)))
            with patch.dict(os.environ, {"OPENAI_API_KEY": "chave_ficticia_cap08"}):
                with patch("execucao_real.gravar_conjunto", side_effect=OSError("disco")):
                    exigir(executar_real("T001", raiz / "sem-arquivo", True, fabrica) == 3)
            exigir(len(chamadas) == 1)
        teste("Falha após resposta não repete inferência simulada", sdk_falha_local)
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None); env.pop("PYTHON_PRATICA_IA_MAX_SAIDA", None)
        env["PYTHONIOENCODING"] = "utf-8"
        pasta = raiz / "cli"
        def cli(nome, args, esperado):
            def rodar():
                r = subprocess.run([sys.executable, str(PASTA / nome), *map(str, args)], env=env, capture_output=True, text=True, encoding="utf-8", timeout=30)
                EXECUCOES.append({"programa": nome, "argumentos": list(map(str, args)), "exit": r.returncode, "stdout": r.stdout, "stderr": r.stderr})
                exigir(r.returncode == esperado, r.stdout + r.stderr)
            teste("CLI " + nome + " / exit " + str(esperado), rodar)
        cli("01_preparar.py", ["--destino", pasta], 0)
        cli("01_preparar.py", ["--destino", pasta], 1)
        cli("02_inspecionar.py", ["--pacote", pasta / "pacote.json"], 0)
        cli("03_revisar.py", ["--pacote", pasta / "pacote.json", "--revisao", PASTA / "revisoes/aceite_invalido.json", "--destino", raiz / "negado"], 1)
        teste("CLI inválida não criou lote", lambda: exigir(not (raiz / "negado").exists()))
        cli("03_revisar.py", ["--pacote", pasta / "pacote.json", "--revisao", pasta / "revisao_pendente.json", "--destino", raiz / "pendente"], 1)
        cli("03_revisar.py", ["--pacote", pasta / "pacote.json", "--revisao", PASTA / "revisoes/decisoes_exemplo.json", "--destino", raiz / "revisado"], 0)
        cli("03_revisar.py", ["--pacote", pasta / "pacote.json", "--revisao", PASTA / "revisoes/decisoes_exemplo.json", "--destino", raiz / "revisado"], 1)
        cli("04_extrair_real.py", ["--destino", raiz / "api"], 2)
        cli("04_extrair_real.py", ["--destino", raiz / "api", "--confirmar-envio"], 1)
        cli("05_examinar_erros.py", [], 0)
        cli("solucao_desafio.py", [], 0)
    hashes = {nome: hashlib.sha256((PASTA / nome).read_bytes()).hexdigest() for nome in ler_json(PASTA / "MANIFESTO_SHA256.json")}
    teste("Integridade das fontes e casos", lambda: exigir(hashes == ler_json(PASTA / "MANIFESTO_SHA256.json")))
    return hashes


def main():
    with patch.dict(os.environ):
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("PYTHON_PRATICA_IA_MAX_SAIDA", None)
        with redirect_stdout(io.StringIO()):
            hashes = executar()
    falhas = sum(c["status"] != "aprovado" for c in CASOS)
    relatorio = {"capitulo": 8, "revisao": "R01", "status": "aprovado_local" if not falhas else "reprovado",
                 "modo": "local_com_sdk_e_transporte_simulado", "data_utc": datetime.now(timezone.utc).isoformat(),
                 "sistema": platform.system(), "plataforma": platform.platform(), "python": platform.python_version(),
                 "sdk_openai": importlib.metadata.version("openai"), "modelo_fixado": MODELO,
                 "total": len(CASOS), "aprovados": len(CASOS) - falhas, "falhas": falhas,
                 "chamadas_reais": 0, "integracao_real": "nao_executada_opcional", "persistencia": "nao_executada",
                 "casos": CASOS, "execucoes": EXECUCOES, "sha256_arquivos": hashes,
                 "nota_console": "Subprocessos capturados em UTF-8; apresentação cp850 deve ser registrada separadamente."}
    destino = PASTA / "resultados"
    destino.mkdir(exist_ok=True)
    path = destino / ("relatorio-cap08-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    path.write_text(serializar(relatorio), encoding="utf-8")
    print(f"{relatorio['status']}: {relatorio['aprovados']}/{relatorio['total']} | falhas: {falhas}")
    print("Chamadas reais: 0 | integração autenticada: opcional, não executada | banco: não utilizado")
    print("Relatório:", path)
    for caso in CASOS:
        if caso["status"] != "aprovado":
            print(caso["nome"], caso.get("diagnostico"))
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
