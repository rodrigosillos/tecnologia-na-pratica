from conexao import configuracao_banco
from banco import consultar

retrato = consultar(configuracao_banco())
print("Despesas confirmadas:", retrato["quantidade"])
print("Total em reais:", format(retrato["total"], ".2f"))
for categoria, quantidade, total in retrato["categorias"]:
    print(categoria, quantidade, format(total, ".2f"), sep=" | ")
