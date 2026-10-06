"""Extração real opcional: uma origem, uma tentativa e nenhuma aprovação."""
from datetime import datetime, timezone
from pathlib import Path
import platform
import time
import importlib.metadata
from openai import OpenAIError
from configuracao_ia import obter_chave, SDK, MODELO
from arquivos import resumo, gravar_conjunto
from contexto import origens, preparar_pedido
from cliente_ia import criar_cliente, chamar_modelo, diagnosticar_erro
from fluxo import montar_pacote, modelo_revisao, conferir_pacote


def executar_real(nome, destino, confirmado=False, fabrica_cliente=criar_cliente):
    if not confirmado:
        print("API real desativada; nenhuma chamada. Use --confirmar-envio quando desejar executar.")
        return 2
    try:
        if Path(destino).exists():
            raise ValueError("Destino já existe; nenhuma chamada será iniciada")
        fontes = origens()
        if nome not in fontes:
            raise ValueError("Origem desconhecida")
        pedido = preparar_pedido(fontes[nome])
        chave = obter_chave()
    except (ValueError, OSError) as erro:
        print("Configuração:", erro)
        return 1
    registro = {"modo": "api_real", "origem": "execucao_sdk",
                "data_utc": datetime.now(timezone.utc).isoformat(),
                "sistema": platform.system(), "python": platform.python_version(),
                "sdk_openai": importlib.metadata.version("openai"),
                "modelo_solicitado": MODELO, "pedido_sha256": resumo(pedido),
                "tentativas_sdk": 0, "max_retries": 0,
                "revisao_humana": "pendente"}
    inicio = time.perf_counter()
    saidas = {}
    try:
        if registro["sdk_openai"] != SDK:
            raise ValueError("SDK diferente do fixado")
        with fabrica_cliente(chave) as cliente:
            registro["tentativas_sdk"] = 1
            resposta = chamar_modelo(cliente, pedido)
        if resposta.get("model") != MODELO or resposta.get("error") is not None:
            raise ValueError("Resposta incompatível com o contrato desta revisão")
        # Sem cabeçalhos nem corpo de erro; guarda a saída para revisão.
        resposta = {k: resposta.get(k) for k in (
            "id", "object", "created_at", "model", "status", "output", "usage", "incomplete_details")}
        pacote = montar_pacote([{"origem_id": nome, "pedido_sha256": resumo(pedido),
                                "resposta": resposta}], "api_real")
        analise = conferir_pacote(pacote)[nome]
        saidas.update({"pacote.json": pacote, "revisao_pendente.json": modelo_revisao(pacote)})
        registro["estado_sugestao"] = analise["estado"]
        registro["status"] = "resposta_recebida"
        print("Modo: API real | uma tentativa | revisão humana pendente")
        print("Estado:", analise["estado"])
        print("Pendências:", ", ".join(analise["pendencias"]) or "nenhuma de preenchimento")
        print("Uso informado:", analise["uso"])
        codigo = 2 if analise["estado"] == "bloqueada" else 0
    except (OpenAIError, ValueError, TypeError, AttributeError) as erro:
        registro["status"] = "falha"
        registro["diagnostico"] = diagnosticar_erro(erro)
        print(registro["diagnostico"])
        codigo = 1
    registro["duracao_segundos"] = round(time.perf_counter() - inicio, 3)
    saidas["metadados.json"] = registro
    try:
        gravar_conjunto(destino, saidas)
    except (OSError, ValueError):
        if registro["tentativas_sdk"]:
            print("Registro não salvo; houve tentativa. Não reenviar automaticamente para recuperar arquivo.")
        else:
            print("Registro não salvo; nenhuma tentativa de chamada ao SDK foi iniciada.")
        return 3
    print("Arquivos:", destino)
    return codigo
