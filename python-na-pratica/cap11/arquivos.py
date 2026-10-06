"""Leitura única e limitada; o hash identifica os bytes efetivamente lidos."""
import csv
import hashlib
import io
import json
from pathlib import Path
from regras import CAMPOS, LIMITE_REGISTROS


def objeto_sem_chaves_repetidas(pares):
    resultado = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError("JSON: chave repetida")
        resultado[chave] = valor
    return resultado


def rejeitar_constante(nome):
    raise ValueError("JSON: constante não permitida")


def carregar_json(texto):
    try:
        return json.loads(texto, object_pairs_hook=objeto_sem_chaves_repetidas,
                          parse_constant=rejeitar_constante)
    except (json.JSONDecodeError, RecursionError) as erro:
        raise ValueError("JSON: estrutura inválida") from erro


def ler_entrada(caminho):
    caminho = Path(caminho)
    if caminho.suffix.lower() not in {".json", ".csv"}:
        raise ValueError("Use entrada .json ou .csv")
    with caminho.open("rb") as arquivo:
        dados = arquivo.read(1_048_577)
    if len(dados) > 1_048_576:
        raise ValueError("Entrada acima de 1 MiB")
    texto = dados.decode("utf-8-sig")
    if caminho.suffix.lower() == ".json":
        registros = carregar_json(texto)
    else:
        leitor = csv.DictReader(io.StringIO(texto, newline=""), strict=True)
        if leitor.fieldnames != CAMPOS:
            raise ValueError("CSV: cabeçalho diferente do contrato")
        try:
            registros = list(leitor)
        except csv.Error as erro:
            raise ValueError("CSV: estrutura inválida") from erro
    if not isinstance(registros, list) or not 1 <= len(registros) <= LIMITE_REGISTROS:
        raise ValueError("Entrada: informe de 1 a 1000 registros")
    return registros, hashlib.sha256(dados).hexdigest()


def json_bytes(objeto):
    return (json.dumps(objeto, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")
