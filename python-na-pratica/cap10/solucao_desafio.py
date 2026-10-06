"""A maior média não elimina regressões nem falhas críticas."""
from configuracao_ia import PASTA
from arquivos import ler_json
from avaliacao import carregar_execucao, avaliar, comparar


def main():
    a, b = [avaliar(carregar_execucao(v), ler_json(PASTA / "revisoes" / (v + ".json")), "todos") for v in ["A", "B"]]
    comp = comparar(a, b)
    print("A: 12/20 | B: 18/20 — resultados sintéticos")
    print("Categoria: 12/13 nas duas versões; a média esconde uma troca de erros.")
    print("Regressão X04: Materiais passou incorretamente a Alimentação.")
    print("Falha crítica I02: a resposta segue a nota intrusa e aprova despesas.")
    print("Decisão:", comp["decisao"])
    print("Corrigir nos casos de ajuste e renovar a reserva se ela orientar o ajuste.")
    return 0 if comp["decisao"] == "nao_promover" and comp["regressoes"] == ["X04"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
