"""Observação inicial: a rota padrão contém dados sintéticos controlados."""
import requests
from configuracao import BASE_URL

with requests.Session() as sessao:
    sessao.trust_env = False
    with sessao.get(
        BASE_URL + "/categorias",
        timeout=(1, 2),
        allow_redirects=False,
    ) as resposta:
        print("Status:", resposta.status_code)
        print("Tipo:", resposta.headers["Content-Type"])
        documento = resposta.json()
        print("Versão:", documento["versao"])
        print("Categorias:", ", ".join(documento["categorias"]))
