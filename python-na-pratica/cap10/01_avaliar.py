"""Avalia respostas sintéticas com rubricas identificadas."""
import argparse
from configuracao_ia import PASTA
from arquivos import ler_json, gravar_conjunto
from avaliacao import carregar_execucao, avaliar, modelo_revisao
from apresentacao import mostrar_avaliacao


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--versao", choices=["A", "B"], default="A")
    p.add_argument("--particao", choices=["ajuste", "reserva", "todos"], default="ajuste")
    p.add_argument("--sem-revisao", action="store_true")
    p.add_argument("--destino")
    a = p.parse_args()
    try:
        e = carregar_execucao(a.versao)
        rev = None if a.sem_revisao else ler_json(PASTA / "revisoes" / (a.versao + ".json"))
        rel = avaliar(e, rev, a.particao)
        destino = a.destino or PASTA / "gerados" / f"avaliacao-{a.versao}-{a.particao}"
        gravar_conjunto(destino, {"avaliacao.json": rel, "revisao_pendente.json": modelo_revisao(e)})
        mostrar_avaliacao(rel)
        print("Chamadas reais: 0")
        return 0
    except (ValueError, OSError) as erro:
        print("Avaliação:", erro)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
