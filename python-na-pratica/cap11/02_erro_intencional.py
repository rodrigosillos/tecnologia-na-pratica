"""Erro lógico isolado: não usa banco, catálogo ou IA."""


def precisa_importar(importacao_confirmada, exportacao_concluida):
    # ERRO INTENCIONAL: ignora o primeiro argumento.
    return not exportacao_concluida


def main():
    observado = precisa_importar(True, False)
    if observado is not False:
        print("Erro detectado: relatório pendente não autoriza nova importação.")
        return 1
    print("Regra conferida.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
