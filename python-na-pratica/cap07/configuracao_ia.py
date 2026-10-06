"""Escolhas fixadas para esta revisão; nenhuma chave é gravada em arquivo."""
import os
from pathlib import Path

PASTA = Path(__file__).resolve().parent
MODELO = "gpt-4.1-mini-2025-04-14"
SDK = "3.24.0"
VERSAO_PROMPT = "cap07-r01"
BASE_URL = "https://api.openai.com/v1"
MAX_CARACTERES = 3000


def limite_saida():
    try:
        valor = int(os.environ.get("PYTHON_PRATICA_IA_MAX_SAIDA", "256"))
    except ValueError:
        raise ValueError("Limite de saída deve ser inteiro entre 32 e 512") from None
    if not 32 <= valor <= 512:
        raise ValueError("Limite de saída deve ser inteiro entre 32 e 512")
    return valor


def obter_chave():
    chave = os.environ.get("OPENAI_API_KEY", "")
    if not chave or not chave.strip():
        raise ValueError("OPENAI_API_KEY não configurada nesta sessão")
    if chave != chave.strip() or any(c.isspace() for c in chave):
        raise ValueError("A chave contém espaços ou quebras de linha; confira a configuração")
    return chave
