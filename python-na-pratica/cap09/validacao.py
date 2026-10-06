"""Valida referência e literalidade, sem alegar prova de implicação semântica."""
from interpretacao import interpretar_resposta
from contrato_ia import validar_estrutura

ABSTENCAO = "Não há suporte suficiente nos trechos recuperados para responder. Confira a busca e o documento completo."


def analisar(resposta, recuperacao):
    envelope = interpretar_resposta(resposta)
    base = {"estado": "bloqueada", "motivo": envelope["motivo"],
            "uso": envelope["uso"], "resposta": None, "revisao_semantica": "pendente"}
    if envelope["estado"] != "concluida":
        return base
    try:
        corpo = validar_estrutura(envelope["texto"])
        afirmacoes = corpo["afirmacoes"]
        if corpo["situacao"] == "sem_cobertura":
            if afirmacoes:
                raise ValueError("Abstenção não pode conter afirmações")
            return {**base, "estado": "abstencao_proposta", "motivo": ABSTENCAO, "resposta": corpo}
        if not 1 <= len(afirmacoes) <= 4:
            raise ValueError("Resposta deve ter entre uma e quatro afirmações")
        fontes = {t["id"]: t for t in recuperacao["trechos"]}
        for afirmacao in afirmacoes:
            if not afirmacao["texto"].strip() or len(afirmacao["texto"]) > 600:
                raise ValueError("Afirmação vazia ou longa demais")
            if not 1 <= len(afirmacao["fontes"]) <= 3:
                raise ValueError("Cada afirmação deve citar entre uma e três fontes")
            usados = set()
            for fonte in afirmacao["fontes"]:
                nome, citacao = fonte["trecho_id"], fonte["citacao"]
                if nome in usados or nome not in fontes:
                    raise ValueError("Fonte repetida ou não recuperada")
                usados.add(nome)
                if not citacao.strip() or len(citacao) > 700 or citacao not in fontes[nome]["texto"]:
                    raise ValueError("Citação vazia, longa demais ou ausente do trecho")
        return {**base, "estado": "aguarda_revisao", "motivo": "Referências conferidas; significado ainda precisa ser revisado", "resposta": corpo}
    except ValueError as erro:
        return {**base, "motivo": str(erro)}
