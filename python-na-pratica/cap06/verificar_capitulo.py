"""Testes locais e de integração; não usa nem apaga o esquema tnp_cap06.
O esquema temporário é criado por esta execução e removido ao terminar.
--sem-banco executa somente a parte local e NÃO aprova a integração.
"""
import argparse
import contextlib
import copy
import csv
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import threading
from uuid import uuid4

sys.dont_write_bytecode = True
PASTA = Path(__file__).resolve().parent
if str(PASTA) not in sys.path:
    sys.path.insert(0, str(PASTA))
import psycopg
from psycopg import sql
from aplicacao import executar_importacao, executar_fluxo, executar_exportacao
from arquivos import ler_csv, ler_json
from banco import importar, consultar, preparar, identificador_esquema
from conexao import configuracao_banco, conectar
from regras import converter_valor, validar_lote
from relatorios import gerar_arquivos, montar_html, texto_csv, exportar
from servidor_catalogo import criar_servidor

CASOS = []
EXECUCOES = []
CATS = ["Alimentação", "Transporte", "Materiais"]
DADOS = PASTA / "dados"


def igual(a, b):
    if a != b:
        raise AssertionError("Recebido: " + repr(a) + "; esperado: " + repr(b))


def exigir(condicao, mensagem):
    if not condicao:
        raise AssertionError(mensagem)


def rejeita(funcao, tipo=ValueError, trecho=""):
    try:
        funcao()
    except tipo as erro:
        exigir(trecho in str(erro), "Diagnóstico diferente do esperado")
        return type(erro).__name__
    raise AssertionError("Operação deveria ter sido rejeitada")


def caso(nome, funcao):
    try:
        evidencia = funcao()
        CASOS.append({"nome": nome, "status": "aprovado", "evidencia": evidencia})
    except Exception as erro:
        CASOS.append({"nome": nome, "status": "reprovado", "erro": str(erro), "tipo": type(erro).__name__})


def pendente(nome):
    CASOS.append({"nome": nome, "status": "pendente_motor_nativo", "motivo": "Requer integração PostgreSQL nativa; não homologada pelo socket WASM"})


def capturar(nome, funcao, esperado, trechos):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        codigo = funcao()
    saida = buf.getvalue()
    EXECUCOES.append({"etapa": nome, "saida": codigo, "stdout": saida})
    igual(codigo, esperado)
    for trecho in trechos:
        exigir(trecho in saida, "Trecho ausente: " + trecho)
    return {"saida": codigo, "stdout": saida}


def retrato_local():
    dados = validar_lote(ler_json(DADOS / "validas.json"), CATS)["despesas"]
    return {"despesas": [(d["id"], d["data"], d["descricao"], d["categoria"], d["valor"]) for d in dados],
            "categorias": [("Alimentação", 1, Decimal("12.50")), ("Materiais", 1, Decimal("80.00")), ("Transporte", 1, Decimal("35.00"))],
            "quantidade": 3, "total": Decimal("127.50")}


def dependencias():
    for linha in (PASTA / "requirements.txt").read_text(encoding="utf-8").splitlines():
        nome, versao = linha.split("==")
        igual(importlib.metadata.version(nome), versao)


def testes_locais():
    caso("Python 3.14", lambda: igual(sys.version_info[:2], (3, 14)))
    caso("Ambiente virtual", lambda: exigir(sys.prefix != sys.base_prefix, "Use a .venv"))
    caso("Dependências fixadas", dependencias)
    caso("Dinheiro mantém Decimal", lambda: igual(converter_valor("127.50"), Decimal("127.50")))
    for valor in ["1.005", "NaN", "-1.00", "0.00", 12.5, "10000000.00"]:
        caso("Dinheiro rejeita " + repr(valor), lambda v=valor: rejeita(lambda: converter_valor(v)))
    for esquema in ["public", "tnp_cap06; DROP SCHEMA public", "tnp_c06_t_qualquer"]:
        caso("Esquema não autorizado " + esquema, lambda e=esquema: rejeita(lambda: identificador_esquema(e)))
    for texto in ["=2+2", "+2", "-2", "@SUM(A1)", " \t=2+2"]:
        caso("CSV neutraliza início de fórmula " + repr(texto), lambda t=texto: igual(texto_csv(t), "'" + t))
    caso("CSV preserva texto comum", lambda: igual(texto_csv("Café, reunião"), "Café, reunião"))
    html = montar_html(retrato_local())
    caso("HTML identifica língua e UTF-8", lambda: exigir('lang="pt-BR"' in html and 'charset="utf-8"' in html, "Metadados HTML ausentes"))
    caso("HTML contém total e categorias", lambda: exigir("127.50" in html and "Alimentação" in html, "Conteúdo HTML divergente"))
    ataque = retrato_local()
    ataque["despesas"][0] = ("D001", date(2026, 9, 10), '<script>alert("teste")</script>', "Alimentação", Decimal("12.50"))
    caso("HTML escapa conteúdo como texto", lambda: exigir("<script>" not in montar_html(ataque) and "&lt;script&gt;" in montar_html(ataque), "HTML interpretável na descrição"))
    with tempfile.TemporaryDirectory() as temp:
        destino = Path(temp) / "gerados"
        original = retrato_local()
        copia = copy.deepcopy(original)
        p = gerar_arquivos(original, destino)
        caso("Exportação não modifica retrato", lambda: igual(original, copia))
        caso("Exportação cria três arquivos", lambda: igual(sorted(x.name for x in p.iterdir()), ["despesas.csv", "despesas.html", "estado.json"]))
        caso("CSV codificação com BOM", lambda: exigir((p / "despesas.csv").read_bytes().startswith(b'\xef\xbb\xbf'), "BOM UTF-8 ausente"))
        with (p / "despesas.csv").open(encoding="utf-8-sig", newline="") as arq:
            linhas = list(csv.DictReader(arq))
        caso("CSV exporta três linhas", lambda: igual(len(linhas), 3))
        caso("CSV mantém centavos em texto", lambda: igual([l["valor"] for l in linhas], ["12.50", "35.00", "80.00"]))
        caso("CSV mantém acentos", lambda: igual(linhas[0]["categoria"], "Alimentação"))
        estado = json.loads((p / "estado.json").read_text(encoding="utf-8"))
        caso("Estado completo corresponde aos arquivos", lambda: igual((estado["estado"], estado["quantidade"], estado["total"]), ("concluida", 3, "127.50")))
        antigo = (p / "despesas.csv").read_bytes()
        novo = gerar_arquivos(original, destino)
        caso("Nova exportação preserva a anterior", lambda: exigir(novo != p and (p / "despesas.csv").read_bytes() == antigo, "Arquivo anterior alterado"))
        caso("Nenhuma pasta parcial após sucesso", lambda: igual(list(destino.glob("em-preparo-*")), []))
        bloqueio = Path(temp) / "arquivo"
        bloqueio.write_text("não apagar", encoding="utf-8")
        caso("Falha de destino é observável", lambda: rejeita(lambda: gerar_arquivos(original, bloqueio), OSError))
        caso("Falha preserva arquivo do destino", lambda: igual(bloqueio.read_text(encoding="utf-8"), "não apagar"))
        vazio = {"despesas": [], "categorias": [], "quantidade": 0, "total": Decimal("0.00")}
        pv = gerar_arquivos(vazio, destino)
        caso("Relatório vazio totaliza zero", lambda: igual(json.loads((pv / "estado.json").read_text(encoding="utf-8"))["total"], "0.00"))


def testes_banco(config, servidor_info):
    esquema = "tnp_c06_t_" + uuid4().hex[:16]
    nome = identificador_esquema(esquema)
    criado = False
    servidor = criar_servidor(0)
    base = "http://127.0.0.1:" + str(servidor.server_address[1])
    thread = threading.Thread(target=servidor.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()
    try:
        with conectar(config) as con:
            servidor_info["versao_completa"] = con.execute("SELECT version()").fetchone()[0]
            servidor_info["server_version"] = con.info.server_version
            servidor_info["banco"], servidor_info["usuario"] = con.execute("SELECT current_database(), current_user").fetchone()
            embarcado = any(x in servidor_info["versao_completa"].lower() for x in ["pglite", "wasm", "emscripten"])
            servidor_info["motor"] = "PGlite/WASM — complementar" if embarcado else "PostgreSQL nativo"
            caso("Conexão aponta ao banco e usuário dedicados", lambda: igual((servidor_info["banco"], servidor_info["usuario"]), ("python_na_pratica", "python_leitor")))
            papeis = con.execute("SELECT rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname = current_user").fetchone()
            caso("Papel sem superusuário, CREATEDB ou CREATEROLE", lambda: igual(papeis, (False, False, False)))
            con.execute(sql.SQL("CREATE SCHEMA {}").format(nome))
        criado = True
        preparar(config, esquema)
        caso("Banco inicial vazio", lambda: igual(consultar(config, esquema)["quantidade"], 0))
        if not embarcado:
            ruim = dict(config, password=uuid4().hex)
            def senha_rejeitada():
                con = None
                try:
                    con = conectar(ruim)
                except psycopg.OperationalError:
                    return "credencial incorreta rejeitada"
                finally:
                    if con is not None:
                        con.close()
                raise AssertionError("Servidor aceitou senha incorreta; confira autenticação local")
            caso("Autenticação rejeita senha incorreta", senha_rejeitada)
        else:
            servidor_info["autenticacao"] = "não homologada: socket PGlite não reproduz autenticação nativa"
            pendente("Autenticação rejeita senha incorreta")

        caso("Importar CSV confirma três despesas", lambda: capturar("02_importar_csv", lambda: executar_importacao(config, DADOS / "validas.csv", base + "/categorias", esquema), 0, ["Importação confirmada", "Novas despesas: 3"]))
        retrato = consultar(config, esquema)
        caso("Total confirmado inicial", lambda: igual((retrato["quantidade"], retrato["total"]), (3, Decimal("127.50"))))
        caso("Tipos recuperados date e Decimal", lambda: exigir(all(type(d[1]) is date and type(d[4]) is Decimal for d in retrato["despesas"]), "Tipo convertido incorretamente"))
        caso("Grupos conferem total e contagem", lambda: igual(retrato["categorias"], retrato_local()["categorias"]))
        caso("Reimportar JSON não duplica", lambda: capturar("03_reimportar_json", lambda: executar_importacao(config, DADOS / "validas.json", base + "/categorias", esquema), 0, ["Novas despesas: 0", "Já existentes e idênticas: 3"]))
        caso("Repetição no arquivo não duplica", lambda: igual(importar(config, ler_json(DADOS / "repetidas.json"), CATS, esquema), {"novas": 0, "existentes": 3, "repetidas_entrada": 1}))
        preparar(config, esquema)
        caso("Preparar novamente preserva dados", lambda: igual(consultar(config, esquema)["quantidade"], 3))
        def entrada_bloqueada():
            rejeita(lambda: importar(config, ler_csv(DADOS / "invalidas.csv"), CATS, esquema))
            igual(consultar(config, esquema)["despesas"], retrato["despesas"])
        caso("Entrada inválida preserva banco", entrada_bloqueada)
        def conflito():
            codigo = capturar("07_conflito_banco", lambda: executar_importacao(config, DADOS / "conflito_banco.json", base + "/categorias", esquema), 1, ["conflito com despesa já gravada: D002"])
            igual(consultar(config, esquema)["despesas"], retrato["despesas"])
            return codigo
        caso("Rollback retira D005 inserida antes do conflito D002", conflito)
        importar(config, [], CATS, esquema)
        caso("Lote vazio não muda banco", lambda: igual(consultar(config, esquema)["quantidade"], 3))
        def api_falha():
            codigo = capturar("API indisponível", lambda: executar_importacao(config, DADOS / "quarta_despesa.json", base + "/cenarios/indisponivel", esquema), 1, ["HTTP 503"])
            igual(consultar(config, esquema)["quantidade"], 3)
            return codigo
        caso("Falha HTTP não grava D004", api_falha)
        with tempfile.TemporaryDirectory() as temp:
            pasta = Path(temp)
            saida = exportar(config, pasta / "validos", esquema)
            caso("Exportação lê estado confirmado", lambda: igual(json.loads((saida / "estado.json").read_text(encoding="utf-8"))["total"], "127.50"))
            bloqueio = pasta / "arquivo"
            bloqueio.write_text("bloqueio didático", encoding="utf-8")
            caso("Falha após commit retorna exportação pendente", lambda: capturar("06_falha_exportacao", lambda: executar_fluxo(config, DADOS / "quarta_despesa.json", base + "/categorias", bloqueio, esquema), 2, ["Importação confirmada", "Novas despesas: 1", "Exportação pendente", "permanece confirmada"]))
            caso("Commit sobrevive à falha do arquivo", lambda: igual((consultar(config, esquema)["quantidade"], consultar(config, esquema)["total"]), (4, Decimal("147.50"))))
            caso("Recuperação somente de exportação", lambda: capturar("05_exportar recuperação", lambda: executar_exportacao(config, pasta / "recuperados", esquema), 0, ["Exportação concluída"]))
            caso("Recuperação não duplica nem remove", lambda: igual((consultar(config, esquema)["quantidade"], consultar(config, esquema)["total"]), (4, Decimal("147.50"))))
            p = next((pasta / "recuperados").glob("exportacao-*"))
            caso("Relatório recuperado usa total confirmado", lambda: igual(json.loads((p / "estado.json").read_text(encoding="utf-8"))["total"], "147.50"))
        caso("Desafio corrigido insere D005 e preserva D002", lambda: capturar("solucao_desafio", lambda: executar_importacao(config, DADOS / "solucao_desafio.json", base + "/categorias", esquema), 0, ["Novas despesas: 1", "Já existentes e idênticas: 1"]))
        caso("Total final guiado", lambda: igual((consultar(config, esquema)["quantidade"], consultar(config, esquema)["total"]), (5, Decimal("157.50"))))
        def restricao(valor, tipo):
            def gravar():
                with conectar(config) as con:
                    con.execute(sql.SQL("INSERT INTO {}.despesas VALUES (%s, %s, %s, %s, %s)").format(nome), ("D099", date(2026, 9, 10), "Teste", "Materiais", valor))
            return rejeita(gravar, tipo)
        for valor, tipo in [(Decimal("0.00"), psycopg.errors.CheckViolation), (Decimal("-1.00"), psycopg.errors.CheckViolation), (Decimal("NaN"), psycopg.errors.CheckViolation), (Decimal("10000000.00"), psycopg.errors.NumericValueOutOfRange)]:
            if embarcado:
                pendente("Restrição SQL rejeita valor " + str(valor))
            else:
                caso("Restrição SQL rejeita valor " + str(valor), lambda v=valor, t=tipo: restricao(v, t))
        def chave_repetida():
            with conectar(config) as con:
                con.execute(sql.SQL("INSERT INTO {}.despesas VALUES (%s,%s,%s,%s,%s)").format(nome), ("D001",date(2026,9,10),"Teste","Materiais",Decimal("1.00")))
        if embarcado:
            pendente("Chave primária rejeita duplicidade direta")
            pendente("Restrições rejeitadas não mudam total")
        else:
            caso("Chave primária rejeita duplicidade direta", lambda: rejeita(chave_repetida, psycopg.errors.UniqueViolation))
            caso("Restrições rejeitadas não mudam total", lambda: igual(consultar(config, esquema)["total"], Decimal("157.50")))
        def numero_arredondado():
            try:
                with conectar(config) as con:
                    con.execute(sql.SQL("INSERT INTO {}.despesas VALUES (%s,%s,%s,%s,%s)").format(nome), ("D099",date(2026,9,10),"Teste","Materiais",Decimal("1.005")))
                    valor = con.execute(sql.SQL("SELECT valor FROM {}.despesas WHERE id = %s").format(nome),("D099",)).fetchone()[0]
                    igual(valor,Decimal("1.01"))
                    raise ValueError("rollback didático")
            except ValueError as erro:
                igual(str(erro), "rollback didático")
            igual(consultar(config, esquema)["quantidade"], 5)
            return "NUMERIC arredonda; validação de escala ocorre antes, em Python"
        caso("Escala SQL não substitui contrato de entrada", numero_arredondado)
        def texto_comando():
            registros = [{"id":"D090", "data":"2026-09-11", "descricao":"=2+2 <script>alert('x')</script>; DROP TABLE despesas; --", "categoria":"Materiais", "valor":"1.00"}]
            importar(config, registros, CATS, esquema)
            r = consultar(config, esquema)
            igual(next(d[2] for d in r["despesas"] if d[0]=="D090"),registros[0]["descricao"])
            with tempfile.TemporaryDirectory() as temp:
                p = exportar(config, Path(temp), esquema)
                with (p / "despesas.csv").open(encoding="utf-8-sig",newline="") as arq:
                    linha = next(d for d in csv.DictReader(arq) if d["id"]=="D090")
                exigir(linha["descricao"].startswith("'=2"), "Texto exportado pode iniciar fórmula")
                html = (p / "despesas.html").read_text(encoding="utf-8")
                exigir("<script>" not in html and "&lt;script&gt;" in html,"HTML não escapado")
            return "Texto preservado no banco e representado com proteção nos relatórios"
        caso("Parâmetros SQL e representação segura de texto externo", texto_comando)
    finally:
        servidor.shutdown(); servidor.server_close();thread.join(timeout=2)
        if criado:
            with conectar(config) as con:
                con.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(nome))
            servidor_info["esquema_temporario_removido"] = esquema


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-banco", action="store_true")
    args = parser.parse_args()
    testes_locais()
    servidor_info = {}
    if not args.sem_banco:
        try:
            config = configuracao_banco()
            testes_banco(config, servidor_info)
        except (Exception, KeyboardInterrupt) as erro:
            # Não inclui string de conexão nem senha no relatório.
            CASOS.append({"nome":"Execução da integração", "status":"reprovado", "tipo":type(erro).__name__, "erro":"Integração interrompida; confira preparação, conexão e casos registrados"})
    arquivos = sorted([p for p in PASTA.rglob("*") if p.is_file() and (p.suffix in {".py", ".sql", ".psql"} or p.parent.name == "dados" or p.name == "requirements.txt") and '__pycache__' not in p.parts])
    hashes = {p.relative_to(PASTA).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in arquivos}
    manifesto = PASTA / "MANIFESTO_SHA256.json"
    caso("Integridade de scripts, SQL, dados e requisitos",lambda:igual(hashes,json.loads(manifesto.read_text(encoding="utf-8"))))
    falhas = [c for c in CASOS if c["status"] == "reprovado"]
    pendentes = [c for c in CASOS if c["status"].startswith("pendente")]
    complementar = "PGlite" in servidor_info.get("motor", "")
    status = "reprovado" if falhas else ("pendente_integracao" if args.sem_banco else "pendente_postgresql_nativo" if complementar else "aprovado")
    relatorio = {"capitulo":6,"revisao":"R01","status":status,"data_utc":datetime.now(timezone.utc).isoformat(),
        "sistema":platform.system(),"plataforma":platform.platform(),"python":platform.python_version(),
        "executavel":sys.executable,"modo":"local_sem_banco" if args.sem_banco else "complementar_wasm" if complementar else "integracao_nativa",
        "total":len(CASOS),"aprovados":sum(c["status"] == "aprovado" for c in CASOS),"falhas":len(falhas),"pendentes":len(pendentes),
        "dependencias":{n:importlib.metadata.version(n) for n in ['requests','psycopg','psycopg-binary']},
        "postgresql":servidor_info,"casos":CASOS,"execucoes":EXECUCOES,"sha256_arquivos":hashes}
    pasta = PASTA / "resultados";pasta.mkdir(exist_ok=True)
    caminho = pasta / ("relatorio-cap06-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")+".json")
    with caminho.open("x",encoding="utf-8") as arq:json.dump(relatorio,arq,ensure_ascii=False,indent=2)
    print("Status:",status)
    print("Verificações:",str(relatorio['aprovados'])+'/'+str(relatorio['total']))
    print("Pendentes:",len(pendentes))
    print("Sistema:",platform.system(),"| Python:",platform.python_version())
    print("Relatório:",caminho)
    for falha in falhas:print("FALHA:",falha['nome'],falha.get('erro',''))
    return 1 if falhas else 2 if status != 'aprovado' else 0


if __name__ == '__main__':
    raise SystemExit(main())
