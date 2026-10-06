"""Arquivos derivados de um retrato confirmado do banco, sem alterar entradas."""
import csv
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import shutil
import tempfile
from uuid import uuid4

from banco import consultar, ESQUEMA


def texto_csv(texto):
    # Relatório para leitura: evita início de fórmula nos textos exportados.
    if texto.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + texto
    return texto


def montar_html(retrato):
    linhas = []
    for ident, data, descricao, categoria, valor in retrato["despesas"]:
        celulas = [ident, data.isoformat(), descricao, categoria, format(valor, ".2f")]
        linhas.append("<tr>" + "".join("<td>" + escape(c) + "</td>" for c in celulas) + "</tr>")
    grupos = "".join("<tr><td>" + escape(c) + "</td><td>" + str(n) + "</td><td>" + format(v, ".2f") + "</td></tr>" for c, n, v in retrato["categorias"])
    return """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Despesas confirmadas — Python na Prática</title>
<style>
body{margin:0;background:#eef2f6;color:#172e48;font:16px/1.55 Arial,sans-serif}
main{max-width:1050px;margin:32px auto;background:white;padding:32px;border-top:6px solid #ed7d31}
h1{font-size:30px;line-height:1.2;margin:8px 0 16px}.marca{font-weight:bold;letter-spacing:2px;font-size:12px}
.resumo{background:#edf6fa;padding:16px;margin:24px 0}.tabela{overflow:auto}
table{border-collapse:collapse;width:100%;font-size:14px;margin-bottom:24px}th,td{text-align:left;border-bottom:1px solid #ced9e3;padding:10px;vertical-align:top}th{background:#172e48;color:white}
td:nth-child(3){overflow-wrap:anywhere}footer{font-size:12px;border-top:1px solid #ced9e3;padding-top:16px}
@media(max-width:600px){main{margin:0;padding:18px}h1{font-size:25px}}
@media print{body{background:white}main{margin:0;padding:16px}tr{break-inside:avoid}}
</style><main><div class="marca">TECNOLOGIA NA PRÁTICA</div>
<h1>Despesas confirmadas</h1><p>Retrato de todos os registros consultados no banco do laboratório.</p>
<div class="resumo">Quantidade: <strong>""" + str(retrato["quantidade"]) + "</strong> · Total em reais: <strong>" + format(retrato["total"], ".2f") + """</strong></div>
<h2>Detalhamento</h2><div class="tabela"><table><thead><tr><th>ID</th><th>Data</th><th>Descrição</th><th>Categoria</th><th>Valor</th></tr></thead><tbody>""" + "".join(linhas) + """</tbody></table></div>
<h2>Por categoria</h2><table><thead><tr><th>Categoria</th><th>Quantidade</th><th>Total em reais</th></tr></thead><tbody>""" + grupos + """</tbody></table>
<footer>Python na Prática · Rodrigo Sillos<br>Dados fictícios. Valores obtidos do banco; nenhuma classificação ou soma feita por IA.</footer></main></html>"""


def gerar_arquivos(retrato, destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    temporaria = Path(tempfile.mkdtemp(prefix="em-preparo-", dir=destino))
    nome = "exportacao-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:8]
    final = destino / nome
    try:
        with (temporaria / "despesas.csv").open("w", encoding="utf-8-sig", newline="") as arq:
            escritor = csv.writer(arq)
            escritor.writerow(["id", "data", "descricao", "categoria", "valor"])
            for ident, data, descricao, categoria, valor in retrato["despesas"]:
                escritor.writerow([texto_csv(ident), data.isoformat(), texto_csv(descricao), texto_csv(categoria), format(valor, ".2f")])
        (temporaria / "despesas.html").write_text(montar_html(retrato), encoding="utf-8")
        (temporaria / "estado.json").write_text(json.dumps({
            "estado": "concluida", "quantidade": retrato["quantidade"],
            "total": format(retrato["total"], ".2f"), "origem": "consulta ao banco",
            "arquivos": ["despesas.csv", "despesas.html"],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporaria.rename(final)
    except Exception:
        shutil.rmtree(temporaria, ignore_errors=True)
        raise
    return final


def exportar(config, destino, esquema=ESQUEMA):
    return gerar_arquivos(consultar(config, esquema), destino)
