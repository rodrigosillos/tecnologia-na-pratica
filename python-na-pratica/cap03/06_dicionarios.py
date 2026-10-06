from decimal import Decimal

despesa = {
    "id": "D001",
    "data": "2026-09-10",
    "descricao": "Café em reunião",
    "categoria": "Alimentação",
    "valor": "12.50",
}

print(despesa["id"])
print(despesa["descricao"])
print("Campo valor presente:", "valor" in despesa)
valor = Decimal(despesa["valor"])
print("Valor em reais:", valor)
