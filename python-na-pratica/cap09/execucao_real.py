"""Extensão opcional: uma consulta, no máximo uma tentativa ao SDK."""
from datetime import datetime, timezone
import importlib.metadata
from pathlib import Path
import platform
import time
from openai import OpenAIError
from configuracao_ia import obter_chave, SDK, MODELO, VERSAO_PROMPT
from arquivos import gravar_conjunto
from documentos import carregar_corpus
from busca import recuperar
from contexto import preparar_pedido, identidade_pedido
from cliente_ia import criar_cliente, chamar_modelo, diagnosticar_erro
from fluxo import montar_pacote, conferir_pacote, apresentar


def executar_real(pergunta, destino, confirmado=False, fabrica_cliente=criar_cliente):
    if not confirmado:
        print("API real desativada; nenhuma chamada. Use --confirmar-envio para habilitar.")
        return 2
    try:
        if Path(destino).exists():
            raise ValueError("Destino já existe; nenhuma chamada será iniciada")
        r = recuperar(pergunta, carregar_corpus())
        pedido = preparar_pedido(r) if not r["sem_trechos"] else None
        chave = obter_chave() if pedido is not None else None
        if importlib.metadata.version("openai") != SDK:
            raise ValueError("SDK diferente do fixado")
    except (ValueError, OSError) as erro:
        print("Configuração:", erro)
        return 1
    registro = {"modo": "api_real", "data_utc": datetime.now(timezone.utc).isoformat(),
                "sistema": platform.system(), "python": platform.python_version(),
                "sdk_openai": SDK, "modelo_solicitado": MODELO, "prompt_versao": VERSAO_PROMPT,
                "pedido_sha256": identidade_pedido(r), "tentativas_sdk": 0,
                "max_retries": 0, "revisao_semantica": "pendente", "banco": "nao_utilizado"}
    inicio = time.perf_counter()
    saidas = {"recuperacao.json": r}
    try:
        resposta = None
        if pedido is not None:
            with fabrica_cliente(chave) as cliente:
                registro["tentativas_sdk"] = 1
                resposta = chamar_modelo(cliente, pedido)
            if resposta.get("model") != MODELO or resposta.get("error") is not None:
                raise ValueError("Resposta incompatível com esta revisão")
            resposta = {k: resposta.get(k) for k in ("id", "object", "created_at", "model", "status", "output", "usage", "incomplete_details")}
        pacote = montar_pacote(r, resposta, "api_real")
        analise = conferir_pacote(pacote)
        saidas.update({"pacote.json": pacote, "analise.json": analise})
        registro.update(status="sem_chamada" if pedido is None else "resposta_recebida", uso=analise["uso"])
        apresentar(pacote, analise)
        print("Tentativas ao SDK:", registro["tentativas_sdk"])
        codigo = 2 if analise["estado"] == "bloqueada" else 0
    except (OpenAIError, ValueError, TypeError, AttributeError) as erro:
        registro.update(status="falha", diagnostico=diagnosticar_erro(erro))
        print(registro["diagnostico"])
        codigo = 1
    registro["duracao_segundos"] = round(time.perf_counter() - inicio, 3)
    saidas["metadados.json"] = registro
    try:
        gravar_conjunto(destino, saidas)
    except (OSError, ValueError):
        print("Registro não salvo. Tentativas ao SDK:", registro["tentativas_sdk"], "— não reenviar automaticamente.")
        return 3
    return codigo
