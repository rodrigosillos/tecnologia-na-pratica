"""Modo real explícito, registro local UTF-8 e nenhuma escrita no banco."""
from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import time
from uuid import uuid4
from openai import OpenAIError

from configuracao_ia import PASTA, MODELO, VERSAO_PROMPT, obter_chave
from contexto import pedido_exemplo, sha256_texto
from cliente_ia import criar_cliente, chamar_modelo, diagnosticar_erro
from interpretacao import interpretar_resposta
from reproducao import apresentar


def salvar_registro(registro, destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    nome = "chamada-real-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:8] + ".json"
    caminho = destino / nome
    with caminho.open("x", encoding="utf-8") as arquivo:
        json.dump(registro, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")
    return caminho


def executar_real(confirmado=False, destino=None, fabrica_cliente=criar_cliente):
    if not confirmado:
        print("API real desativada. Use --confirmar-envio para autorizar uma chamada com possível cobrança.")
        return 2
    try:
        pedido = pedido_exemplo()
        chave = obter_chave()
    except (ValueError, OSError, UnicodeError) as erro:
        print("Configuração:", str(erro))
        return 1
    registro = {
        "modo": "api_real", "origem": "execucao_sdk", "capitulo": 7, "revisao": "R01",
        "data_utc": datetime.now(timezone.utc).isoformat(), "sistema": platform.system(),
        "python": platform.python_version(), "sdk_openai": importlib.metadata.version("openai"),
        "modelo_solicitado": MODELO, "versao_prompt": VERSAO_PROMPT,
        "input_sha256": sha256_texto(pedido["input"]),
        "instructions_sha256": sha256_texto(pedido["instructions"]),
        "pedido": pedido, "tentativas_sdk": 0, "max_retries": 0,
        "revisao_do_conteudo": "pendente", "resposta": None,
    }
    inicio = time.perf_counter()
    try:
        with fabrica_cliente(chave) as cliente:
            registro["tentativas_sdk"] = 1
            resposta = chamar_modelo(cliente, pedido)
        # Somente campos necessários à conferência; não registra cabeçalhos.
        registro["resposta"] = {k: resposta.get(k) for k in (
            "id", "object", "created_at", "model", "status", "output", "usage", "incomplete_details")}
        # A interpretação também considera error, sem persistir o corpo desse erro.
        resultado = interpretar_resposta(resposta)
        registro["resultado"] = resultado
        registro["status"] = "resposta_recebida" if resultado["estado"] == "concluida" else "pendente_resposta"
        print("Modo: API real | uma tentativa ao SDK | sem repetição automática")
        apresentar(resultado)
        codigo = 0 if resultado["estado"] == "concluida" else 2
    except (OpenAIError, ValueError, TypeError, AttributeError) as erro:
        registro["status"] = "falha_api"
        registro["diagnostico"] = diagnosticar_erro(erro)
        print(registro["diagnostico"])
        codigo = 1
    registro["duracao_segundos"] = round(time.perf_counter() - inicio, 3)
    try:
        caminho = salvar_registro(registro, destino or PASTA / "gerados")
    except (OSError, ValueError):
        print("Registro não salvo. A tentativa já ocorreu; não reenvie automaticamente para recuperar um arquivo.")
        return 3
    print("Registro:", caminho)
    return codigo
