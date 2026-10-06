"""Configuração do capítulo 10; sem chamada ao importar."""
import os
from pathlib import Path

PASTA = Path(__file__).resolve().parent
MODELO = "gpt-4.1-mini-2025-04-14"
SDK = "3.24.0"
BASE_URL = "https://api.openai.com/v1"
LIMITE_SAIDA = 768


def obter_chave():
    chave = os.environ.get("OPENAI_API_KEY", "")
    if not chave or chave != chave.strip() or any(c.isspace() for c in chave):
        raise ValueError("OPENAI_API_KEY ausente ou inválida nesta sessão")
    return chave
