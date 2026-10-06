"""Contrastes sintéticos: validação técnica não resolve significado."""
from arquivos import ler_json
from configuracao_ia import PASTA
from fluxo import preparar_reproducao
from validacao import analisar


def main():
    r = preparar_reproducao("P01")["recuperacao"]
    for caso in ler_json(PASTA / "casos/contrastes.json"):
        resultado = analisar(caso["resposta"], r)
        print(caso["nome"], "->", resultado["estado"])
        if resultado["estado"] != caso["esperado"]:
            return 1
    print("Unidade alterada e condição invertida exigem rejeição humana, mesmo com citações válidas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
