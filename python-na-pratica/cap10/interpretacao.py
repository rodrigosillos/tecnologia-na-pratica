"""Estado de transporte e formato não comprovam a correção do texto gerado."""


def uso_normalizado(uso):
    if not isinstance(uso, dict):
        return None
    nomes = ["input_tokens", "output_tokens", "total_tokens"]
    if any(type(uso.get(n)) is not int or uso[n] < 0 for n in nomes):
        return None
    if uso["input_tokens"] + uso["output_tokens"] != uso["total_tokens"]:
        return None
    return {n: uso[n] for n in nomes}


def interpretar_resposta(resposta):
    resultado = {"estado": "resposta_invalida", "texto": None,
                 "motivo": "Envelope de resposta inválido", "uso": None}
    if not isinstance(resposta, dict):
        return resultado
    resultado["uso"] = uso_normalizado(resposta.get("usage"))
    estado = resposta.get("status")
    if estado == "incomplete":
        resultado.update(estado="incompleta", motivo="Resposta incompleta; texto parcial não foi aceito")
        return resultado
    if estado in {"queued", "in_progress", "cancelled", "failed"}:
        resultado.update(estado="nao_concluida", motivo="Serviço não entregou uma resposta concluída")
        return resultado
    if estado != "completed" or resposta.get("error") is not None:
        return resultado
    saidas = resposta.get("output")
    if not isinstance(saidas, list):
        return resultado
    textos = []
    recusou = False
    for item in saidas:
        # O capítulo não pediu ferramentas ou outros tipos de saída.
        if not isinstance(item, dict) or item.get("type") != "message":
            return resultado
        if item.get("role") != "assistant" or item.get("status") != "completed":
            return resultado
        conteudos = item.get("content")
        if not isinstance(conteudos, list):
            return resultado
        for parte in conteudos:
            if not isinstance(parte, dict):
                return resultado
            if parte.get("type") == "refusal":
                recusou = True
            elif parte.get("type") == "output_text" and isinstance(parte.get("text"), str):
                textos.append(parte["text"])
            else:
                return resultado
    if recusou:
        resultado.update(estado="recusada", motivo="O modelo recusou a solicitação; nenhuma sugestão foi aceita")
        return resultado
    texto = "\n".join(textos).strip()
    if not texto:
        resultado.update(estado="sem_texto", motivo="Resposta concluída sem texto utilizável")
        return resultado
    if resultado["uso"] is None:
        resultado.update(estado="uso_ausente", motivo="Texto recebido, mas uso ausente ou inválido; confira a resposta")
        return resultado
    resultado.update(estado="concluida", texto=texto, motivo="Texto disponível para revisão; conteúdo ainda não validado")
    return resultado
