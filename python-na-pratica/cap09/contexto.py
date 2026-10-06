"""Monta apenas o contexto selecionado; não lê arquivos citados pelo modelo."""
from arquivos import serializar, resumo
from configuracao_ia import PASTA, MODELO, VERSAO_PROMPT, limite_saida
from contrato_ia import formato_resposta


def preparar_pedido(recuperacao):
    if recuperacao["sem_trechos"]:
        raise ValueError("Sem trechos recuperados: não iniciar chamada")
    contexto = {"pergunta": recuperacao["pergunta"],
                "corpus_versao": recuperacao["corpus_versao"],
                "trechos": [{k: t[k] for k in ("id", "documento", "secao", "texto")}
                            for t in recuperacao["trechos"]]}
    return {"model": MODELO,
            "instructions": (PASTA / "prompts/consulta.md").read_text(encoding="utf-8"),
            "input": [{"role": "user", "content": serializar(contexto)}],
            "text": {"format": formato_resposta()},
            "max_output_tokens": limite_saida(), "store": False, "truncation": "disabled"}


def identidade_pedido(recuperacao):
    if recuperacao["sem_trechos"]:
        return resumo({"recuperacao": recuperacao, "sem_chamada": True})
    return resumo({"prompt_versao": VERSAO_PROMPT, "pedido": preparar_pedido(recuperacao)})
