from decimal import Decimal


def exigir_positivo(valor: Decimal) -> Decimal:
    if valor <= Decimal("0.00"):
        raise ValueError("valor: deve ser maior que zero")
    return valor


try:
    valor = exigir_positivo(Decimal("0.00"))
    print("Valor aceito:", valor)
except ValueError as erro:
    print("Entrada rejeitada:", str(erro))

print("Conferência encerrada")
