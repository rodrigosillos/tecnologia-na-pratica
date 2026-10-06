from pathlib import Path
from conexao import configuracao_banco
from configuracao import BASE_URL
from aplicacao import executar_importacao

pasta = Path(__file__).resolve().parent
config = configuracao_banco()
raise SystemExit(executar_importacao(
    config, pasta / "dados/validas.json", BASE_URL + "/categorias"
))
