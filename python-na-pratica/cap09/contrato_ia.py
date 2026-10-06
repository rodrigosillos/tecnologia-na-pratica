"""Estrutura de resposta; suporte semântico exige revisão."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, ValidationError
from arquivos import decodificar


class Fonte(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    trecho_id: str
    citacao: str


class Afirmacao(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    texto: str
    fontes: list[Fonte]


class Resposta(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    situacao: Literal["respondida", "sem_cobertura"]
    afirmacoes: list[Afirmacao]


def formato_resposta():
    return {"type": "json_schema", "name": "consulta_politica",
            "strict": True, "schema": Resposta.model_json_schema()}


def validar_estrutura(texto):
    try:
        return Resposta.model_validate(decodificar(texto)).model_dump()
    except ValidationError:
        raise ValueError("Resposta fora do esquema de consulta") from None
