"""Contrato de despesas do capítulo 5; não faz persistência."""
from datetime import date
from decimal import Decimal
from re import fullmatch

CAMPOS = ["id", "data", "descricao", "categoria", "valor"]
LIMITE_REGISTROS = 1000


def texto_obrigatorio(valor: object, campo: str, limite: int) -> str:
    if not isinstance(valor, str):
        raise ValueError(campo + ": informe texto")
    if not valor or valor != valor.strip():
        raise ValueError(campo + ": vazio ou com espaços nas extremidades")
    if len(valor) > limite:
        raise ValueError(campo + ": texto acima do limite")
    return valor


def converter_valor(texto: str) -> Decimal:
    if not isinstance(texto, str):
        raise ValueError("valor: informe texto, por exemplo 12.50")
    if fullmatch(r"[0-9]{1,7}\.[0-9]{2}", texto) is None:
        raise ValueError("valor: use 1 a 7 dígitos, ponto e 2 casas decimais")
    valor = Decimal(texto)
    if valor <= Decimal("0.00"):
        raise ValueError("valor: deve ser maior que zero")
    return valor


def converter_data(texto: str) -> date:
    if not isinstance(texto, str):
        raise ValueError("data: informe texto no formato AAAA-MM-DD")
    if fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", texto) is None:
        raise ValueError("data: use AAAA-MM-DD")
    try:
        return date.fromisoformat(texto)
    except ValueError as erro:
        raise ValueError("data: dia, mês ou ano impossível") from erro


def validar_despesa(registro: dict, categorias: list[str]) -> dict:
    if not isinstance(registro, dict):
        raise ValueError("registro: esperado um objeto com campos")
    if len(registro) != len(CAMPOS):
        raise ValueError("registro: campos ausentes ou extras")
    for campo in CAMPOS:
        if campo not in registro:
            raise ValueError("registro: campos ausentes ou extras")

    identificador = texto_obrigatorio(registro["id"], "id", 9)
    if fullmatch(r"D[0-9]{3,8}", identificador) is None:
        raise ValueError("id: use D seguido de 3 a 8 dígitos")
    descricao = texto_obrigatorio(registro["descricao"], "descricao", 120)
    categoria = texto_obrigatorio(registro["categoria"], "categoria", 30)
    if categoria not in categorias:
        raise ValueError("categoria: não consta no catálogo recebido")
    data_despesa = converter_data(registro["data"])
    valor = converter_valor(registro["valor"])

    return {
        "id": identificador,
        "data": data_despesa,
        "descricao": descricao,
        "categoria": categoria,
        "valor": valor,
    }


def validar_lote(registros: list, categorias: list[str]) -> dict:
    if not isinstance(registros, list):
        raise ValueError("lote: esperado uma lista de registros")
    if len(registros) > LIMITE_REGISTROS:
        raise ValueError("lote: limite de 1000 registros excedido")
    por_id = {}
    erros = []
    repetidos = 0
    posicao = 0

    for registro in registros:
        posicao = posicao + 1
        try:
            despesa = validar_despesa(registro, categorias)
            identificador = despesa["id"]
            if identificador in por_id:
                if por_id[identificador] != despesa:
                    raise ValueError("id: conteúdo conflitante para " + identificador)
                repetidos = repetidos + 1
            else:
                por_id[identificador] = despesa
        except ValueError as erro:
            erros.append("Registro " + str(posicao) + ": " + str(erro))

    if erros:
        return {"despesas": [], "erros": erros, "repetidos": repetidos}
    return {
        "despesas": list(por_id.values()),
        "erros": [],
        "repetidos": repetidos,
    }
