"""Só a leitura HTTP explicitamente classificada pode ser repetida."""
import time


class FalhaTransitoria(Exception):
    """Falha de uma leitura GET que admite uma nova tentativa limitada."""


def tentar_leitura(operacao, max_tentativas=3, espera=0.2,
                  registrar=lambda evento, **campos: None, dormir=time.sleep):
    if type(max_tentativas) is not int or not 1 <= max_tentativas <= 5:
        raise ValueError("Tentativas: use um inteiro de 1 a 5")
    if isinstance(espera, bool) or not isinstance(espera, (int, float)) or not 0 <= espera <= 1:
        raise ValueError("Espera: use de 0 a 1 segundo")
    for numero in range(1, max_tentativas + 1):
        registrar("catalogo_tentativa", tentativa=numero)
        try:
            return operacao()
        except FalhaTransitoria:
            if numero == max_tentativas:
                registrar("catalogo_esgotado", tentativa=numero)
                raise
            atraso = espera * 2 ** (numero - 1)
            registrar("catalogo_aguardar", segundos=atraso)
            dormir(atraso)
