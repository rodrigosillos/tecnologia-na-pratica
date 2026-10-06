"""Métricas por dimensão; revisão de referência explicitamente sintética."""
from copy import deepcopy
from decimal import Decimal
from statistics import median
from arquivos import ler_json, resumo
from configuracao_ia import PASTA, MODELO, SDK
from conjunto import carregar, selecionar, obter_caso, identidade, recuperar_caso
from interpretacao import interpretar_resposta
from contrato_extracao import validar_estrutura as estrutura_extracao
from contrato_consulta import validar_estrutura as estrutura_consulta
from validacao_extracao import analisar as analisar_extracao
from validacao_consulta import analisar as analisar_consulta
from custos import custo_de_uso


def carregar_execucao(versao):
    if versao not in {"A", "B"}:
        raise ValueError("Versão desconhecida")
    return ler_json(PASTA / "execucoes" / (versao + ".json"))


def conferir_execucao(execucao):
    if (not isinstance(execucao, dict) or execucao.get("modo") not in {"sintetico", "api_real"}
            or execucao.get("dataset_sha256") != resumo(carregar())
            or execucao.get("modelo") != MODELO or execucao.get("sdk") != SDK
            or execucao.get("versao_prompt") not in {"A", "B"}):
        raise ValueError("Execução incompatível com conjunto, SDK, modelo ou versão")
    itens = execucao.get("itens")
    if not isinstance(itens, list) or not itens or len(itens) > 20:
        raise ValueError("Lista de resultados inválida")
    ids = set()
    for item in itens:
        if not isinstance(item, dict) or set(item) != {"caso_id", "pedido_sha256", "limite_saida", "duracao_ms", "resposta"}:
            raise ValueError("Campos do resultado inválidos")
        caso = obter_caso(item["caso_id"])
        if caso["id"] in ids:
            raise ValueError("Resultado duplicado para um caso")
        ids.add(caso["id"])
        if item["pedido_sha256"] != identidade(caso, execucao["versao_prompt"], item["limite_saida"]):
            raise ValueError("Resultado não corresponde ao pedido/corpus atual")
        if not isinstance(item.get("resposta"), dict) or item["resposta"].get("model") != MODELO:
            raise ValueError("Modelo do resultado divergente")
        if type(item["duracao_ms"]) is not int or item["duracao_ms"] < 0:
            raise ValueError("Duração inválida")
    return {i["caso_id"]: i for i in itens}


def modelo_revisao(execucao):
    conferir_execucao(execucao)
    return {"natureza": "revisao_humana", "execucao_sha256": resumo(execucao),
            "responsavel": "", "itens": [
                {"caso_id": i["caso_id"], "resposta_sha256": resumo(i["resposta"]),
                 "atende_pergunta": None, "preserva_regras": None, "justificativa": ""}
                for i in execucao["itens"] if obter_caso(i["caso_id"])["tarefa"] == "consulta"]}


def conferir_revisao(revisao, execucao):
    if revisao is None:
        return {}
    if not isinstance(revisao, dict):
        raise ValueError("Revisão inválida")
    if revisao.get("execucao_sha256") != resumo(execucao):
        raise ValueError("Revisão pertence a outra execução")
    if revisao.get("natureza") not in {"referencia_sintetica", "revisao_humana"}:
        raise ValueError("Natureza da revisão inválida")
    if execucao["modo"] != "sintetico" and revisao["natureza"] == "referencia_sintetica":
        raise ValueError("Rubrica sintética não pode aprovar inferência real")
    itens = {i["caso_id"]: i for i in execucao["itens"] if obter_caso(i["caso_id"])["tarefa"] == "consulta"}
    revisoes = revisao.get("itens")
    if not isinstance(revisoes, list) or len(revisoes) != len(itens):
        raise ValueError("Revisão deve cobrir todos os casos de consulta desta execução")
    resultado = {}
    for r in revisoes:
        if not isinstance(r, dict) or set(r) != {"caso_id", "resposta_sha256", "atende_pergunta", "preserva_regras", "justificativa"}:
            raise ValueError("Campos do item de revisão inválidos")
        nome = r["caso_id"]
        if nome not in itens or nome in resultado or r["resposta_sha256"] != resumo(itens[nome]["resposta"]):
            raise ValueError("Caso ou hash da revisão divergente")
        valores = [r["atende_pergunta"], r["preserva_regras"]]
        if any(v is not None and type(v) is not bool for v in valores):
            raise ValueError("Critérios da revisão devem ser booleanos ou null")
        if any(v is not None for v in valores):
            if not isinstance(revisao.get("responsavel"), str) or not revisao["responsavel"].strip():
                raise ValueError("Identifique o responsável pela revisão")
            if not isinstance(r.get("justificativa"), str) or not r["justificativa"].strip():
                raise ValueError("Justifique a revisão")
        resultado[nome] = r
    return resultado


def metrica(valores):
    return {"acertos": sum(v is True for v in valores), "total": len(valores),
            "falhas": sum(v is False for v in valores), "pendentes": sum(v is None for v in valores)}


def julgar(caso, item, revisao=None):
    resposta = item["resposta"]
    env = interpretar_resposta(resposta)
    extracao = caso["tarefa"] == "extracao"
    corpo = None
    try:
        if env["estado"] == "concluida":
            corpo = (estrutura_extracao if extracao else estrutura_consulta)(env["texto"])
    except ValueError:
        pass
    formato = corpo is not None
    a = (analisar_extracao(resposta, caso["entrada"], ["Alimentação", "Transporte", "Materiais"])
         if extracao else analisar_consulta(resposta, recuperar_caso(caso)))
    tecnico = a["estado"] != "bloqueada"
    campos, ausencias = [], []
    categoria = abstencao = fontes = fundamento = seguranca = None
    if extracao:
        for nome, esperado in caso["gabarito"].items():
            igual = formato and corpo[nome] == esperado
            campos.append(igual)
            if esperado is None:
                ausencias.append(igual)
        categoria = formato and corpo["categoria"] == caso["gabarito"]["categoria"]
        sucesso = bool(formato and tecnico and all(campos))
        if caso["critico"]:
            seguranca = sucesso
    else:
        abstencao = formato and corpo["situacao"] == caso["gabarito"]["situacao"]
        if caso["gabarito"]["situacao"] == "respondida":
            citadas = {f["trecho_id"] for af in corpo["afirmacoes"] for f in af["fontes"]} if formato else set()
            fontes = bool(tecnico and set(caso["gabarito"]["fontes_necessarias"]) <= citadas)
        if revisao is not None:
            valores = [revisao["atende_pergunta"], revisao["preserva_regras"]]
            fundamento = False if False in valores else None if None in valores else True
        automatico = bool(formato and tecnico and abstencao and fontes is not False)
        sucesso = False if not automatico or fundamento is False else None if fundamento is None else True
        if caso["critico"]:
            seguranca = sucesso
    return {"caso_id": caso["id"], "grupo": caso["grupo"], "particao": caso["particao"],
            "critico": caso["critico"], "sucesso": sucesso, "formato": formato,
            "validacao_tecnica": tecnico, "campos": campos, "categoria": categoria,
            "ausencias": ausencias, "abstencao": abstencao, "fontes": fontes,
            "fundamentacao": fundamento, "seguranca": seguranca,
            "consulta": not extracao, "estado_tecnico": a["estado"],
            "uso": env["uso"], "duracao_ms": item["duracao_ms"]}


def avaliar(execucao, revisao=None, particao="ajuste", permitir_parcial=False):
    itens = conferir_execucao(execucao)
    revisoes = conferir_revisao(revisao, execucao)
    esperados = selecionar(particao)
    ausentes = [c["id"] for c in esperados if c["id"] not in itens]
    if ausentes and not permitir_parcial:
        raise ValueError("Execução não cobre todos os casos da partição solicitada")
    linhas = [julgar(c, itens[c["id"]], revisoes.get(c["id"])) for c in esperados if c["id"] in itens]
    if not linhas:
        raise ValueError("Nenhum resultado para a partição")
    custos = [custo_de_uso(r["uso"]) for r in linhas]
    metricas = {"casos": metrica([r["sucesso"] for r in linhas]),
                "formato": metrica([r["formato"] for r in linhas]),
                "validacao_tecnica": metrica([r["validacao_tecnica"] for r in linhas]),
                "campos": metrica([v for r in linhas for v in r["campos"]]),
                "categoria": metrica([r["categoria"] for r in linhas if not r["consulta"]]),
                "ausencias": metrica([v for r in linhas for v in r["ausencias"]]),
                "abstencao": metrica([r["abstencao"] for r in linhas if r["consulta"]]),
                "fontes": metrica([r["fontes"] for r in linhas if r["fontes"] is not None]),
                "fundamentacao": metrica([r["fundamentacao"] for r in linhas if r["consulta"]]),
                "seguranca": metrica([r["seguranca"] for r in linhas if r["critico"]])}
    falhas_criticas = [r["caso_id"] for r in linhas if r["critico"] and r["sucesso"] is not True]
    return {"modo": execucao["modo"], "versao_prompt": execucao["versao_prompt"],
            "dataset_sha256": execucao["dataset_sha256"], "execucao_sha256": resumo(execucao),
            "particao": particao, "casos_ausentes": ausentes,
            "natureza_revisao": revisao["natureza"] if revisao else "pendente",
            "metricas": metricas, "falhas_criticas_ou_pendentes": falhas_criticas,
            "custo_estimado_usd": str(sum((c for c in custos if c is not None), Decimal("0"))),
            "usos_conhecidos": sum(c is not None for c in custos), "usos_ausentes": sum(c is None for c in custos),
            "mediana_ms": str(median([Decimal(r["duracao_ms"]) for r in linhas])),
            "nota_medidas": "Tokens e tempos inventados para o exercício" if execucao["modo"] == "sintetico" else "Uso do serviço e tempo local; custo é estimativa",
            "linhas": linhas}


def comparar(a, b):
    if a["modo"] != b["modo"] or a["dataset_sha256"] != b["dataset_sha256"] or a["particao"] != b["particao"]:
        raise ValueError("Não compare modos, conjuntos ou partições diferentes")
    mapa_a = {r["caso_id"]: r for r in a["linhas"]}
    mapa_b = {r["caso_id"]: r for r in b["linhas"]}
    if set(mapa_a) != set(mapa_b) or a["casos_ausentes"] or b["casos_ausentes"]:
        raise ValueError("Comparação exige a mesma cobertura completa da partição")
    regressoes = [i for i in mapa_a if mapa_a[i]["sucesso"] is True and mapa_b[i]["sucesso"] is not True]
    melhorias = [i for i in mapa_a if mapa_a[i]["sucesso"] is not True and mapa_b[i]["sucesso"] is True]
    razoes = []
    if b["particao"] != "todos":
        razoes.append("Avaliação parcial: incluir ajuste e reserva antes de decidir")
    if regressoes:
        razoes.append("Regressões: " + ", ".join(regressoes))
    if b["falhas_criticas_ou_pendentes"]:
        razoes.append("Casos críticos falhos ou pendentes: " + ", ".join(b["falhas_criticas_ou_pendentes"]))
    m = b["metricas"]["casos"]
    if m["pendentes"]:
        razoes.append("Revisões pendentes")
    if m["acertos"] * 10 < m["total"] * 9:
        razoes.append("Menos de 90% dos casos aprovados")
    return {"modo": b["modo"], "melhorias": melhorias, "regressoes": regressoes,
            "decisao": "nao_promover" if razoes else "criterios_deste_conjunto_atendidos",
            "razoes": razoes, "nota": "Comparação sintética não comprova ganho do prompt ou desempenho de um serviço real."}
