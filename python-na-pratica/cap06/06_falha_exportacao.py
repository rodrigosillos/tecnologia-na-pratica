"""Falha de arquivo deliberada depois do commit; não muda permissões do sistema."""
from pathlib import Path
import tempfile
from conexao import configuracao_banco
from configuracao import BASE_URL
from aplicacao import executar_fluxo

pasta = Path(__file__).resolve().parent
config = configuracao_banco()
with tempfile.TemporaryDirectory() as auxiliar:
    bloqueio = Path(auxiliar) / "destino"
    bloqueio.write_text("Este caminho é um arquivo, não uma pasta.", encoding="utf-8")
    codigo = executar_fluxo(
        config, pasta / "dados/quarta_despesa.json", BASE_URL + "/categorias", bloqueio
    )
raise SystemExit(codigo)
