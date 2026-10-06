"""Vínculo determinístico; não é assinatura nem prova de autoria da revisão."""
from extracao.arquivos import resumo


def conferir_vinculo(proveniencia, entrada_hash):
    if not isinstance(proveniencia, dict):
        raise ValueError("Proveniência inválida")
    tipo = proveniencia.get("tipo")
    if tipo == "estruturada":
        if set(proveniencia) != {"tipo", "entrada_sha256"} or proveniencia["entrada_sha256"] != entrada_hash:
            raise ValueError("Vínculo da entrada estruturada divergente")
    elif tipo == "revisada":
        if set(proveniencia) != {"tipo", "pacote", "revisao", "trilha"}:
            raise ValueError("Proveniência revisada incompleta")
        pacote, revisao, trilha = (proveniencia[k] for k in ("pacote", "revisao", "trilha"))
        if not all(isinstance(x, dict) for x in (pacote, revisao, trilha)):
            raise ValueError("Revisão arquivada inválida")
        if (entrada_hash != resumo({"pacote": pacote, "revisao": revisao})
                or revisao.get("pacote_sha256") != resumo(pacote)
                or trilha.get("pacote_sha256") != resumo(pacote)
                or trilha.get("revisao_sha256") != resumo(revisao)):
            raise ValueError("Hashes da revisão divergentes")
    else:
        raise ValueError("Tipo de proveniência desconhecido")
