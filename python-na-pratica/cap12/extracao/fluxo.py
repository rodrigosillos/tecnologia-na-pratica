"""Sugestão, revisão explícita e lote compatível com o capítulo 6; sem banco."""
from copy import deepcopy
from decimal import Decimal
from .configuracao_ia import PASTA, MODELO, VERSAO_PROMPT
from .arquivos import ler_json, resumo, serializar
from .contexto import origens, categorias, preparar_pedido
from .validacao import analisar, conferir_campos, CAMPOS
from .contrato_ia import validar_estrutura
from regras import texto_obrigatorio, validar_lote


def montar_pacote(itens, modo):
    return {"versao": 1, "modo": modo,
            "origem": "sintetica" if modo == "reproducao" else "execucao_sdk",
            "modelo": MODELO, "versao_prompt": VERSAO_PROMPT, "itens": itens}


def preparar_reproducao():
    itens = []
    for nome, origem in origens().items():
        caso = ler_json(PASTA / "casos" / (nome + ".json"))
        if (caso.get("origem") != "sintetica" or caso.get("origem_id") != nome
                or caso.get("pedido_sha256") != resumo(preparar_pedido(origem))):
            raise ValueError("Caso sintético não corresponde ao pedido: " + nome)
        itens.append({"origem_id": nome, "pedido_sha256": caso["pedido_sha256"],
                      "resposta": caso["resposta"]})
    return montar_pacote(itens, "reproducao")


def conferir_pacote(pacote):
    campos = {"versao", "modo", "origem", "modelo", "versao_prompt", "itens"}
    if not isinstance(pacote, dict) or set(pacote) != campos:
        raise ValueError("Pacote: campos inválidos")
    if type(pacote["versao"]) is not int or pacote["versao"] != 1:
        raise ValueError("Pacote: versão inválida")
    if not isinstance(pacote["modo"], str) or pacote["modo"] not in {"reproducao", "api_real"}:
        raise ValueError("Pacote: modo inválido")
    esperado = "sintetica" if pacote["modo"] == "reproducao" else "execucao_sdk"
    if pacote["origem"] != esperado or pacote["modelo"] != MODELO or pacote["versao_prompt"] != VERSAO_PROMPT:
        raise ValueError("Pacote: origem, modelo ou prompt divergente")
    if not isinstance(pacote["itens"], list) or not 1 <= len(pacote["itens"]) <= 3:
        raise ValueError("Pacote: espere de um a três itens")
    conhecidas = origens()
    vistos, analises = set(), {}
    for item in pacote["itens"]:
        if not isinstance(item, dict) or set(item) != {"origem_id", "pedido_sha256", "resposta"}:
            raise ValueError("Pacote: item inválido")
        nome = item["origem_id"]
        if not isinstance(nome, str) or nome not in conhecidas or nome in vistos:
            raise ValueError("Pacote: origem desconhecida ou repetida")
        vistos.add(nome)
        fonte = conhecidas[nome]
        if item["pedido_sha256"] != resumo(preparar_pedido(fonte)):
            raise ValueError("Pacote: contexto alterado em " + nome)
        if pacote["modo"] == "api_real":
            resposta = item["resposta"]
            if (not isinstance(resposta, dict) or resposta.get("model") != MODELO
                    or not isinstance(resposta.get("id"), str)
                    or not resposta["id"].startswith("resp_") or "sintetica" in resposta["id"]):
                raise ValueError("Pacote real: resposta sem identificação compatível")
        analises[nome] = analisar(item["resposta"], fonte["texto"], categorias())
    return analises


def modelo_revisao(pacote):
    conferir_pacote(pacote)
    return {"versao": 1, "pacote_sha256": resumo(pacote), "revisor": "",
            "decisoes": [{"origem_id": i["origem_id"], "acao": "pendente",
                           "motivo": "", "correcoes": {}, "complemento": None}
                          for i in pacote["itens"]]}


def revisar(pacote, revisao):
    analises = conferir_pacote(pacote)
    if not isinstance(revisao, dict) or set(revisao) != {"versao", "pacote_sha256", "revisor", "decisoes"}:
        raise ValueError("Revisão: campos inválidos")
    if type(revisao["versao"]) is not int or revisao["versao"] != 1:
        raise ValueError("Revisão: versão inválida")
    if revisao["pacote_sha256"] != resumo(pacote):
        raise ValueError("Revisão pertence a outro pacote; conferir novamente")
    revisor = texto_obrigatorio(revisao["revisor"], "revisor", 80)
    decisoes = revisao["decisoes"]
    if not isinstance(decisoes, list) or len(decisoes) != len(analises):
        raise ValueError("Revisão: uma decisão por origem é obrigatória")
    fontes = origens()
    complementos = ler_json(PASTA / "entradas/complementos.json")
    vistos, registros, trilha = set(), [], []
    for decisao in decisoes:
        if not isinstance(decisao, dict) or set(decisao) != {"origem_id", "acao", "motivo", "correcoes", "complemento"}:
            raise ValueError("Decisão com campos inválidos")
        nome = decisao["origem_id"]
        if not isinstance(nome, str) or nome not in analises or nome in vistos:
            raise ValueError("Revisão: origem desconhecida ou repetida")
        vistos.add(nome)
        acao = decisao["acao"]
        if not isinstance(acao, str) or acao not in {"aceitar", "corrigir", "rejeitar"}:
            raise ValueError("Revisão ainda pendente ou ação inválida: " + nome)
        motivo = texto_obrigatorio(decisao["motivo"], "motivo", 300)
        correcoes = decisao["correcoes"]
        if not isinstance(correcoes, dict) or not set(correcoes).issubset(CAMPOS):
            raise ValueError("Correções: campos não permitidos")
        complemento = decisao["complemento"]
        if complemento is not None and not isinstance(complemento, str):
            raise ValueError("Complemento: identificador inválido")
        if acao != "corrigir" and (correcoes or complemento is not None):
            raise ValueError("Aceitar ou rejeitar não permite alterações ocultas")
        item_trilha = {"origem_id": nome, "id_destino": fontes[nome]["id_destino"],
                       "acao": acao, "motivo": motivo, "revisor": revisor,
                       "original": analises[nome]["sugestao"], "final": None,
                       "correcoes": correcoes, "complemento": None}
        if acao == "rejeitar":
            trilha.append(item_trilha)
            continue
        if analises[nome]["estado"] == "bloqueada":
            raise ValueError(nome + ": sugestão bloqueada; rejeite ou produza outra sugestão")
        atual = deepcopy(analises[nome]["sugestao"])
        texto = fontes[nome]["texto"]
        if acao == "corrigir":
            if not correcoes:
                raise ValueError("Corrigir exige pelo menos um campo")
            if complemento is not None:
                extra = complementos.get(complemento)
                if not isinstance(extra, dict) or extra.get("origem_id") != nome:
                    raise ValueError("Complemento não corresponde à origem")
                texto += "\n" + extra["texto"]
                item_trilha["complemento"] = {"id": complemento, "texto": extra["texto"], "sha256": resumo(extra)}
            for campo, mudanca in correcoes.items():
                if not isinstance(mudanca, dict) or set(mudanca) != {"valor", "trecho"}:
                    raise ValueError("Correção exige valor e trecho")
                if atual[campo] == mudanca["valor"] and atual["evidencias"][campo] == mudanca["trecho"]:
                    raise ValueError("Correção sem alteração: " + campo)
                atual[campo] = mudanca["valor"]
                atual["evidencias"][campo] = mudanca["trecho"]
            atual = validar_estrutura(serializar(atual))
        conf = conferir_campos(atual, texto, categorias())
        if conf["erros"] or conf["pendencias"]:
            raise ValueError(nome + ": revisão não resolveu todos os campos: " +
                             "; ".join(conf["erros"] + conf["pendencias"]))
        registro = {"id": fontes[nome]["id_destino"], **{c: atual[c] for c in CAMPOS}}
        registros.append(registro)
        item_trilha["final"] = atual
        trilha.append(item_trilha)
    lote = validar_lote(registros, categorias())
    if lote["erros"]:
        raise ValueError("Lote revisado inválido: " + "; ".join(lote["erros"]))
    total = sum((d["valor"] for d in lote["despesas"]), Decimal("0.00"))
    auditoria = {"versao": 1, "modo": pacote["modo"], "origem": pacote["origem"],
                 "pacote_sha256": resumo(pacote), "revisao_sha256": resumo(revisao),
                 "registros": len(registros), "rejeitados": len(trilha) - len(registros),
                 "total_lote_revisado": str(total), "persistencia": "nao_executada",
                 "aviso": "Revisão de dados didáticos; não é aprovação financeira nem prova de autoria",
                 "decisoes": trilha}
    return registros, auditoria
