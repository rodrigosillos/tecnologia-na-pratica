"""Origens e catálogo locais versionados; o modelo não escolhe IDs de negócio."""
from .configuracao_ia import PASTA, MODELO, limite_saida
from .arquivos import ler_json
from contrato_catalogo import validar_catalogo
from .contrato_ia import formato_resposta, Sugestao


def categorias():
    nomes = validar_catalogo(ler_json(PASTA / "entradas/catalogo.json"))
    enum = Sugestao.model_json_schema()["properties"]["categoria"]["anyOf"][0]["enum"]
    if set(nomes) != set(enum):
        raise ValueError("Catálogo e esquema divergentes; revisar o contrato")
    return nomes


def origens():
    registros = ler_json(PASTA / "entradas/origens.json")
    if not isinstance(registros, list) or not registros:
        raise ValueError("Origens: lista vazia ou inválida")
    resultado = {}
    ids = set()
    from regras import validar_despesa
    for r in registros:
        if not isinstance(r, dict) or set(r) != {"origem_id", "id_destino", "texto"}:
            raise ValueError("Origem com campos inválidos")
        nome = r["origem_id"]
        if not isinstance(nome, str) or not nome or nome in resultado:
            raise ValueError("Origem vazia ou repetida")
        if not isinstance(r["texto"], str) or not 1 <= len(r["texto"].strip()) <= 3000:
            raise ValueError("Texto da origem vazio ou acima de 3.000 caracteres")
        validar_despesa({"id": r["id_destino"], "data": "2026-09-11",
                        "descricao": "Teste de identificador", "categoria": "Transporte",
                        "valor": "1.00"}, categorias())
        if r["id_destino"] in ids:
            raise ValueError("Identificador de destino repetido")
        ids.add(r["id_destino"])
        resultado[nome] = r
    return resultado


def preparar_pedido(origem):
    instrucoes = (PASTA / "prompts/extracao.md").read_text(encoding="utf-8").strip()
    return {"model": MODELO, "instructions": instrucoes,
            "input": "Documento sintético para extração:\n" + origem["texto"],
            "text": {"format": formato_resposta()}, "max_output_tokens": limite_saida(),
            "store": False, "truncation": "disabled", "tools": []}
