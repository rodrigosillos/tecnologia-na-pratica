from contexto import pedido_exemplo, sha256_texto
from configuracao_ia import obter_chave

pedido = pedido_exemplo()
print("Nenhuma chamada será feita por este programa.")
print("Modelo:", pedido["model"])
print("Limite de saída:", pedido["max_output_tokens"], "tokens")
print("Instruções:")
print(pedido["instructions"].strip())
print("Entrada:")
print(pedido["input"].strip())
print("SHA-256 da entrada:", sha256_texto(pedido["input"]))
try:
    obter_chave()
except ValueError:
    print("Chave: ausente ou precisa de correção")
else:
    print("Chave: presente no ambiente; valor não exibido")
