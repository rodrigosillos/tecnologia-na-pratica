from pathlib import Path
from conexao import configuracao_banco
from aplicacao import executar_exportacao

pasta = Path(__file__).resolve().parent
raise SystemExit(executar_exportacao(configuracao_banco(), pasta / "gerados"))
