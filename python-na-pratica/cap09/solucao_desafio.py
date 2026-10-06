"""Compare uma afirmação com a fonte, sem consultar outro modelo."""
from arquivos import ler_json
from configuracao_ia import PASTA
from fluxo import preparar_reproducao
from validacao import analisar


def main():
    caso = next(c for c in ler_json(PASTA / "casos/contrastes.json") if c["nome"] == "unidade_alterada")
    analise = analisar(caso["resposta"], preparar_reproducao("P01")["recuperacao"])
    print("Resultado técnico:", analise["estado"])
    print("Afirmação: R$ 60,00 por refeição.")
    print("Fonte POL-002: R$ 60,00 por pessoa por dia, somando as despesas do dia.")
    print("Decisão didática: rejeitar a afirmação; a unidade foi alterada.")
    print("Uma citação literal não prova que a conclusão é sustentada por ela.")
    return 0 if analise["estado"] == "aguarda_revisao" else 1


if __name__ == "__main__":
    raise SystemExit(main())
