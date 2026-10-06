"""Uma amostra opcional; não executa automaticamente o conjunto de vinte casos."""
from datetime import datetime, timezone
import importlib.metadata
from pathlib import Path
import platform
import time
from openai import OpenAIError
from arquivos import resumo, serializar, gravar_conjunto
from configuracao_ia import MODELO, SDK, obter_chave
from conjunto import carregar, obter_caso, preparar_pedido, identidade
from custos import novo_controle, reservar, concluir, retrato, tarifas
from cliente_ia import criar_cliente, chamar_modelo, diagnosticar_erro
from avaliacao import modelo_revisao


def executar_real(nome, destino, confirmado=False, versao="B", orcamento_usd="0.010000",
                  limite_saida=768, limite_caracteres=16000, fabrica_cliente=criar_cliente):
    if not confirmado:
        print("API real desativada; use --confirmar-envio se decidir executar uma amostra.")
        return 2
    try:
        if Path(destino).exists():
            raise ValueError("Destino já existe; nenhuma chamada será iniciada")
        caso = obter_caso(nome)
        pedido, r = preparar_pedido(caso, versao, limite_saida, limite_caracteres)
        if r is not None and r["sem_trechos"]:
            raise ValueError("Sem contexto recuperado: não iniciar chamada")
        if importlib.metadata.version("openai") != SDK:
            raise ValueError("SDK diferente do fixado")
        controle = novo_controle(1, orcamento_usd)
        # Heurística conservadora de planejamento, não contagem exata de tokens.
        entrada_prevista = len(serializar(pedido).encode("utf-8")) + 256
        reservar(controle, entrada_prevista, limite_saida)
        chave = obter_chave()
    except (ValueError, OSError) as erro:
        print("Configuração:", erro)
        return 1
    meta = {"modo": "api_real", "data_utc": datetime.now(timezone.utc).isoformat(),
            "sistema": platform.system(), "python": platform.python_version(), "sdk": SDK,
            "modelo": MODELO, "caso_id": nome, "versao_prompt": versao,
            "entrada_prevista_heuristica": entrada_prevista, "tarifas": tarifas(),
            "tentativas_sdk": 0, "max_retries": 0, "revisao_semantica": "pendente"}
    inicio = time.perf_counter()
    saidas = {}
    try:
        with fabrica_cliente(chave) as cliente:
            meta["tentativas_sdk"] = 1
            resposta = chamar_modelo(cliente, pedido)
        if resposta.get("model") != MODELO:
            raise ValueError("Modelo da resposta diferente do solicitado")
        duracao = round((time.perf_counter() - inicio) * 1000)
        custo = concluir(controle, resposta.get("usage"))
        execucao = {"modo": "api_real", "nota": "Amostra isolada; não é avaliação completa do conjunto",
                    "dataset_sha256": resumo(carregar()), "modelo": MODELO, "sdk": SDK,
                    "versao_prompt": versao,
                    "itens": [{"caso_id": nome, "pedido_sha256": identidade(caso, versao, limite_saida),
                               "limite_saida": limite_saida, "duracao_ms": duracao,
                               "resposta": {k: resposta.get(k) for k in ("id", "object", "created_at", "model", "status", "output", "usage", "incomplete_details", "error")}}]}
        # Não arquiva corpos de erro do serviço.
        if resposta.get("error") is not None:
            raise ValueError("Resposta de serviço com erro")
        saidas.update({"execucao.json": execucao, "revisao_pendente.json": modelo_revisao(execucao)})
        meta.update(status="resposta_recebida", custo_estimado_usd=None if custo is None else str(custo))
        print("Resposta arquivada para avaliação; nenhuma despesa aprovada.")
        codigo = 0
    except (OpenAIError, ValueError, TypeError, AttributeError) as erro:
        if controle["reserva"] is not None:
            concluir(controle, None)
        meta.update(status="falha", diagnostico=diagnosticar_erro(erro))
        print(meta["diagnostico"])
        codigo = 1
    meta["duracao_ms"] = round((time.perf_counter() - inicio) * 1000)
    meta["controle_local"] = retrato(controle)
    saidas["metadados.json"] = meta
    try:
        gravar_conjunto(destino, saidas)
    except (OSError, ValueError):
        print("Registro não salvo. Tentativas ao SDK:", meta["tentativas_sdk"], "— não reenviar automaticamente.")
        return 3
    return codigo
