"""Classifica o próximo passo; não executa ações nem substitui a consulta."""


def decidir(importacao, exportacao):
    if importacao not in {"confirmada", "ausente", "incerta"} or exportacao not in {"pendente", "concluida"}:
        raise ValueError("Estado desconhecido")
    if importacao == "incerta":
        return "consultar"
    if importacao == "ausente":
        if exportacao == "concluida":
            raise ValueError("Arquivo sem recibo confirmado exige investigação")
        return "importar"
    return "conferir" if exportacao == "concluida" else "exportar"


def main():
    for importacao, exportacao in [("ausente", "pendente"), ("confirmada", "pendente"),
                                   ("confirmada", "concluida"), ("incerta", "pendente")]:
        print(importacao, "/", exportacao, "->", decidir(importacao, exportacao))


if __name__ == "__main__":
    main()
