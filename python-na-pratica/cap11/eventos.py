"""Eventos permitidos, sem conteúdo de entrada, senha, DSN ou erro bruto."""
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from uuid import uuid4


class ArquivoObrigatorio(logging.FileHandler):
    def handleError(self, record):
        raise OSError("Arquivo de log indisponível")


def abrir_log(pasta, execucao, comando):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    tentativa_id = uuid4().hex
    caminho = pasta / (tentativa_id + ".jsonl")
    logger = logging.getLogger("cap11." + tentativa_id)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = ArquivoObrigatorio(caminho, mode="x", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    def registrar(evento, **campos):
        permitidos = {"tentativa", "segundos", "novas", "existentes", "quantidade", "total", "estado", "sqlstate"}
        if not set(campos) <= permitidos:
            raise ValueError("Campo de log não permitido")
        registro = {"data_utc": datetime.now(timezone.utc).isoformat(),
                    "tentativa_id": tentativa_id, "execucao": execucao,
                    "comando": comando, "evento": evento, **campos}
        logger.info(json.dumps(registro, ensure_ascii=False, allow_nan=False))

    def fechar():
        logger.removeHandler(handler)
        handler.close()

    return registrar, fechar, caminho
