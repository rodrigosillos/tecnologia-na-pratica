"""Comandos de IA e revisão sem acesso ao banco."""
from copy import deepcopy
from pathlib import Path
from extracao import fluxo as extrair
from extracao import contexto as textos
from extracao.arquivos import ler_json, gravar_conjunto, resumo
from extracao.configuracao_ia import PASTA as PASTA_EXTRACAO
from consulta import fluxo as consultar


def pacote_sintetico(cenario="padrao"):
    pacote = extrair.preparar_reproducao()
    if cenario != "padrao":
        if cenario not in {"incompleta", "recusa"}:
            raise ValueError("Cenário desconhecido")
        nome = "resposta_incompleta" if cenario == "incompleta" else "recusa"
        caso = next(c for c in ler_json(PASTA_EXTRACAO / "casos/erros.json") if c["nome"] == nome)
        pacote = deepcopy(pacote)
        next(i for i in pacote["itens"] if i["origem_id"] == "T002")["resposta"] = caso["resposta"]
    return pacote


def preparar_sugestoes(destino, cenario="padrao"):
    pacote = pacote_sintetico(cenario)
    analises = extrair.conferir_pacote(pacote)
    gravar_conjunto(destino, {"pacote.json": pacote, "analises.json": analises,
                             "revisao_pendente.json": extrair.modelo_revisao(pacote)})
    print("Modo: reproducao | origem: sintetica | chamadas reais: 0")
    for nome, a in analises.items():
        print(nome, a["estado"], "pendências:", ", ".join(a["pendencias"]) or "nenhuma de preenchimento")
    return 1 if any(a["estado"] == "bloqueada" for a in analises.values()) else 0


def inspecionar(caminho):
    pacote = ler_json(caminho)
    analises = extrair.conferir_pacote(pacote)
    fontes = textos.origens()
    print("Modo:", pacote["modo"], "Origem:", pacote["origem"])
    for nome, a in analises.items():
        print(nome, "->", fontes[nome]["id_destino"])
        print("Original:", fontes[nome]["texto"])
        print("Sugestão:", a["sugestao"])
        print("Estado:", a["estado"], "Pendências:", a["pendencias"], "Erros:", a["erros"])
    return 0


def lote_revisado(pacote, revisao):
    registros, trilha = extrair.revisar(pacote, revisao)
    if not registros:
        raise ValueError("Revisão não liberou despesas; nada a importar")
    origem = {"tipo": "revisada", "pacote": pacote, "revisao": revisao, "trilha": trilha}
    return registros, resumo({"pacote": pacote, "revisao": revisao}), origem


def revisar_sugestoes(caminho_pacote, caminho_revisao, destino):
    registros, h, proveniencia = lote_revisado(ler_json(caminho_pacote), ler_json(caminho_revisao))
    gravar_conjunto(destino, {"lote.json": registros, "trilha.json": proveniencia["trilha"]})
    print("Revisão conferida:", len(registros), "registros /", proveniencia["trilha"]["total_lote_revisado"])
    print("Rejeitados:", proveniencia["trilha"]["rejeitados"], "| Banco: não utilizado")
    return 0


def consulta_sintetica(nome, destino):
    pacote = consultar.preparar_reproducao(nome)
    analise = consultar.conferir_pacote(pacote)
    gravar_conjunto(destino, {"pacote.json": pacote, "analise.json": analise,
                             "recuperacao.json": pacote["recuperacao"]})
    consultar.apresentar(pacote, analise)
    return 1 if analise["estado"] == "bloqueada" else 0
