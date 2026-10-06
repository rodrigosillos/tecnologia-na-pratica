"""Mostra os trechos completos selecionados, sem executar um modelo."""
import argparse
from documentos import carregar_corpus
from busca import recuperar
from fluxo import obter_pergunta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--caso", default=None)
    grupo.add_argument("--pergunta")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()
    try:
        pergunta = args.pergunta if args.pergunta is not None else obter_pergunta(args.caso or "P01")
        r = recuperar(pergunta, carregar_corpus(), top_k=args.top_k)
        print("Busca local | chamadas API: 0")
        print("Pergunta:", r["pergunta"])
        print("Corpus:", r["corpus_versao"])
        print("Trechos:", len(r["trechos"]))
        for t in r["trechos"]:
            print(f"[{t['id']}] {t['documento']} / {t['secao']} | pontos: {t['pontos']}")
            print(t["texto"])
        if r["sem_trechos"]:
            print("Nenhum trecho atingiu os critérios; isso não prova ausência de regra no corpus.")
        return 0
    except (ValueError, OSError) as erro:
        print("Busca:", erro)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
