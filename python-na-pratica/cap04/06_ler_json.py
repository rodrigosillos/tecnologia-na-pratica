import json
from pathlib import Path

caminho = Path(__file__).resolve().parent / "dados" / "validas.json"
with caminho.open("r", encoding="utf-8-sig") as arquivo:
    registros = json.load(arquivo)

print("Registros lidos, ainda sem validação:", len(registros))
print("Primeiro valor:", registros[0]["valor"])
print("Valor ainda é texto:", isinstance(registros[0]["valor"], str))
