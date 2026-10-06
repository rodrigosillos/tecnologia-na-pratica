"""Estimativas em USD com Decimal; sem promessa de equivalência à fatura."""
from decimal import Decimal, InvalidOperation
from extracao.arquivos import ler_json
from pathlib import Path
from extracao.configuracao_ia import MODELO
PASTA = Path(__file__).resolve().parent
from extracao.interpretacao import uso_normalizado


def decimal_nao_negativo(texto):
    if not isinstance(texto, str) or len(texto) > 30:
        raise ValueError("Valor decimal deve ser texto curto")
    try:
        numero = Decimal(texto)
    except InvalidOperation:
        raise ValueError("Valor decimal inválido") from None
    if not numero.is_finite() or numero < 0:
        raise ValueError("Valor decimal negativo ou não finito")
    return numero


def tarifas():
    t = ler_json(PASTA / "dados/tarifas_referencia.json")
    if t["modelo"] != MODELO or t["moeda"] != "USD" or t["perfil"] != "texto_padrao_sem_desconto_de_cache":
        raise ValueError("Perfil de tarifas incompatível")
    decimal_nao_negativo(t["entrada_por_milhao"])
    decimal_nao_negativo(t["saida_por_milhao"])
    return t


def estimar(entrada, saida, tabela=None):
    if any(type(n) is not int or not 0 <= n <= 10000000 for n in [entrada, saida]):
        raise ValueError("Contagem de tokens inválida")
    t = tarifas() if tabela is None else tabela
    custo_entrada = Decimal(entrada) * decimal_nao_negativo(t["entrada_por_milhao"])
    custo_saida = Decimal(saida) * decimal_nao_negativo(t["saida_por_milhao"])
    return (custo_entrada + custo_saida) / Decimal("1000000")


def custo_de_uso(uso, tabela=None):
    u = uso_normalizado(uso)
    return None if u is None else estimar(u["input_tokens"], u["output_tokens"], tabela)


def novo_controle(max_chamadas=3, orcamento_usd="0.010000"):
    if type(max_chamadas) is not int or not 1 <= max_chamadas <= 20:
        raise ValueError("Máximo de chamadas deve estar entre 1 e 20")
    limite = decimal_nao_negativo(orcamento_usd)
    return {"max_chamadas": max_chamadas, "orcamento": limite, "tentativas": 0,
            "consumo_estimado": Decimal("0"), "reserva": None, "incerto": False}


def reservar(controle, entrada_prevista, saida_maxima):
    if controle["incerto"] or controle["reserva"] is not None:
        raise ValueError("Consumo incerto ou chamada anterior pendente; interromper")
    custo = estimar(entrada_prevista, saida_maxima)
    if controle["tentativas"] >= controle["max_chamadas"]:
        raise ValueError("Limite de chamadas atingido")
    if controle["consumo_estimado"] + custo > controle["orcamento"]:
        raise ValueError("Reserva excede o orçamento estimado")
    controle["tentativas"] += 1
    controle["reserva"] = custo
    return custo


def concluir(controle, uso):
    if controle["reserva"] is None:
        raise ValueError("Não há chamada reservada")
    custo = custo_de_uso(uso)
    if custo is None:
        controle["incerto"] = True
        return None  # Não libera a reserva nem inventa consumo zero.
    if custo > controle["reserva"] or controle["consumo_estimado"] + custo > controle["orcamento"]:
        controle["incerto"] = True
    controle["consumo_estimado"] += custo
    controle["reserva"] = None
    return custo


def retrato(controle):
    return {k: str(v) if isinstance(v, Decimal) else v for k, v in controle.items()}
