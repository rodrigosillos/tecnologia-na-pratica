"""Recalcula a validação e mostra as fontes; não aceita um parecer salvo."""
import argparse
from configuracao_ia import PASTA
from arquivos import ler_json
from fluxo import conferir_pacote, apresentar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pacote", default=str(PASTA / "gerados/reproducao-P01/pacote.json"))
    args = parser.parse_args()
    try:
        pacote = ler_json(args.pacote)
        analise = conferir_pacote(pacote)
        apresentar(pacote, analise)
        print("Fontes completas usadas no contexto:")
        for t in pacote["recuperacao"]["trechos"]:
            print(f"[{t['id']}] {t['documento']} / {t['secao']}")
            print(t["texto"])
        return 2 if analise["estado"] == "bloqueada" else 0
    except (ValueError, OSError) as erro:
        print("Conferência:", erro)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
