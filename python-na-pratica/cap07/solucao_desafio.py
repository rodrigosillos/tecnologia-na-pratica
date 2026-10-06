from reproducao import carregar_caso
from interpretacao import interpretar_resposta

resposta = carregar_caso("incompleta")["resposta"]
resultado = interpretar_resposta(resposta)
print("Status recebido:", resposta["status"])
print("Há trecho parcial:", bool(resposta["output"]))
print("Pode aceitar como resposta concluída:", resultado["estado"] == "concluida")
print("Texto aceito:", resultado["texto"])
