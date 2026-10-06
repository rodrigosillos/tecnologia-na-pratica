from conexao import configuracao_banco, conectar

config = configuracao_banco()
with conectar(config) as con:
    banco, usuario = con.execute("SELECT current_database(), current_user").fetchone()
    versao = con.execute("SHOW server_version").fetchone()[0]
print("Banco:", banco)
print("Usuário:", usuario)
print("PostgreSQL:", versao)
