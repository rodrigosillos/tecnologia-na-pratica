"""Coordena leitura, validação e apresentação; não grava despesas."""
from pathlib import Path

from arquivos import ler_csv, ler_json
from calculos import somar_valores
from regras import validar_lote
from cliente_catalogo import obter_catalogo


def executar(caminho: Path, url: str) -> int:
    try:
        if caminho.suffix == ".csv":
            registros = ler_csv(caminho)
        elif caminho.suffix == ".json":
            registros = ler_json(caminho)
        else:
            raise ValueError("arquivo: use extensão .csv ou .json")
        categorias = obter_catalogo(url)
        resultado = validar_lote(registros, categorias)
    except (OSError, UnicodeError, ValueError) as erro:
        print("Lote não processado:", str(erro))
        print("Nenhuma despesa foi gravada")
        return 1

    if resultado["erros"]:
        print("Lote bloqueado")
        for mensagem in resultado["erros"]:
            print(mensagem)
        print("Nenhuma despesa foi gravada")
        return 1

    valores = []
    for despesa in resultado["despesas"]:
        valores.append(despesa["valor"])
    total = somar_valores(valores)
    print("Lote validado em memória")
    print("Despesas únicas:", len(resultado["despesas"]))
    print("Repetições idênticas:", resultado["repetidos"])
    print("Total em reais:", total)
    print("Nenhuma despesa foi gravada")
    return 0
