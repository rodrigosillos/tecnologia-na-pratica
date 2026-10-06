"""Percurso sintético, sem chave, rede ou banco."""
import argparse
from configuracao_ia import PASTA
from arquivos import gravar_conjunto
from fluxo import preparar_reproducao, conferir_pacote, apresentar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caso", default="P01")
    parser.add_argument("--destino", default=str(PASTA / "gerados/reproducao-P01"))
    args = parser.parse_args()
    try:
        pacote = preparar_reproducao(args.caso)
        analise = conferir_pacote(pacote)
        gravar_conjunto(args.destino, {"pacote.json": pacote, "analise.json": analise})
        apresentar(pacote, analise)
        print("Chamadas reais: 0 | Saída ilustrativa criada para o exercício")
        return 2 if analise["estado"] == "bloqueada" else 0
    except (ValueError, OSError) as erro:
        print("Reprodução:", erro)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
