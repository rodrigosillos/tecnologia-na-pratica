"""Prepara os três casos sintéticos e uma revisão ainda pendente."""
import argparse
from configuracao_ia import PASTA
from arquivos import gravar_conjunto
from fluxo import preparar_reproducao, modelo_revisao


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--destino", default=str(PASTA / "gerados/reproducao"))
    args = parser.parse_args()
    try:
        pacote = preparar_reproducao()
        gravar_conjunto(args.destino, {"pacote.json": pacote,
                                     "revisao_pendente.json": modelo_revisao(pacote)})
        print("Modo: reprodução | origem: sintética | chamadas à API: 0")
        print("Sugestões: 3 | revisões pendentes: 3 | despesas gravadas no banco: 0")
        print("Arquivos:", args.destino)
        return 0
    except (ValueError, OSError) as erro:
        print("Preparação bloqueada:", erro)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
