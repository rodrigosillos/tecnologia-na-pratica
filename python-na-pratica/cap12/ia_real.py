"""Extensão optativa: uma tentativa, custo estimado, nenhuma escrita no banco."""
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from time import perf_counter
from openai import OpenAIError
from extracao.configuracao_ia import obter_chave, MODELO, SDK
from extracao.cliente_ia import criar_cliente, chamar_modelo, diagnosticar_erro
from extracao.arquivos import gravar_conjunto, serializar, resumo
from extracao import fluxo as extrair, contexto as textos
from consulta import fluxo as consultar, contexto as perguntas
from consulta.busca import recuperar
from consulta.documentos import carregar_corpus
from custos import novo_controle, reservar, concluir, retrato, tarifas


def executar_real(tipo, entrada, destino, confirmado=False, orcamento="0.010000", fabrica_cliente=criar_cliente):
    if not confirmado:
        print("API real desativada; nenhuma chamada. Confirmação explícita é obrigatória.")
        return 2
    try:
        if Path(destino).exists() or Path(destino).is_symlink():
            raise ValueError("Destino existente")
        if version("openai") != SDK:
            raise ValueError("SDK diferente do fixado")
        controle = novo_controle(max_chamadas=1, orcamento_usd=orcamento)
        recuperacao = None
        if tipo == "extracao":
            fontes = textos.origens()
            if entrada not in fontes:
                raise ValueError("Origem desconhecida")
            pedido = textos.preparar_pedido(fontes[entrada])
        elif tipo == "consulta":
            recuperacao = recuperar(entrada, carregar_corpus())
            pedido = None if recuperacao["sem_trechos"] else perguntas.preparar_pedido(recuperacao)
        else:
            raise ValueError("Tipo desconhecido")
        if pedido is not None:
            texto_pedido = serializar(pedido)
            if len(texto_pedido) > 16000:
                raise ValueError("Pedido acima de 16.000 caracteres")
            # Aproximação didática, não tokenizador nem limite superior garantido.
            reservar(controle, len(texto_pedido.encode("utf-8")) + 256, pedido["max_output_tokens"])
            chave = obter_chave()
        else:
            chave = None
    except (ValueError, OSError):
        print("Configuração bloqueada; confira destino, origem, orçamento e credencial da sessão.")
        return 1
    meta = {"modo": "api_real", "tarefa": tipo, "data_utc": datetime.now(timezone.utc).isoformat(),
            "modelo": MODELO, "sdk": SDK, "tentativas_sdk": 0, "max_retries": 0,
            "pedido_sha256": resumo(pedido), "tarifas_referencia": tarifas(),
            "revisao": "pendente", "banco": "nao_utilizado"}
    saidas = {}
    inicio = perf_counter()
    try:
        resposta = None
        if pedido is not None:
            with fabrica_cliente(chave) as cliente:
                meta["tentativas_sdk"] = 1
                resposta = chamar_modelo(cliente, pedido)
            uso = resposta.get("usage") if isinstance(resposta, dict) else None
            concluir(controle, uso)
            if not isinstance(resposta, dict) or resposta.get("model") != MODELO or resposta.get("error") is not None:
                raise ValueError("Resposta incompatível")
            resposta = {k: resposta.get(k) for k in ("id", "object", "created_at", "model", "status", "output", "usage", "incomplete_details")}
        if tipo == "extracao":
            pacote = extrair.montar_pacote([{"origem_id": entrada, "pedido_sha256": resumo(pedido), "resposta": resposta}], "api_real")
            analises = extrair.conferir_pacote(pacote)
            estado = analises[entrada]["estado"]
            saidas.update({"pacote.json": pacote, "analises.json": analises,
                           "revisao_pendente.json": extrair.modelo_revisao(pacote)})
        else:
            pacote = consultar.montar_pacote(recuperacao, resposta, "api_real")
            analise = consultar.conferir_pacote(pacote)
            estado = analise["estado"]
            saidas.update({"pacote.json": pacote, "analise.json": analise, "recuperacao.json": recuperacao})
            consultar.apresentar(pacote, analise)
        meta.update(status="sem_chamada" if pedido is None else "resposta_recebida", estado=estado)
        print("Estado:", estado, "| Tentativas SDK:", meta["tentativas_sdk"])
        codigo = 1 if estado == "bloqueada" else 0
    except (OpenAIError, ValueError, TypeError, AttributeError):
        if meta["tentativas_sdk"] and controle["reserva"] is not None:
            concluir(controle, None)
        meta.update(status="falha", diagnostico="IA indisponível ou resposta incompatível; sem repetição automática")
        print(meta["diagnostico"])
        codigo = 1
    meta["duracao_segundos"] = round(perf_counter()-inicio,3)
    meta["controle"] = retrato(controle)
    saidas["metadados.json"] = meta
    try:
        gravar_conjunto(destino, saidas)
    except (OSError, ValueError):
        print("Arquivos não salvos. Tentativas SDK:", meta["tentativas_sdk"], "— não repetir para recuperar arquivo.")
        return 3
    return codigo
