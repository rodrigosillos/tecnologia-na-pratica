from decimal import Decimal

from calculos import somar_valores

total = Decimal("999.00")
valores = [Decimal("12.50"), Decimal("35.00"), Decimal("80.00")]
print("Calculado:", somar_valores(valores))
print("Outra chamada:", somar_valores(valores))
print("Variável externa:", total)
