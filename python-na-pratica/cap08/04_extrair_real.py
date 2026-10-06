"""Extensão opcional; uso sem confirmação não faz envio."""
import argparse
from configuracao_ia import PASTA
from execucao_real import executar_real


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--origem", default="T001", choices=["T001", "T002", "T003"])
    parser.add_argument("--destino", default=str(PASTA / "gerados/api-real"))
    parser.add_argument("--confirmar-envio", action="store_true")
    args = parser.parse_args()
    raise SystemExit(executar_real(args.origem, args.destino, args.confirmar_envio))
