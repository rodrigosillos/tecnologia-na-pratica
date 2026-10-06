"""Primeiro consulte a lista; ainda é preciso validar cada despesa do lote."""
from pathlib import Path
from aplicacao import executar
from configuracao import BASE_URL

pasta = Path(__file__).resolve().parent
raise SystemExit(executar(pasta / "dados" / "desafio.json", BASE_URL + "/categorias"))
