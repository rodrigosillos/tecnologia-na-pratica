"""Uma chamada autenticada opcional, sempre mediante confirmação explícita."""
import argparse
from configuracao_ia import PASTA
from fluxo import obter_pergunta
from execucao_real import executar_real


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--caso", default=None)
    grupo.add_argument("--pergunta")
    parser.add_argument("--destino", default=str(PASTA / "gerados/api-real"))
    parser.add_argument("--confirmar-envio", action="store_true")
    args = parser.parse_args()
    try:
        pergunta = args.pergunta if args.pergunta is not None else obter_pergunta(args.caso or "P01")
        return executar_real(pergunta, args.destino, args.confirmar_envio)
    except (ValueError, OSError) as erro:
        print("Configuração:", erro)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
