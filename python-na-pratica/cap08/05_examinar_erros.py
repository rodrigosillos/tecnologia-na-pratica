"""Contrasta campos válidos, referências inválidas e interpretação incorreta."""
from configuracao_ia import PASTA
from arquivos import ler_json
from contexto import origens, categorias
from validacao import analisar


if __name__ == "__main__":
    print("Casos sintéticos | chamadas à API: 0")
    for caso in ler_json(PASTA / "casos/erros.json"):
        analise = analisar(caso["resposta"], origens()[caso["origem_id"]]["texto"], categorias())
        print(caso["nome"] + ": " + analise["estado"])
    print("Substring existente não comprova categoria adequada nem escolha do total correto.")
