from decimal import Decimal

valor = Decimal("35.00")
print("É Decimal:", isinstance(valor, Decimal))
print("É finito:", valor.is_finite())
print("É texto:", isinstance(valor, str))
