"""Mostra a sugestão ao lado do documento; não chama API nem altera dados."""
import argparse
from configuracao_ia import PASTA
from arquivos import ler_json
from fluxo import conferir_pacote
from contexto import origens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pacote", default=str(PASTA / "gerados/reproducao/pacote.json"))
    args = parser.parse_args()
    try:
        pacote = ler_json(args.pacote)
        analises = conferir_pacote(pacote)
        print("Origem do pacote:", pacote["origem"])
        print("Chamadas à API nesta inspeção: 0")
        for nome, analise in analises.items():
            print(nome + " | " + analise["estado"])
            print("Fonte:", origens()[nome]["texto"])
            print("Sugestão:", analise["sugestao"])
            print("Pendências:", ", ".join(analise["pendencias"]) or "nenhuma de preenchimento")
            for erro in analise["erros"]:
                print("Bloqueio:", erro)
        print("Toda sugestão precisa de decisão explícita.")
        return 2 if any(a["estado"] == "bloqueada" for a in analises.values()) else 0
    except (ValueError, OSError) as erro:
        print("Inspeção bloqueada:", erro)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
