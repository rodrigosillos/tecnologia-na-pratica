"""Cálculos recebem valores já validados; não leem arquivos ou imprimem."""
from decimal import Decimal


def somar_valores(valores: list[Decimal]) -> Decimal:
    total = Decimal("0.00")
    for valor in valores:
        total = total + valor
    return total
