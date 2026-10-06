"""Formato solicitado ao modelo; conformidade não significa verdade."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, ValidationError
from arquivos import decodificar


class Evidencias(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    data: str | None
    valor: str | None
    descricao: str | None
    categoria: str | None


class Sugestao(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    data: str | None
    valor: str | None
    descricao: str | None
    categoria: Literal["Alimentação", "Transporte", "Materiais"] | None
    evidencias: Evidencias


def formato_resposta():
    return {"type": "json_schema", "name": "sugestao_despesa",
            "strict": True, "schema": Sugestao.model_json_schema()}


def validar_estrutura(texto):
    try:
        return Sugestao.model_validate(decodificar(texto)).model_dump()
    except ValidationError as erro:
        campos = sorted({".".join(str(p) for p in e["loc"]) for e in erro.errors()})
        raise ValueError("Estrutura inválida nos campos: " + ", ".join(campos)) from None
