"""Relatório determinístico de um recibo; destino existente nunca é substituído."""
import csv
import hashlib
import io
from html import escape
from pathlib import Path
import shutil
import tempfile
from arquivos import json_bytes
from recibos import conferir_recibo


def texto_csv(texto):
    return "'" + texto if texto.lstrip().startswith(("=", "+", "-", "@")) else texto


def renderizar(recibo):
    conferir_recibo(recibo)
    r = recibo["retrato"]
    saida = io.StringIO(newline="")
    escritor = csv.writer(saida, lineterminator="\r\n")
    campos = ["id", "data", "descricao", "categoria", "valor"]
    escritor.writerow(campos)
    linhas = []
    for d in r["despesas"]:
        escritor.writerow([texto_csv(d[c]) for c in campos])
        linhas.append("<tr>" + "".join("<td>" + escape(d[c]) + "</td>" for c in campos) + "</tr>")
    html = """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Despesas confirmadas</title><style>
body{font:16px/1.55 Arial,sans-serif;color:#173047;background:#eef3f7;margin:0}
main{background:white;max-width:1000px;margin:24px auto;padding:28px;border-top:6px solid #ed7d31}
.tabela{overflow:auto}table{border-collapse:collapse;width:100%}th,td{padding:10px;text-align:left;border-bottom:1px solid #ccc}
th{background:#173047;color:white}h1{line-height:1.2}.resumo{padding:12px;background:#edf6fa}
@media(max-width:600px){main{margin:0;padding:16px}}
</style><main><p>TECNOLOGIA NA PRÁTICA</p><h1>Despesas confirmadas</h1>
"""
    html += "<p>Execução: <strong>" + recibo["execucao"] + "</strong></p>"
    html += "<p class='resumo'>Quantidade: " + str(r["quantidade"]) + " · Total em reais: " + r["total"] + "</p>"
    html += "<p>Retrato preservado na importação desta execução; pode diferir do banco atual.</p>"
    html += "<div class='tabela'><table><thead><tr>" + "".join("<th>" + c + "</th>" for c in ["ID", "Data", "Descrição", "Categoria", "Valor"]) + "</tr></thead><tbody>" + "".join(linhas) + "</tbody></table></div>"
    html += "<p>Dados fictícios · Rodrigo Sillos · Valores calculados por regras, sem IA.</p></main></html>\n"
    arquivos = {"despesas.csv": saida.getvalue().encode("utf-8-sig"), "despesas.html": html.encode("utf-8")}
    arquivos["recibo.json"] = json_bytes(recibo)
    arquivos["proveniencia.json"] = json_bytes(recibo["proveniencia"])
    arquivos["manifesto.json"] = json_bytes({"versao": 1, "execucao": recibo["execucao"],
        "sha256": {n: hashlib.sha256(b).hexdigest() for n, b in arquivos.items()}})
    return arquivos


def conferir_destino(recibo, raiz):
    arquivos = renderizar(recibo)
    final = Path(raiz) / recibo["execucao"]
    if not final.exists() and not final.is_symlink():
        return "pendente"
    if final.is_symlink() or not final.is_dir() or {p.name for p in final.iterdir()} != set(arquivos):
        raise ValueError("Destino existente incompatível; preserve-o e escolha outra raiz")
    for nome, esperado in arquivos.items():
        p = final / nome
        if p.is_symlink() or not p.is_file() or p.stat().st_size != len(esperado) or p.read_bytes() != esperado:
            raise ValueError("Arquivo existente divergente; preserve-o e escolha outra raiz")
    return "concluida"


def exportar(recibo, raiz):
    if conferir_destino(recibo, raiz) == "concluida":
        return "reutilizada"
    raiz = Path(raiz)
    raiz.mkdir(parents=True, exist_ok=True)
    temporaria = Path(tempfile.mkdtemp(prefix="em-preparo-", dir=raiz))
    try:
        for nome, conteudo in renderizar(recibo).items():
            (temporaria / nome).write_bytes(conteudo)
        final = raiz / recibo["execucao"]
        if final.exists() or final.is_symlink():
            raise ValueError("Destino apareceu durante a exportação")
        temporaria.rename(final)
    except Exception:
        shutil.rmtree(temporaria, ignore_errors=True)
        raise
    return "criada"
