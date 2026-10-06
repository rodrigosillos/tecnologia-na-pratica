"""Verificação por contratos e resultados, incluindo HTTP real em loopback.
Execute com a .venv do livro. Não usa serviços externos nem modelos de IA.
"""
import contextlib
import copy
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
import threading

sys.dont_write_bytecode = True
PASTA = Path(__file__).resolve().parent
if str(PASTA) not in sys.path:
    sys.path.insert(0, str(PASTA))
from aplicacao import executar
from arquivos import ler_csv, ler_json
from calculos import somar_valores
from cliente_catalogo import obter_catalogo, validar_url_local
from contrato_catalogo import validar_catalogo
from regras import converter_data, converter_valor, validar_lote
from servidor_catalogo import criar_servidor

CASOS = []
PROGRAMAS = []
CATS = ["Alimentação", "Transporte", "Materiais"]
DOC = {"versao": 1, "categorias": CATS}


def igual(recebido, esperado):
    if recebido != esperado:
        raise AssertionError("Recebido: " + repr(recebido) + "; esperado: " + repr(esperado))


def exigir(condicao, mensagem):
    if not condicao:
        raise AssertionError(mensagem)


def rejeita(funcao, trecho):
    try:
        funcao()
    except ValueError as erro:
        exigir(trecho in str(erro), "Mensagem inesperada: " + str(erro))
        return str(erro)
    raise AssertionError("Entrada indevida foi aceita")


def caso(nome, funcao):
    try:
        evidencia = funcao()
        CASOS.append({"nome": nome, "status": "aprovado", "evidencia": evidencia})
    except Exception as erro:
        CASOS.append({"nome": nome, "status": "reprovado", "erro": repr(erro)})


def catalogo_sem_mutacao():
    original = copy.deepcopy(DOC)
    recebidas = validar_catalogo(original)
    recebidas.append("Outra")
    igual(original, DOC)


def verifica_lote(nome, quantidade, repetidos, total=None, erros=None):
    leitor = ler_csv if nome.endswith(".csv") else ler_json
    entrada = leitor(PASTA / "dados" / nome)
    copia = copy.deepcopy(entrada)
    resultado = validar_lote(entrada, CATS)
    igual(entrada, copia)
    igual(len(resultado["despesas"]), quantidade)
    igual(resultado["repetidos"], repetidos)
    if erros is not None:
        igual(resultado["erros"], erros)
    else:
        igual(resultado["erros"], [])
    if total is not None:
        igual(somar_valores([d["valor"] for d in resultado["despesas"]]), Decimal(total))


def app(caminho, url):
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        codigo = executar(caminho, url)
    return codigo, saida.getvalue()


def programa(arquivo, argumentos, codigo, linhas):
    ambiente = os.environ.copy()
    ambiente.update(PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1",
                    PYTHON_COLORS="0", PYTHON_PRATICA_API_URL=BASE)
    with tempfile.TemporaryDirectory() as outro_diretorio:
        resultado = subprocess.run(
            [sys.executable, str(PASTA / arquivo)] + argumentos,
            cwd=outro_diretorio, env=ambiente, capture_output=True,
            encoding="utf-8", timeout=15,
        )
    PROGRAMAS.append({"arquivo": arquivo, "argumentos": argumentos,
                      "exit": resultado.returncode, "stdout": resultado.stdout,
                      "stderr": resultado.stderr})
    igual(resultado.returncode, codigo)
    igual(resultado.stdout.splitlines(), linhas)
    igual(resultado.stderr, "")


def dependencias():
    obtidas = {}
    for linha in (PASTA / "requirements.txt").read_text(encoding="utf-8").splitlines():
        nome, versao = linha.split("==")
        obtidas[nome] = importlib.metadata.version(nome)
        igual(obtidas[nome], versao)
    return obtidas


caso("Ambiente: Python 3.14", lambda: igual(sys.version_info[:2], (3, 14)))
caso("Ambiente: executando em ambiente virtual", lambda: exigir(sys.prefix != sys.base_prefix, "Use a .venv"))
caso("Ambiente: dependências fixadas", dependencias)
caso("Catálogo: três nomes esperados", lambda: igual(validar_catalogo(DOC), CATS))
caso("Catálogo: entrada preservada e retorno independente", catalogo_sem_mutacao)
for nome, documento, mensagem in [
    ("raiz lista", [], "objeto"),
    ("raiz nula", None, "objeto"),
    ("ausência de versão", {"categorias": CATS}, "campos"),
    ("ausência de categorias", {"versao": 1}, "campos"),
    ("campo adicional", dict(DOC, segredo="x"), "campos"),
    ("versão futura", dict(DOC, versao=2), "versão"),
    ("versão texto", dict(DOC, versao="1"), "versão"),
    ("versão decimal", dict(DOC, versao=1.0), "versão"),
    ("versão booleana", dict(DOC, versao=True), "versão"),
    ("lista vazia", dict(DOC, categorias=[]), "1 a 20"),
    ("lista excessiva", dict(DOC, categorias=[str(i) for i in range(21)]), "1 a 20"),
    ("categorias texto", dict(DOC, categorias="Transporte"), "1 a 20"),
    ("categorias nulas", dict(DOC, categorias=None), "1 a 20"),
    ("item inteiro", dict(DOC, categorias=[1]), "informe texto"),
    ("item booleano", dict(DOC, categorias=[False]), "informe texto"),
    ("item vazio", dict(DOC, categorias=[""]), "vazio"),
    ("espaço inicial", dict(DOC, categorias=[" Transporte"]), "espaços"),
    ("espaço final", dict(DOC, categorias=["Transporte "]), "espaços"),
    ("nome extenso", dict(DOC, categorias=["a" * 31]), "limite"),
    ("controle interno", dict(DOC, categorias=["Trans\nporte"]), "controle"),
    ("categoria repetida", dict(DOC, categorias=["Transporte"] * 2), "repetida"),
]:
    caso("Catálogo rejeita " + nome, lambda d=documento, m=mensagem: rejeita(lambda: validar_catalogo(d), m))
caso("Catálogo aceita vinte nomes", lambda: igual(len(validar_catalogo(dict(DOC, categorias=[str(i) for i in range(20)]))), 20))
caso("Catálogo aceita nome no limite", lambda: igual(validar_catalogo(dict(DOC, categorias=["a" * 30])), ["a" * 30]))
for valor in [12.5, True, None, "12,50", "12.5", "1e2", "NaN", "Infinity", "-1.00", "0.00", "10000000.00", " 12.50"]:
    caso("Dinheiro rejeita " + repr(valor), lambda v=valor: rejeita(lambda: converter_valor(v), "valor:"))
caso("Dinheiro preserva centavos", lambda: igual(converter_valor("12.50") + converter_valor("35.00") + converter_valor("80.00"), Decimal("127.50")))
for valor in ["2026-02-30", "2026-9-10", "2026-09-10T00:00:00", None]:
    caso("Data rejeita " + repr(valor), lambda v=valor: rejeita(lambda: converter_data(v), "data:"))
caso("Lote CSV válido e imutável", lambda: verifica_lote("validas.csv", 3, 0, "127.50"))
caso("Lote JSON equivalente", lambda: verifica_lote("validas.json", 3, 0, "127.50"))
caso("Repetição idêntica não aumenta total", lambda: verifica_lote("repetidas.json", 3, 1, "127.50"))
caso("Data e valor inválidos bloqueiam integralmente", lambda: verifica_lote("invalidas.csv", 0, 0, erros=["Registro 2: data: dia, mês ou ano impossível", "Registro 3: valor: use 1 a 7 dígitos, ponto e 2 casas decimais"]))
caso("Valor JSON numérico bloqueia lote", lambda: verifica_lote("valor_numerico.json", 0, 0, erros=["Registro 1: valor: informe texto, por exemplo 12.50"]))
caso("Conflito D002 bloqueia D004", lambda: verifica_lote("desafio.json", 0, 0, erros=["Registro 4: id: conteúdo conflitante para D002"]))
caso("CSV com vírgula entre aspas", lambda: verifica_lote("descricao_com_virgula.csv", 3, 0, "127.50"))
caso("Lote vazio", lambda: igual(validar_lote([], CATS), {"despesas": [], "erros": [], "repetidos": 0}))
caso("Limite de registros", lambda: rejeita(lambda: validar_lote([{}] * 1001, CATS), "1000"))
for url in ["https://127.0.0.1:8765/categorias", "http://example.com:8765/categorias", "http://user:senha@127.0.0.1:8765/categorias", "http://127.0.0.1/categorias", "http://127.0.0.1:0/categorias", "http://127.0.0.1:8765/categorias?x=1", "http://127.0.0.1:8765/categorias#x"]:
    caso("URL local: rejeição " + url, lambda u=url: rejeita(lambda: validar_url_local(u), "API:"))

servidor = criar_servidor(0)
BASE = "http://127.0.0.1:" + str(servidor.server_address[1])
thread = threading.Thread(target=servidor.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
thread.start()
try:
    caso("HTTP real: endereço de loopback", lambda: igual(servidor.server_address[0], "127.0.0.1"))
    caso("HTTP real: catálogo 200", lambda: igual(obter_catalogo(BASE + "/categorias"), CATS))
    for rota, trecho in [
        ("/ausente", "HTTP 404"), ("/cenarios/indisponivel", "HTTP 503"),
        ("/cenarios/json-invalido", "JSON inválido"),
        ("/cenarios/contrato-invalido", "1 a 20"),
        ("/cenarios/tipo-incorreto", "Content-Type"), ("/cenarios/sem-tipo", "Content-Type"),
        ("/cenarios/sem-conteudo", "recebido 204"), ("/cenarios/redirecionamento", "recebido 302"),
        ("/cenarios/chave-repetida", "chave repetida"), ("/cenarios/nao-finito", "constante"),
        ("/cenarios/utf8-invalido", "UTF-8"), ("/cenarios/grande", "32 KiB"),
    ]:
        caso("HTTP real: rejeita " + rota, lambda r=rota, t=trecho: rejeita(lambda: obter_catalogo(BASE + r), t))
    caso("HTTP real: corpo no limite", lambda: igual(obter_catalogo(BASE + "/cenarios/limite"), CATS))
    caso("HTTP real: timeout antes dos cabeçalhos", lambda: rejeita(lambda: obter_catalogo(BASE + "/cenarios/lenta", timeout=(0.5, 0.1)), "tempo limite"))
    caso("HTTP real: falha durante o corpo", lambda: rejeita(lambda: obter_catalogo(BASE + "/cenarios/lenta-corpo", timeout=(0.5, 0.1)), "comunicação HTTP"))

    def uma_consulta():
        anterior = servidor.contagens.get("/categorias", 0)
        codigo, saida = app(PASTA / "dados/validas.csv", BASE + "/categorias")
        igual(codigo, 0)
        exigir("127.50" in saida, "Total incorreto")
        igual(servidor.contagens["/categorias"] - anterior, 1)
    caso("Aplicação consulta catálogo uma vez por lote", uma_consulta)

    def sem_fallback():
        anterior = servidor.contagens.get("/cenarios/indisponivel", 0)
        codigo, saida = app(PASTA / "dados/validas.csv", BASE + "/cenarios/indisponivel")
        igual(codigo, 1)
        exigir("HTTP 503" in saida and "Total" not in saida, "Falha ocultada ou total parcial")
        igual(servidor.contagens["/cenarios/indisponivel"] - anterior, 1)
    caso("Aplicação não substitui catálogo nem repete chamada", sem_fallback)

    def novo_nome():
        categorias = obter_catalogo(BASE + "/cenarios/extra")
        entradas = ler_json(PASTA / "dados/validas.json")
        entradas[0]["categoria"] = "Livros"
        igual(validar_lote(entradas, categorias)["erros"], [])
        exigir(bool(validar_lote(entradas, CATS)["erros"]), "Catálogo do teste não foi aplicado")
    caso("Aplicação usa novos nomes fornecidos pela API", novo_nome)

    def bloqueios_rede():
        for rota in ["/cenarios/json-invalido", "/cenarios/contrato-invalido", "/cenarios/tipo-incorreto"]:
            codigo, saida = app(PASTA / "dados/validas.csv", BASE + rota)
            igual(codigo, 1)
            exigir("Total" not in saida, "Total indevido após falha " + rota)
    caso("Aplicação não totaliza respostas rejeitadas", bloqueios_rede)

    with socket.socket() as reservada:
        reservada.bind(("127.0.0.1", 0))  # Porta reservada sem servidor escutando.
        ausente = "http://127.0.0.1:" + str(reservada.getsockname()[1]) + "/categorias"
        caso("HTTP real: servidor ausente", lambda: rejeita(lambda: obter_catalogo(ausente, timeout=(0.3, 0.3)), "comunicação HTTP"))
        def indisponivel_sem_total():
            codigo, saida = app(PASTA / "dados/validas.csv", ausente)
            igual(codigo, 1)
            exigir("Total" not in saida, "Total indevido sem servidor")
        caso("Aplicação bloqueia servidor ausente", indisponivel_sem_total)

    resumo = ["Lote validado em memória", "Despesas únicas: 3", "Repetições idênticas: 0", "Total em reais: 127.50", "Nenhuma despesa foi gravada"]
    execucoes = [
        ("01_observar_resposta.py", [], 0, ["Status: 200", "Tipo: application/json; charset=utf-8", "Versão: 1", "Categorias: Alimentação, Transporte, Materiais"]),
        ("02_validar_contrato.py", [], 0, ["Aceitas: " + str(CATS)]),
        ("03_consultar_catalogo.py", [], 0, ["Catálogo aceito: Alimentação, Transporte, Materiais"]),
        ("04_resumo_csv.py", [], 0, resumo), ("05_resumo_json.py", [], 0, resumo),
        ("solucao_exercicio.py", [], 1, ["Lote bloqueado", "Registro 2: categoria: não consta no catálogo recebido", "Nenhuma despesa foi gravada"]),
        ("solucao_desafio.py", [], 1, ["Lote bloqueado", "Registro 4: id: conteúdo conflitante para D002", "Nenhuma despesa foi gravada"]),
    ]
    for argumento, mensagem in [
        ("404", "API: resposta HTTP 404"), ("503", "API: resposta HTTP 503"),
        ("json", "API: JSON inválido"), ("contrato", "catálogo: informe de 1 a 20 categorias"),
        ("tipo", "API: Content-Type deve ser application/json"),
        ("lenta", "API: tempo limite de conexão ou leitura excedido"),
        ("redirect", "API: esperado HTTP 200; recebido 302"),
    ]:
        execucoes.append(("06_observar_falhas.py", [argumento], 1, ["Consulta interrompida: " + mensagem]))
    for arquivo, argumentos, codigo, linhas in execucoes:
        caso("Programa: " + arquivo + " " + " ".join(argumentos), lambda a=arquivo, ar=argumentos, c=codigo, l=linhas: programa(a, ar, c, l))
finally:
    servidor.shutdown()
    servidor.server_close()
    thread.join(timeout=2)

arquivos = sorted([p for p in PASTA.rglob("*.py") if "__pycache__" not in p.parts] + list((PASTA / "dados").glob("*")) + [PASTA / "requirements.txt"])
hashes = {str(p.relative_to(PASTA)).replace(os.sep, "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in arquivos}
manifesto = PASTA / "MANIFESTO_SHA256.json"
if manifesto.exists():
    caso("Integridade: scripts, dados e dependências", lambda: igual(hashes, json.loads(manifesto.read_text(encoding="utf-8"))))
erros = [c for c in CASOS if c["status"] != "aprovado"]
relatorio = {
    "capitulo": 5, "revisao": "R01", "status": "reprovado" if erros else "aprovado",
    "data_utc": datetime.now(timezone.utc).isoformat(),
    "sistema": platform.system(), "plataforma": platform.platform(),
    "python": platform.python_version(), "executavel": sys.executable,
    "ambiente_virtual": sys.prefix != sys.base_prefix,
    "dependencias": {n: importlib.metadata.version(n) for n in ["requests", "certifi", "charset-normalizer", "idna", "urllib3"]},
    "integracao": "HTTP real em 127.0.0.1, porta temporária; servidor com respostas sintéticas",
    "total": len(CASOS), "aprovados": len(CASOS) - len(erros), "falhas": len(erros),
    "casos": CASOS, "programas": PROGRAMAS, "sha256_arquivos": hashes,
}
pasta_resultados = PASTA / "resultados"
pasta_resultados.mkdir(exist_ok=True)
saida = pasta_resultados / ("relatorio-cap05-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
with saida.open("x", encoding="utf-8") as arquivo:
    json.dump(relatorio, arquivo, ensure_ascii=False, indent=2)
print("Status:", relatorio["status"])
print("Verificações:", str(relatorio["aprovados"]) + "/" + str(relatorio["total"]))
print("Sistema:", relatorio["sistema"], "| Python:", relatorio["python"])
print("Relatório:", saida)
for erro in erros:
    print("FALHA:", erro["nome"], erro["erro"])
raise SystemExit(1 if erros else 0)
