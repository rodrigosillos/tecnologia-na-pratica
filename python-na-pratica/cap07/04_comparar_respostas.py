from reproducao import reproduzir

print("Dois casos sintéticos da mesma entrada; chamadas à API: 0")
for nome in ["concluida", "data_inventada"]:
    resultado = reproduzir(nome)
    print("Caso:", nome, "| estado técnico:", resultado["estado"])
    print(resultado["texto"])
print("Confira a entrada: ela não informa data. Qual resposta acrescentou esse dado?")
