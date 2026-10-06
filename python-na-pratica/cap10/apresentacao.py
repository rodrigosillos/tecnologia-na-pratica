"""Saídas concisas com denominadores e natureza das medidas."""


def mostrar_avaliacao(relatorio):
    print("Modo:", relatorio["modo"], "| versão:", relatorio["versao_prompt"], "| partição:", relatorio["particao"])
    for nome, m in relatorio["metricas"].items():
        print(f"{nome}: {m['acertos']}/{m['total']} | falhas: {m['falhas']} | pendentes: {m['pendentes']}")
    print("Casos ausentes:", len(relatorio["casos_ausentes"]))
    print("Custo estimado USD:", relatorio["custo_estimado_usd"], "| usos ausentes:", relatorio["usos_ausentes"])
    print("Mediana ms:", relatorio["mediana_ms"])
    print(relatorio["nota_medidas"])
    print("Aprovação de despesas: não executada | Banco: não utilizado")
