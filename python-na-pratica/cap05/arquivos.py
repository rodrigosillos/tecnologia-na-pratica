"""Adaptadores locais CSV/JSON, com limites para o laboratório pequeno."""
import csv
import io
import json
from pathlib import Path

from regras import CAMPOS, LIMITE_REGISTROS

LIMITE_BYTES = 1_048_576


def ler_texto(caminho: Path) -> str:
    with caminho.open("rb") as arquivo:
        conteudo = arquivo.read(LIMITE_BYTES + 1)
    if len(conteudo) > LIMITE_BYTES:
        raise ValueError("arquivo: limite de 1 MiB excedido")
    return conteudo.decode("utf-8-sig")


def ler_csv(caminho: Path) -> list:
    texto = ler_texto(caminho)
    registros = []
    try:
        with io.StringIO(texto, newline="") as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=",", strict=True)
            if leitor.fieldnames != CAMPOS:
                raise ValueError("CSV: cabeçalho diferente do contrato")
            for registro in leitor:
                if len(registros) >= LIMITE_REGISTROS:
                    raise ValueError("lote: limite de 1000 registros excedido")
                registros.append(registro)
    except csv.Error as erro:
        raise ValueError("CSV: estrutura inválida") from erro
    return registros


def objeto_sem_chaves_repetidas(pares: list) -> dict:
    resultado = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError("JSON: chave repetida")
        resultado[chave] = valor
    return resultado


def rejeitar_constante(nome: str):
    raise ValueError("JSON: constante não permitida: " + nome)


def ler_json(caminho: Path) -> list:
    texto = ler_texto(caminho)
    try:
        registros = json.loads(
            texto,
            object_pairs_hook=objeto_sem_chaves_repetidas,
            parse_constant=rejeitar_constante,
        )
    except json.JSONDecodeError as erro:
        raise ValueError("JSON: estrutura inválida") from erro
    except RecursionError as erro:
        raise ValueError("JSON: aninhamento excessivo") from erro
    if not isinstance(registros, list):
        raise ValueError("JSON: a raiz deve ser uma lista")
    if len(registros) > LIMITE_REGISTROS:
        raise ValueError("lote: limite de 1000 registros excedido")
    return registros
