"""Cliente da API LOCAL: uma tentativa, sem cache, sem catálogo alternativo."""
import json
from urllib.parse import urlsplit

import requests

from arquivos import objeto_sem_chaves_repetidas, rejeitar_constante
from contrato_catalogo import validar_catalogo

LIMITE_RESPOSTA = 32_768
TIMEOUT = (1.0, 2.0)


def validar_url_local(url: str) -> None:
    partes = urlsplit(url)
    if (partes.scheme != "http" or partes.hostname != "127.0.0.1"
            or partes.username is not None or partes.password is not None
            or partes.query or partes.fragment or partes.port is None):
        raise ValueError("API: use http://127.0.0.1:porta/caminho no laboratório")
    if not 1 <= partes.port <= 65535:
        raise ValueError("API: porta inválida")


def obter_catalogo(url: str, timeout: tuple = TIMEOUT) -> list[str]:
    validar_url_local(url)
    try:
        with requests.Session() as sessao:
            # O servidor local não usa proxy nem credenciais de .netrc.
            sessao.trust_env = False
            with sessao.get(
                url,
                headers={"Accept": "application/json"},
                timeout=timeout,
                allow_redirects=False,
                stream=True,
            ) as resposta:
                resposta.raise_for_status()
                if resposta.status_code != 200:
                    raise ValueError("API: esperado HTTP 200; recebido "
                                     + str(resposta.status_code))
                tipo = resposta.headers.get("Content-Type", "")
                if tipo.split(";", 1)[0].strip().lower() != "application/json":
                    raise ValueError("API: Content-Type deve ser application/json")
                conteudo = bytearray()
                for bloco in resposta.iter_content(chunk_size=1024):
                    if len(conteudo) + len(bloco) > LIMITE_RESPOSTA:
                        raise ValueError("API: resposta acima de 32 KiB")
                    conteudo.extend(bloco)
    except requests.exceptions.ConnectTimeout as erro:
        # Em alguns Windows, porta sem listener vira ConnectTimeout em vez de
        # ConnectionError; em ambos os casos não há resposta HTTP a examinar.
        raise ValueError("API: falha de comunicação HTTP") from erro
    except requests.exceptions.Timeout as erro:
        raise ValueError("API: tempo limite de conexão ou leitura excedido") from erro
    except requests.exceptions.HTTPError as erro:
        raise ValueError("API: resposta HTTP " + str(erro.response.status_code)) from erro
    except requests.exceptions.RequestException as erro:
        raise ValueError("API: falha de comunicação HTTP") from erro

    try:
        texto = conteudo.decode("utf-8")
        documento = json.loads(
            texto,
            object_pairs_hook=objeto_sem_chaves_repetidas,
            parse_constant=rejeitar_constante,
        )
    except UnicodeError as erro:
        raise ValueError("API: resposta não está em UTF-8") from erro
    except json.JSONDecodeError as erro:
        raise ValueError("API: JSON inválido") from erro
    except RecursionError as erro:
        raise ValueError("API: JSON com aninhamento excessivo") from erro
    return validar_catalogo(documento)
