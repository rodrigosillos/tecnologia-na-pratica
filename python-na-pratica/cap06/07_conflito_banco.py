from pathlib import Path
from conexao import configuracao_banco
from configuracao import BASE_URL
from aplicacao import executar_importacao

pasta = Path(__file__).resolve().parent
raise SystemExit(executar_importacao(
    configuracao_banco(), pasta / "dados/conflito_banco.json", BASE_URL + "/categorias"
))
