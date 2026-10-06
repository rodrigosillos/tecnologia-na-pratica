"""Avalia execução arquivada e mantém explícita a cobertura parcial."""
import argparse
from arquivos import ler_json, gravar_conjunto
from avaliacao import avaliar
from apresentacao import mostrar_avaliacao


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--execucao", required=True)
    p.add_argument("--revisao")
    p.add_argument("--destino", required=True)
    a = p.parse_args()
    try:
        execucao = ler_json(a.execucao)
        revisao = ler_json(a.revisao) if a.revisao else None
        rel = avaliar(execucao, revisao, "todos", permitir_parcial=True)
        gravar_conjunto(a.destino, {"avaliacao.json": rel})
        mostrar_avaliacao(rel)
        return 0
    except (ValueError, OSError) as erro:
        print("Avaliação:", erro)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
