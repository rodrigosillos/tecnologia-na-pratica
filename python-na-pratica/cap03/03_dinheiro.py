from decimal import Decimal

print(0.10 + 0.20)
print(Decimal("0.10") + Decimal("0.20"))
print(Decimal(0.10) == Decimal("0.10"))

cafe = Decimal("12.50")
corrida = Decimal("35.00")
print("Subtotal em reais:", cafe + corrida)
