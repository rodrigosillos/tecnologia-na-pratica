from cliente_catalogo import obter_catalogo
from configuracao import BASE_URL

try:
    categorias = obter_catalogo(BASE_URL + "/categorias")
except ValueError as erro:
    print("Consulta interrompida:", str(erro))
    raise SystemExit(1)
print("Catálogo aceito:", ", ".join(categorias))
