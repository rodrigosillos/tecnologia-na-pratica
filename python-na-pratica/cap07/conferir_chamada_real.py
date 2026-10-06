"""Confere um registro local já produzido; não faz outra chamada à API."""
import argparse
import json
from pathlib import Path
from configuracao_ia import MODELO, SDK, VERSAO_PROMPT
from contexto import pedido_exemplo, sha256_texto
from interpretacao import interpretar_resposta


def conferir(registro):
    esperado = {
        "modo": "api_real", "origem": "execucao_sdk", "capitulo": 7,
        "revisao": "R01", "sdk_openai": SDK, "modelo_solicitado": MODELO,
        "versao_prompt": VERSAO_PROMPT, "max_retries": 0, "tentativas_sdk": 1,
        "status": "resposta_recebida",
    }
    if not isinstance(registro, dict) or any(registro.get(k) != v for k, v in esperado.items()):
        raise ValueError("Registro não atende aos metadados da chamada real desta revisão")
    pedido = pedido_exemplo()
    if (registro.get("input_sha256") != sha256_texto(pedido["input"])
            or registro.get("instructions_sha256") != sha256_texto(pedido["instructions"])):
        raise ValueError("Entrada ou instruções diferentes das usadas nesta revisão")
    if registro.get("pedido") != pedido:
        raise ValueError("Parâmetros diferentes dos configurados para esta conferência")
    resposta = registro.get("resposta")
    if not isinstance(resposta, dict) or resposta.get("model") != MODELO:
        raise ValueError("Modelo devolvido não corresponde ao snapshot fixado")
    identificador = resposta.get("id")
    if (not isinstance(identificador, str) or not identificador.startswith("resp_")
            or "sintetica" in identificador):
        raise ValueError("Identificador de resposta ausente ou sintético")
    resultado = interpretar_resposta(resposta)
    if resultado["estado"] != "concluida":
        raise ValueError("Chamada não entregou texto concluído com uso válido")
    if resultado != registro.get("resultado"):
        raise ValueError("Resultado registrado diverge do envelope de resposta")
    return resultado


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("registro", type=Path)
    args = parser.parse_args()
    try:
        registro = json.loads(args.registro.read_text(encoding="utf-8"))
        resultado = conferir(registro)
    except (OSError, UnicodeError, ValueError) as erro:
        print("Conferência pendente:", str(erro))
        return 1
    print("Registro real consistente com o contrato desta revisão.")
    print("Chamadas feitas por esta conferência: 0")
    print("Revisão humana do conteúdo: ainda necessária; não é comprovada pelos metadados.")
    print("Total de tokens informado:", resultado["uso"]["total_tokens"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
