from conexao import configuracao_banco
from banco import preparar

config = configuracao_banco()
preparar(config)
print("Estrutura tnp_cap06 preparada; despesas existentes preservadas")
