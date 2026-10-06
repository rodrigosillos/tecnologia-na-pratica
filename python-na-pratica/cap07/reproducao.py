"""Casos sintéticos identificados; nenhuma chamada ao provedor."""
import json
from configuracao_ia import PASTA
from contexto import pedido_exemplo, sha256_texto
from interpretacao import interpretar_resposta

CASOS = ("concluida", "incompleta", "recusada", "sem_texto", "sem_uso", "data_inventada")


def carregar_caso(nome):
    if nome not in CASOS:
        raise ValueError("Caso de reprodução desconhecido")
    caso = json.loads((PASTA / "casos" / (nome + ".json")).read_text(encoding="utf-8"))
    pedido = pedido_exemplo()
    if caso.get("origem") != "sintetica":
        raise ValueError("A revisão espera casos sintéticos identificados")
    if (caso.get("input_sha256") != sha256_texto(pedido["input"])
            or caso.get("instructions_sha256") != sha256_texto(pedido["instructions"])):
        raise ValueError("Caso gravado não corresponde à entrada e às instruções atuais")
    return caso


def reproduzir(nome):
    return interpretar_resposta(carregar_caso(nome)["resposta"])


def apresentar(resultado):
    print("Estado:", resultado["estado"])
    print(resultado["motivo"])
    if resultado["texto"] is not None:
        print("Texto para revisão:")
        print(resultado["texto"])
    if resultado["uso"] is not None:
        uso = resultado["uso"]
        print("Tokens:", uso["input_tokens"], "entrada |", uso["output_tokens"], "saída |", uso["total_tokens"], "total")
