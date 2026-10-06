"""Reprodução sintética e conferência vinculadas ao corpus e à pergunta."""
from arquivos import ler_json, resumo
from configuracao_ia import PASTA, MODELO
from documentos import carregar_corpus
from busca import recuperar
from contexto import identidade_pedido
from validacao import analisar, ABSTENCAO


def perguntas():
    return ler_json(PASTA / "casos/perguntas.json")


def obter_pergunta(nome):
    itens = [p for p in perguntas() if p["id"] == nome]
    if len(itens) != 1:
        raise ValueError("Caso de pergunta desconhecido")
    return itens[0]["pergunta"]


def montar_pacote(recuperacao, resposta, modo):
    if modo not in {"reproducao_sintetica", "api_real"}:
        raise ValueError("Modo desconhecido")
    pacote = {"formato": "cap09-r01", "modo": modo,
              "recuperacao": recuperacao, "pedido_sha256": identidade_pedido(recuperacao),
              "resposta": resposta}
    return {**pacote, "pacote_sha256": resumo(pacote)}


def conferir_pacote(pacote):
    chaves = {"formato", "modo", "recuperacao", "pedido_sha256", "resposta", "pacote_sha256"}
    if not isinstance(pacote, dict) or set(pacote) != chaves or pacote["formato"] != "cap09-r01":
        raise ValueError("Pacote inválido")
    if pacote["modo"] not in {"reproducao_sintetica", "api_real"}:
        raise ValueError("Modo desconhecido")
    if resumo({k: v for k, v in pacote.items() if k != "pacote_sha256"}) != pacote["pacote_sha256"]:
        raise ValueError("Pacote alterado desde a geração")
    r = pacote["recuperacao"]
    if not isinstance(r, dict) or not isinstance(r.get("parametros"), dict):
        raise ValueError("Recuperação inválida")
    try:
        atual = recuperar(r["pergunta"], carregar_corpus(), **r["parametros"])
    except (KeyError, TypeError):
        raise ValueError("Parâmetros de recuperação inválidos") from None
    if atual != r or identidade_pedido(r) != pacote["pedido_sha256"]:
        raise ValueError("Corpus, recuperação ou configuração diferentes da execução arquivada")
    if r["sem_trechos"]:
        if pacote["resposta"] is not None:
            raise ValueError("Uma busca sem trechos não deve conter resposta de modelo")
        return {"estado": "abstencao_local", "motivo": ABSTENCAO,
                "resposta": None, "uso": None, "revisao_semantica": "conferir_recuperacao"}
    if not isinstance(pacote["resposta"], dict) or pacote["resposta"].get("model") != MODELO:
        raise ValueError("Resposta com modelo diferente do fixado")
    return analisar(pacote["resposta"], r)


def preparar_reproducao(nome):
    pergunta = obter_pergunta(nome)
    r = recuperar(pergunta, carregar_corpus())
    fixture = ler_json(PASTA / "casos" / (nome + ".json"))
    if (fixture.get("natureza") != "sintetica_nao_inferencia"
            or fixture.get("recuperacao_sha256") != resumo(r)
            or fixture.get("pedido_sha256") != identidade_pedido(r)):
        raise ValueError("Caso sintético não corresponde à pergunta, ao corpus ou à configuração")
    pacote = montar_pacote(r, fixture["resposta"], "reproducao_sintetica")
    conferir_pacote(pacote)
    return pacote


def apresentar(pacote, analise):
    print("Modo:", pacote["modo"])
    print("Pergunta:", pacote["recuperacao"]["pergunta"])
    print("Estado:", analise["estado"])
    print(analise["motivo"])
    corpo = analise["resposta"]
    if corpo is not None:
        for i, a in enumerate(corpo["afirmacoes"], 1):
            print(f"{i}. {a['texto']}")
            for f in a["fontes"]:
                print(f"   [{f['trecho_id']}] {f['citacao']}")
    print("Revisão semântica:", analise["revisao_semantica"])
    print("Aprovação de despesas: não executada | Banco: não utilizado")
