from decimal import Decimal

valores_texto = ["12.50", "35.00", "80.00"]
total = Decimal("0.00")
quantidade = 0

for valor_texto in valores_texto:
    valor = Decimal(valor_texto)
    total = total + valor
    quantidade = quantidade + 1
    print("Acumulado:", total)

print("Quantidade:", quantidade)
print("Total em reais:", total)
