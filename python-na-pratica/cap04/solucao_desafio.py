from pathlib import Path

from aplicacao import executar

caminho = Path(__file__).resolve().parent / "dados" / "desafio.json"
raise SystemExit(executar(caminho))
