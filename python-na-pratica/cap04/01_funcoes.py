from decimal import Decimal


def somar_valores(valores):
    total = Decimal("0.00")
    for valor in valores:
        total = total + valor
    return total


valores = [Decimal("12.50"), Decimal("35.00"), Decimal("80.00")]
resultado = somar_valores(valores)
print("Total em reais:", resultado)
print("Lista vazia:", somar_valores([]))
