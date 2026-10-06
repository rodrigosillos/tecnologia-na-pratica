"""GET local, sem retry oculto, sem redirecionamento ou catálogo alternativo."""
from urllib.parse import urlsplit
import requests
from arquivos import carregar_json
from contrato_catalogo import validar_catalogo
from tentativas import FalhaTransitoria, tentar_leitura


def validar_url(url):
    partes = urlsplit(url)
    if (partes.scheme != "http" or partes.hostname != "127.0.0.1"
            or partes.username is not None or partes.password is not None
            or partes.query or partes.fragment or partes.port is None
            or not 1 <= partes.port <= 65535):
        raise ValueError("Catálogo: use http://127.0.0.1:porta/caminho")


def obter_uma_vez(url):
    validar_url(url)
    try:
        with requests.Session() as sessao:
            sessao.trust_env = False
            with sessao.get(url, timeout=(1.0, 2.0), allow_redirects=False,
                            stream=True, headers={"Accept": "application/json"}) as resposta:
                if resposta.status_code in {502, 503, 504}:
                    raise FalhaTransitoria("Catálogo temporariamente indisponível")
                if resposta.status_code != 200:
                    raise ValueError("Catálogo: HTTP não aceito: " + str(resposta.status_code))
                if resposta.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                    raise ValueError("Catálogo: Content-Type inválido")
                dados = bytearray()
                for bloco in resposta.iter_content(1024):
                    dados.extend(bloco)
                    if len(dados) > 32_768:
                        raise ValueError("Catálogo acima de 32 KiB")
    except (requests.Timeout, requests.ConnectionError) as erro:
        raise FalhaTransitoria("Catálogo: falha de comunicação HTTP") from erro
    except requests.RequestException as erro:
        raise ValueError("Catálogo: falha HTTP não repetível neste roteiro") from erro
    try:
        return validar_catalogo(carregar_json(dados.decode("utf-8")))
    except UnicodeError as erro:
        raise ValueError("Catálogo: UTF-8 inválido") from erro


def obter_catalogo(url, max_tentativas=3, registrar=lambda evento, **campos: None):
    validar_url(url)
    return tentar_leitura(lambda: obter_uma_vez(url), max_tentativas,
                          registrar=registrar)
