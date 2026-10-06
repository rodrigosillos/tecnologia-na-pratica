from decimal import Decimal

from calculos import somar_valores
from regras import converter_valor

valores = [Decimal("12.50"), Decimal("35.00"), Decimal("80.00")]
obtido = somar_valores(valores)
esperado = Decimal("127.50")
if obtido != esperado:
    raise AssertionError("A soma da base deveria ser 127.50")

try:
    converter_valor("0.00")
except ValueError:
    print("Valor zero rejeitado como esperado")
else:
    raise AssertionError("A regra aceitou um valor zero")

print("Verificações da regra: 2/2")
