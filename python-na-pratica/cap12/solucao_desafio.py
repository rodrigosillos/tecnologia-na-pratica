"""Nova regra de apresentação, separada da política e do contrato de importação."""
from decimal import Decimal
from regras import converter_valor


def destacar(registros, limite="50.00"):
    corte = converter_valor(limite)
    return [{"id": r["id"], "valor": r["valor"],
             "destaque": converter_valor(r["valor"]) >= corte}
            for r in registros]


def main():
    from arquivos import ler_entrada
    from pathlib import Path
    registros, _ = ler_entrada(Path(__file__).parent / "dados/validas.json")
    for linha in destacar(registros):
        print(linha["id"], linha["valor"], "destacar" if linha["destaque"] else "sem destaque")
    print("Destaque visual não altera total, categoria, importação ou aprovação.")


if __name__ == "__main__":
    main()
