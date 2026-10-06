"""Contrato próprio da API didática; sem acesso à rede."""
from regras import texto_obrigatorio


def validar_catalogo(documento: object) -> list[str]:
    if not isinstance(documento, dict):
        raise ValueError("catálogo: esperado um objeto")
    if set(documento) != {"versao", "categorias"}:
        raise ValueError("catálogo: campos ausentes ou extras")
    if type(documento["versao"]) is not int or documento["versao"] != 1:
        raise ValueError("catálogo: versão não aceita")
    categorias = documento["categorias"]
    if not isinstance(categorias, list) or not 1 <= len(categorias) <= 20:
        raise ValueError("catálogo: informe de 1 a 20 categorias")
    aceitas = []
    for item in categorias:
        nome = texto_obrigatorio(item, "categoria", 30)
        if not nome.isprintable():
            raise ValueError("categoria: contém caractere de controle")
        if nome in aceitas:
            raise ValueError("catálogo: categoria repetida")
        aceitas.append(nome)
    return aceitas
