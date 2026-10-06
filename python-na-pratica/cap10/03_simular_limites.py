"""Exercita limites sem rede, chave ou consumo real."""
import argparse
from custos import novo_controle, reservar, concluir, retrato
from arquivos import serializar


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cenario", choices=["orcamento", "chamadas", "incerto"], default="orcamento")
    a = p.parse_args()
    controle = novo_controle(1 if a.cenario == "chamadas" else 3,
                            "0.002000" if a.cenario == "orcamento" else "0.010000")
    reserva = reservar(controle, 1000, 768)
    print("Simulação local | chamadas reais: 0")
    print("Reserva estimada USD:", reserva)
    uso = None if a.cenario == "incerto" else {"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500}
    custo = concluir(controle, uso)
    print("Custo do uso:", "desconhecido" if custo is None else str(custo))
    try:
        reservar(controle, 1000, 768)
    except ValueError as erro:
        print("Próxima tentativa bloqueada:", erro)
        print(serializar(retrato(controle)).strip())
        return 0
    print("Falha do exemplo: o bloqueio esperado não ocorreu")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
