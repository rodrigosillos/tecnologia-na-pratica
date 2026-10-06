"""Configuração explícita; importar não executa chamadas."""
import os
from pathlib import Path

PASTA = Path(__file__).resolve().parent
MODELO = "gpt-4.1-mini-2025-04-14"
SDK = "3.24.0"
BASE_URL = "https://api.openai.com/v1"
VERSAO_PROMPT = "cap09-r01"


def limite_saida():
    try:
        valor = int(os.environ.get("PYTHON_PRATICA_IA_MAX_SAIDA", "768"))
    except ValueError:
        raise ValueError("Limite de saída deve ser inteiro entre 32 e 1024") from None
    if not 32 <= valor <= 1024:
        raise ValueError("Limite de saída deve ser inteiro entre 32 e 1024")
    return valor


def obter_chave():
    chave = os.environ.get("OPENAI_API_KEY", "")
    if not chave:
        raise ValueError("OPENAI_API_KEY não configurada nesta sessão")
    if chave != chave.strip() or any(c.isspace() for c in chave):
        raise ValueError("Chave com espaços; confira a configuração")
    return chave
