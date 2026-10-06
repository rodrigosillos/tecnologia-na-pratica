categorias = ["Alimentação", "Transporte", "Materiais"]
categoria = "Transporte"
data_informada = None

if data_informada is None:
    print("Pendente: informar a data")
elif categoria not in categorias:
    print("Pendente: revisar a categoria")
else:
    print("Data informada e categoria conhecida")
