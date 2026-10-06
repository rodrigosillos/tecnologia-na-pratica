"""Busca lexical pequena e explicável; pontuação não é probabilidade."""
import re
import unicodedata

IGNORADAS = set("a o as os um uma de da do das dos e em no na nos nas por para com sem qual quais que quanto como posso pode ao aos se ser meu minha uma é".split())


def termos(texto):
    decomposto = unicodedata.normalize("NFD", texto.casefold())
    simples = "".join(c for c in decomposto if not unicodedata.combining(c))
    return {t for t in re.findall(r"[a-z0-9]+", simples) if len(t) > 1 and t not in IGNORADAS}


def pontuar(pergunta, trecho):
    consulta = termos(pergunta)
    no_titulo = consulta & termos(trecho["secao"])
    no_corpo = consulta & termos(trecho["texto"])
    return 3 * len(no_titulo) + len(no_corpo)


def recuperar(pergunta, corpus, top_k=3, minimo=2, max_caracteres=6000):
    if not isinstance(pergunta, str) or not pergunta.strip() or len(pergunta) > 500:
        raise ValueError("Pergunta vazia ou acima de 500 caracteres")
    if type(top_k) is not int or not 1 <= top_k <= 5:
        raise ValueError("top_k deve ser inteiro entre 1 e 5")
    if type(minimo) is not int or minimo < 1:
        raise ValueError("Pontuação mínima deve ser inteira e positiva")
    if type(max_caracteres) is not int or not 1 <= max_caracteres <= 6000:
        raise ValueError("Limite de contexto deve estar entre 1 e 6.000 caracteres")
    candidatos = [{**t, "pontos": pontuar(pergunta, t)} for t in corpus["trechos"]]
    candidatos = sorted((t for t in candidatos if t["pontos"] >= minimo),
                        key=lambda t: (-t["pontos"], t["id"]))
    selecionados, usados = [], 0
    for trecho in candidatos:
        if len(selecionados) == top_k:
            break
        tamanho = len(trecho["texto"])
        if usados + tamanho > max_caracteres:
            continue  # Mantém seções inteiras; não corta uma regra pela metade.
        selecionados.append(trecho)
        usados += tamanho
    return {"pergunta": pergunta.strip(), "corpus_versao": corpus["versao"],
            "corpus_sha256": corpus["sha256"], "algoritmo": "lexical-titulo3-corpo1-r01",
            "parametros": {"top_k": top_k, "minimo": minimo, "max_caracteres": max_caracteres},
            "caracteres_trechos": usados, "trechos": selecionados,
            "sem_trechos": not selecionados}
