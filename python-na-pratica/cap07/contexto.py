"""Monta apenas a tarefa e o texto sintético escolhidos para esta chamada."""
import hashlib
from configuracao_ia import PASTA, MODELO, MAX_CARACTERES, limite_saida


def sha256_texto(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def preparar_pedido(texto):
    if not isinstance(texto, str) or not texto.strip():
        raise ValueError("Entrada de IA deve conter texto")
    if len(texto) > MAX_CARACTERES:
        raise ValueError("Entrada excede 3000 caracteres; reduza o trecho escolhido")
    instrucoes = (PASTA / "prompts/orientacao.md").read_text(encoding="utf-8")
    if not instrucoes.strip() or len(instrucoes) > 3000:
        raise ValueError("Arquivo de instruções vazio ou fora do limite desta revisão")
    entrada = "Texto sintético de uma despesa, para leitura e conferência:\n" + texto
    return {
        "model": MODELO,
        "instructions": instrucoes,
        "input": entrada,
        "max_output_tokens": limite_saida(),
        "store": False,
        "truncation": "disabled",
        "tools": [],
    }


def pedido_exemplo():
    return preparar_pedido((PASTA / "entradas/descricao.md").read_text(encoding="utf-8"))
