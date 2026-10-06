despesas = [
    {"id": "D001", "categoria": "Alimentação"},
    {"id": "D002", "categoria": "Transporte"},
    {"id": "D003", "categoria": "Materiais"},
]
selecionados = []

for despesa in despesas:
    if despesa["categoria"] == "Transporte":
        selecionados.append(despesa["id"])

print("IDs selecionados:", selecionados)
print("Registros de origem:", len(despesas))
