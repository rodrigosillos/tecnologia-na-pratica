"""Extensão opcional: uma chamada, escolhida pelo leitor."""
import argparse
from configuracao_ia import PASTA
from execucao_real import executar_real


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--caso", default="R01")
    p.add_argument("--versao", choices=["A", "B"], default="B")
    p.add_argument("--confirmar-envio", action="store_true")
    p.add_argument("--orcamento-usd", default="0.010000")
    p.add_argument("--limite-saida", type=int, default=768)
    p.add_argument("--limite-caracteres", type=int, default=16000)
    p.add_argument("--destino", default=str(PASTA / "gerados/amostra-real"))
    a = p.parse_args()
    return executar_real(a.caso, a.destino, a.confirmar_envio, a.versao,
                         a.orcamento_usd, a.limite_saida, a.limite_caracteres)


if __name__ == "__main__":
    raise SystemExit(main())
