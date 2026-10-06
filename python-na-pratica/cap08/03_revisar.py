"""Aplica um arquivo de decisões e exporta um lote; nunca conecta ao banco."""
import argparse
from configuracao_ia import PASTA
from arquivos import ler_json, gravar_conjunto
from fluxo import revisar


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pacote", default=str(PASTA / "gerados/reproducao/pacote.json"))
    parser.add_argument("--revisao", required=True)
    parser.add_argument("--destino", default=str(PASTA / "gerados/revisado"))
    args = parser.parse_args()
    try:
        lote, trilha = revisar(ler_json(args.pacote), ler_json(args.revisao))
        gravar_conjunto(args.destino, {"lote_revisado.json": lote, "trilha_revisao.json": trilha})
        print("Revisão aplicada | origem:", trilha["origem"])
        print("Registros para o percurso determinístico:", trilha["registros"])
        print("Rejeitados:", trilha["rejeitados"])
        print("Total do lote revisado:", trilha["total_lote_revisado"])
        print("Persistência no banco: não executada")
        return 0
    except (ValueError, OSError) as erro:
        print("Revisão bloqueada:", erro)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
