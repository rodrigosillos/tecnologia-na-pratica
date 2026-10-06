from datetime import date
from decimal import Decimal

despesas = [
    {
        "id": "D001",
        "data": "2026-09-10",
        "descricao": "Café em reunião",
        "categoria": "Alimentação",
        "valor": "12.50",
    },
    {
        "id": "D002",
        "data": "2026-09-10",
        "descricao": "Corrida para visitar cliente",
        "categoria": "Transporte",
        "valor": "35.00",
    },
    {
        "id": "D003",
        "data": "2026-09-10",
        "descricao": "Cabo para o escritório",
        "categoria": "Materiais",
        "valor": "80.00",
    },
]

inicio = date(2026, 9, 1)
fim = date(2026, 10, 1)
categoria_alvo = "Materiais"
quantidade = 0
total = Decimal("0.00")
quantidade_categoria = 0
total_categoria = Decimal("0.00")

for despesa in despesas:
    data_despesa = date.fromisoformat(despesa["data"])
    valor = Decimal(despesa["valor"])

    if inicio <= data_despesa < fim:
        quantidade = quantidade + 1
        total = total + valor

        if despesa["categoria"] == categoria_alvo:
            quantidade_categoria = quantidade_categoria + 1
            total_categoria = total_categoria + valor

print("Despesas no período:", quantidade)
print("Total em reais:", total)
print("Categoria:", categoria_alvo)
print("Despesas da categoria:", quantidade_categoria)
print("Subtotal em reais:", total_categoria)
