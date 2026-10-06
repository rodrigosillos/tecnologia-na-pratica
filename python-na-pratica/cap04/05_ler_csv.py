import csv
from pathlib import Path

caminho = Path(__file__).resolve().parent / "dados" / "validas.csv"
with caminho.open("r", encoding="utf-8-sig", newline="") as arquivo:
    leitor = csv.DictReader(arquivo, delimiter=",")
    registros = list(leitor)

print("Registros lidos, ainda sem validação:", len(registros))
print("Primeiro valor:", registros[0]["valor"])
print("Valor ainda é texto:", isinstance(registros[0]["valor"], str))
