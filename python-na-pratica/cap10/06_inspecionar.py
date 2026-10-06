"""Mostra entrada, critério, resultado e revisão de um caso sintético."""
import argparse
from configuracao_ia import PASTA
from arquivos import ler_json, serializar
from conjunto import obter_caso, recuperar_caso
from avaliacao import carregar_execucao


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--caso", default="X02")
    p.add_argument("--versao", choices=["A", "B"], default="A")
    a = p.parse_args()
    try:
        c = obter_caso(a.caso)
        e = carregar_execucao(a.versao)
        i = next(x for x in e["itens"] if x["caso_id"] == c["id"])
        print("Caso:", c["id"], "| partição:", c["particao"], "| saída sintética:", a.versao)
        print("Entrada:", c["entrada"])
        print("Critério:", c["criterio"])
        print("Gabarito:", serializar(c["gabarito"]).strip())
        print("Resposta:", i["resposta"]["output"][0]["content"][0]["text"].strip())
        if c["tarefa"] == "consulta":
            print("Trechos recuperados:", serializar(recuperar_caso(c)["trechos"]).strip())
            rev = ler_json(PASTA / "revisoes" / (a.versao + ".json"))
            print("Rubrica sintética:", next(x["justificativa"] for x in rev["itens"] if x["caso_id"] == c["id"]))
        return 0
    except (ValueError, OSError) as erro:
        print("Inspeção:", erro)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
