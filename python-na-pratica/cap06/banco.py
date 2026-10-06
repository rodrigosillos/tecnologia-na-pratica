"""Persistência transacional; uma execução de aplicação por vez."""
from pathlib import Path
from re import fullmatch
from psycopg import sql
from conexao import conectar
from regras import validar_lote

ESQUEMA = "tnp_cap06"


def identificador_esquema(esquema):
    if esquema != ESQUEMA and fullmatch(r"tnp_c06_t_[a-f0-9]{16}", esquema) is None:
        raise ValueError("Esquema fora do laboratório")
    return sql.Identifier(esquema)


def preparar(config, esquema=ESQUEMA):
    nome = identificador_esquema(esquema)
    # Todas as instruções vêm deste arquivo local fornecido, nunca da entrada.
    fonte = (Path(__file__).resolve().parent / "sql/esquema.sql").read_text(encoding="utf-8")
    with conectar(config) as con:
        for comando in fonte.split(";\n"):
            if comando.strip():
                con.execute(sql.SQL(comando).format(esquema=nome))
        versao = con.execute(sql.SQL("SELECT versao FROM {}.metadados WHERE chave = 1").format(nome)).fetchone()
        if versao != (1,):
            raise ValueError("Esquema incompatível com o capítulo 6")


def importar(config, registros, categorias, esquema=ESQUEMA):
    resultado = validar_lote(registros, categorias)
    if resultado["erros"]:
        raise ValueError("; ".join(resultado["erros"]))
    nome = identificador_esquema(esquema)
    novas = 0
    existentes = 0
    with conectar(config) as con:
        for despesa in resultado["despesas"]:
            campos = (despesa["data"], despesa["descricao"],
                      despesa["categoria"], despesa["valor"])
            anterior = con.execute(
                sql.SQL("SELECT data, descricao, categoria, valor FROM {}.despesas WHERE id = %s").format(nome),
                (despesa["id"],),
            ).fetchone()
            if anterior is None:
                con.execute(
                    sql.SQL("INSERT INTO {}.despesas (id, data, descricao, categoria, valor) VALUES (%s, %s, %s, %s, %s)").format(nome),
                    (despesa["id"],) + campos,
                )
                novas += 1
            elif anterior == campos:
                existentes += 1
            else:
                raise ValueError("conflito com despesa já gravada: " + despesa["id"])
    # O retorno ocorre depois da saída bem-sucedida do contexto de conexão.
    return {"novas": novas, "existentes": existentes,
            "repetidas_entrada": resultado["repetidos"]}


def consultar(config, esquema=ESQUEMA):
    nome = identificador_esquema(esquema)
    with conectar(config) as con:
        con.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        linhas = con.execute(sql.SQL(
            "SELECT id, data, descricao, categoria, valor FROM {}.despesas ORDER BY id"
        ).format(nome)).fetchall()
        grupos = con.execute(sql.SQL(
            "SELECT categoria, count(*), sum(valor) FROM {}.despesas GROUP BY categoria ORDER BY categoria COLLATE \"C\""
        ).format(nome)).fetchall()
        quantidade, total = con.execute(sql.SQL(
            "SELECT count(*), COALESCE(sum(valor), 0.00) FROM {}.despesas"
        ).format(nome)).fetchone()
    return {"despesas": linhas, "categorias": grupos, "quantidade": quantidade, "total": total}
