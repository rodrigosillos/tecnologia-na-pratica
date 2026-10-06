"""Contrato do comprovante técnico de importação; não aprova despesas."""
from decimal import Decimal
from re import fullmatch
from regras import validar_lote


def validar_id(execucao):
    if not isinstance(execucao, str) or fullmatch(r"[a-z0-9][a-z0-9_-]{0,39}", execucao) is None:
        raise ValueError("Execução: use 1 a 40 letras minúsculas, números, _ ou -")
    return execucao


def validar_hash(valor):
    if not isinstance(valor, str) or fullmatch(r"[a-f0-9]{64}", valor) is None:
        raise ValueError("Hash da entrada inválido")


def criar_retrato(linhas):
    despesas = [{"id": i, "data": d.isoformat(), "descricao": t,
                 "categoria": c, "valor": format(v, ".2f")}
                for i, d, t, c, v in linhas]
    return {"despesas": despesas, "quantidade": len(despesas),
            "total": format(sum((v for i, d, t, c, v in linhas), Decimal("0.00")), ".2f")}


def conferir_recibo(recibo):
    if not isinstance(recibo, dict) or set(recibo) != {"execucao", "entrada_sha256", "novas", "existentes", "retrato"}:
        raise ValueError("Recibo incompatível")
    validar_id(recibo["execucao"])
    validar_hash(recibo["entrada_sha256"])
    for campo in ("novas", "existentes"):
        if type(recibo[campo]) is not int or recibo[campo] < 0:
            raise ValueError("Contagem inválida no recibo")
    retrato = recibo["retrato"]
    if not isinstance(retrato, dict) or set(retrato) != {"despesas", "quantidade", "total"}:
        raise ValueError("Retrato incompatível")
    registros = retrato["despesas"]
    if not isinstance(registros, list) or not registros:
        raise ValueError("Retrato vazio ou inválido")
    categorias = []
    for r in registros:
        if not isinstance(r, dict) or not isinstance(r.get("categoria"), str):
            raise ValueError("Despesa inválida no retrato")
        if r["categoria"] not in categorias:
            categorias.append(r["categoria"])
    resultado = validar_lote(registros, categorias)
    if resultado["erros"] or resultado["repetidos"]:
        raise ValueError("Registros inválidos ou repetidos no retrato")
    ids = [d["id"] for d in resultado["despesas"]]
    total = sum((d["valor"] for d in resultado["despesas"]), Decimal("0.00"))
    if (ids != sorted(ids) or type(retrato["quantidade"]) is not int
            or retrato["quantidade"] != len(ids) or retrato["total"] != format(total, ".2f")
            or recibo["novas"] + recibo["existentes"] > len(ids)):
        raise ValueError("Contagem, ordem ou total divergente no recibo")
    return recibo
