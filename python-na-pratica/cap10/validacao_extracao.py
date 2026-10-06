"""Validações de domínio e vínculo literal; a relação semântica exige revisão."""
from datetime import datetime
from re import fullmatch
from contrato_extracao import validar_estrutura
from interpretacao import interpretar_resposta
from regras import converter_data, converter_valor, texto_obrigatorio

CAMPOS = ("data", "valor", "descricao", "categoria")


def conferir_campos(sugestao, texto, categorias):
    erros, pendencias = [], []
    for campo in CAMPOS:
        valor = sugestao[campo]
        trecho = sugestao["evidencias"][campo]
        if valor is None:
            pendencias.append(campo)
            if trecho is not None:
                erros.append(campo + ": valor ausente exige evidência null")
            continue
        if not isinstance(trecho, str) or not trecho.strip() or trecho not in texto:
            erros.append(campo + ": evidência não encontrada na fonte")
            continue
        try:
            if campo == "data":
                dia = converter_data(valor)
                if fullmatch(r"[0-9]{2}/[0-9]{2}/[0-9]{4}", trecho):
                    original = datetime.strptime(trecho, "%d/%m/%Y").date()
                else:
                    original = converter_data(trecho)
                if dia != original:
                    raise ValueError("data: não corresponde à evidência")
            elif campo == "valor":
                quantia = converter_valor(valor)
                achado = fullmatch(r"R\$ ?([0-9]{1,7},[0-9]{2})", trecho)
                if not achado or converter_valor(achado.group(1).replace(",", ".")) != quantia:
                    raise ValueError("valor: não corresponde à evidência monetária")
            elif campo == "descricao":
                texto_obrigatorio(valor, campo, 120)
                if valor != trecho:
                    raise ValueError("descricao: neste capítulo, use o trecho literal")
            elif valor not in categorias:
                raise ValueError("categoria: fora do catálogo")
        except ValueError as erro:
            erros.append(str(erro))
    return {"erros": erros, "pendencias": pendencias}


def analisar(resposta, texto, categorias):
    envelope = interpretar_resposta(resposta)
    if envelope["estado"] != "concluida":
        return {"estado": "bloqueada", "erros": [envelope["motivo"]],
                "pendencias": [], "sugestao": None, "uso": envelope["uso"]}
    try:
        sugestao = validar_estrutura(envelope["texto"])
    except ValueError as erro:
        return {"estado": "bloqueada", "erros": [str(erro)],
                "pendencias": [], "sugestao": None, "uso": envelope["uso"]}
    conf = conferir_campos(sugestao, texto, categorias)
    return {"estado": "bloqueada" if conf["erros"] else "aguarda_revisao",
            **conf, "sugestao": sugestao, "uso": envelope["uso"]}
