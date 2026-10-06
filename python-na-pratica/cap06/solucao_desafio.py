"""D002 volta a 35.00, após conferência da origem; D005 pode ser aceita."""
from pathlib import Path
from conexao import configuracao_banco
from configuracao import BASE_URL
from aplicacao import executar_importacao

pasta = Path(__file__).resolve().parent
raise SystemExit(executar_importacao(
    configuracao_banco(), pasta / "dados/solucao_desafio.json", BASE_URL + "/categorias"
))
