from pathlib import Path

from aplicacao import executar

caminho = Path(__file__).resolve().parent / "dados" / "invalidas.csv"
raise SystemExit(executar(caminho))
