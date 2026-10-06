from conexao import configuracao_banco, conectar

config = configuracao_banco()
with conectar(config) as con:
    linha = con.execute(
        """SELECT descricao, valor
           FROM tnp_cap06.despesas
           WHERE id = %s""",
        ("D002",),
    ).fetchone()

if linha is None:
    print("Despesa não encontrada")
else:
    print("Descrição:", linha[0])
    print("Valor em reais:", format(linha[1], ".2f"))
