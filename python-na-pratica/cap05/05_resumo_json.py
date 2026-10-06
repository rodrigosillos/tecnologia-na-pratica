from pathlib import Path
from aplicacao import executar
from configuracao import BASE_URL

pasta = Path(__file__).resolve().parent
raise SystemExit(executar(pasta / "dados" / "validas.json", BASE_URL + "/categorias"))
