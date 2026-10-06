"""Uma chamada ao SDK; sem repetição automática e sem expor corpo de erros."""
from openai import (OpenAI, APIConnectionError, APITimeoutError,
                    APIStatusError, APIResponseValidationError)
from configuracao_ia import BASE_URL


def criar_cliente(chave, http_client=None):
    return OpenAI(api_key=chave, base_url=BASE_URL, timeout=30.0,
                  max_retries=0, http_client=http_client)


def chamar_modelo(cliente, pedido):
    resposta = cliente.responses.create(**pedido)
    return resposta.model_dump(mode="json")


def diagnosticar_erro(erro):
    # Não use str(erro): um corpo de erro pode repetir dados da requisição.
    if isinstance(erro, APITimeoutError):
        return "IA: tempo de espera excedido; processamento e consumo podem ser incertos"
    if isinstance(erro, APIConnectionError):
        return "IA: falha de comunicação; confira a conexão antes de tentar novamente"
    if isinstance(erro, APIResponseValidationError):
        return "IA: resposta incompatível com o SDK fixado"
    if isinstance(erro, APIStatusError):
        status = erro.status_code
        if status == 401:
            return "IA: autenticação recusada (401); confira a chave e seu acesso"
        if status == 403:
            return "IA: acesso não permitido (403)"
        if status == 404:
            return "IA: recurso ou modelo indisponível (404); não houve troca automática de modelo"
        if status == 429:
            if erro.code in {"insufficient_quota", "credit_balance_exhausted", "billing_hard_limit_reached"}:
                return "IA: saldo ou quota insuficiente (429); confira a conta"
            return "IA: limite ou quota atingido (429); confira a conta antes de repetir"
        if 500 <= status <= 599:
            return "IA: falha no serviço (5xx); nenhuma repetição automática foi feita"
        return "IA: requisição recusada; confira parâmetros e acesso"
    return "IA: falha inesperada; confira a configuração e o SDK"
