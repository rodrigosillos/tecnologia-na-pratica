propostas = [
    {
        "id_proposta": "P001",
        "texto": "Corrida de aplicativo para reunião com cliente, R$ 35,00.",
        "data": None,
        "categoria": "Transporte",
        "valor": "35.00",
        "revisada": False,
    },
    {
        "id_proposta": "P002",
        "texto": "Almoço depois da visita, 42 reais",
        "data": None,
        "categoria": "Alimentação",
        "valor": "42.00",
        "revisada": False,
    },
]
pendentes = 0

for proposta in propostas:
    if proposta["data"] is None:
        pendentes = pendentes + 1
        print(proposta["id_proposta"], "Pendente: informar a data")
    elif not proposta["revisada"]:
        pendentes = pendentes + 1
        print(proposta["id_proposta"], "Pendente: revisão humana")
    else:
        print(proposta["id_proposta"], "Seguir para validação completa")

print("Propostas pendentes:", pendentes)
print("Nenhuma proposta foi importada")
