"""Despesas e recibo na mesma transação; sem retry automático de escrita."""
from pathlib import Path
from re import fullmatch
from psycopg import sql
from psycopg.types.json import Jsonb
from conexao import conectar
from regras import validar_lote
from recibos import validar_id, validar_hash, criar_retrato, conferir_recibo

ESQUEMA = "tnp_cap11"


def nome_esquema(esquema):
    if esquema != ESQUEMA and fullmatch(r"tnp_c11_t_[a-f0-9]{16}", esquema) is None:
        raise ValueError("Esquema fora do capítulo 11")
    return sql.Identifier(esquema)


def preparar(config, esquema=ESQUEMA):
    nome = nome_esquema(esquema)
    fonte = (Path(__file__).parent / "sql/esquema.sql").read_text(encoding="utf-8")
    with conectar(config) as con:
        for comando in fonte.split(";\n"):
            if comando.strip():
                con.execute(sql.SQL(comando).format(esquema=nome))
        if con.execute(sql.SQL("SELECT versao FROM {}.metadados WHERE chave=1").format(nome)).fetchone() != (1,):
            raise ValueError("Versão de esquema incompatível")


def recibo_na_conexao(con, execucao, nome):
    linha = con.execute(sql.SQL(
        "SELECT entrada_sha256, novas, existentes, retrato FROM {}.execucoes WHERE id=%s"
    ).format(nome), (execucao,)).fetchone()
    if linha is None:
        return None
    return conferir_recibo(dict(zip(
        ["execucao", "entrada_sha256", "novas", "existentes", "retrato"], (execucao,) + linha)))


def consultar_recibo(config, execucao, esquema=ESQUEMA):
    validar_id(execucao)
    nome = nome_esquema(esquema)
    with conectar(config) as con:
        return recibo_na_conexao(con, execucao, nome)


def importar(config, execucao, entrada_hash, registros, categorias, esquema=ESQUEMA):
    validar_id(execucao)
    validar_hash(entrada_hash)
    resultado = validar_lote(registros, categorias)
    if resultado["erros"] or not resultado["despesas"]:
        raise ValueError("Lote inválido: " + "; ".join(resultado["erros"]))
    nome = nome_esquema(esquema)
    novas = existentes = 0
    with conectar(config) as con:
        anterior = recibo_na_conexao(con, execucao, nome)
        if anterior is not None:
            if anterior["entrada_sha256"] != entrada_hash:
                raise ValueError("Execução já vinculada a outra entrada")
            return anterior
        for d in resultado["despesas"]:
            campos = (d["data"], d["descricao"], d["categoria"], d["valor"])
            gravada = con.execute(sql.SQL(
                "SELECT data, descricao, categoria, valor FROM {}.despesas WHERE id=%s"
            ).format(nome), (d["id"],)).fetchone()
            if gravada is None:
                con.execute(sql.SQL(
                    "INSERT INTO {}.despesas VALUES (%s, %s, %s, %s, %s)"
                ).format(nome), (d["id"],) + campos)
                novas += 1
            elif gravada == campos:
                existentes += 1
            else:
                raise ValueError("Conflito com despesa confirmada: " + d["id"])
        linhas = con.execute(sql.SQL(
            "SELECT id, data, descricao, categoria, valor FROM {}.despesas ORDER BY id"
        ).format(nome)).fetchall()
        recibo = conferir_recibo({"execucao": execucao, "entrada_sha256": entrada_hash,
                                 "novas": novas, "existentes": existentes,
                                 "retrato": criar_retrato(linhas)})
        con.execute(sql.SQL("INSERT INTO {}.execucoes (id, entrada_sha256, novas, existentes, retrato) VALUES (%s, %s, %s, %s, %s)").format(nome),
                    (execucao, entrada_hash, novas, existentes, Jsonb(recibo["retrato"])))
    # Só chegamos aqui após a confirmação bem-sucedida do contexto.
    return recibo
