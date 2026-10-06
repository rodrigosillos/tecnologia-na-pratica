from contrato_catalogo import validar_catalogo

documento = {
    "versao": 1,
    "categorias": ["Alimentação", "Transporte", "Materiais"],
}
print("Aceitas:", validar_catalogo(documento))
