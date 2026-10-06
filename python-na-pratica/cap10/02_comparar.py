"""Compara versões no mesmo conjunto e na mesma partição."""
import argparse
from configuracao_ia import PASTA
from arquivos import ler_json, gravar_conjunto
from avaliacao import carregar_execucao, avaliar, comparar


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--particao", choices=["ajuste", "reserva", "todos"], default="ajuste")
    p.add_argument("--destino")
    a = p.parse_args()
    try:
        rels = {v: avaliar(carregar_execucao(v), ler_json(PASTA / "revisoes" / (v + ".json")), a.particao) for v in ["A", "B"]}
        comp = comparar(rels["A"], rels["B"])
        destino = a.destino or PASTA / "gerados" / ("comparacao-" + a.particao)
        gravar_conjunto(destino, {"A.json": rels["A"], "B.json": rels["B"], "comparacao.json": comp})
        print("Comparação sintética | partição:", a.particao)
        for v, r in rels.items():
            m = r["metricas"]["casos"]
            print(f"{v}: {m['acertos']}/{m['total']} | pendentes: {m['pendentes']}")
        print("Melhorias:", ", ".join(comp["melhorias"]) or "nenhuma")
        print("Regressões:", ", ".join(comp["regressoes"]) or "nenhuma")
        print("Decisão:", comp["decisao"])
        for razao in comp["razoes"]:
            print(razao)
        print(comp["nota"])
        return 0
    except (ValueError, OSError) as erro:
        print("Comparação:", erro)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
