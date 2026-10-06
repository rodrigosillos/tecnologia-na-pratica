"""Os erros são intencionais; cada consulta falha com saída 1."""
import sys
from cliente_catalogo import obter_catalogo
from configuracao import BASE_URL

rotas = {
    "404": "/ausente",
    "503": "/cenarios/indisponivel",
    "json": "/cenarios/json-invalido",
    "contrato": "/cenarios/contrato-invalido",
    "tipo": "/cenarios/tipo-incorreto",
    "lenta": "/cenarios/lenta",
    "redirect": "/cenarios/redirecionamento",
}
if len(sys.argv) != 2 or sys.argv[1] not in rotas:
    print("Uso: python 06_observar_falhas.py 404|503|json|contrato|tipo|lenta|redirect")
    raise SystemExit(2)
try:
    obter_catalogo(BASE_URL + rotas[sys.argv[1]])
except ValueError as erro:
    print("Consulta interrompida:", str(erro))
    raise SystemExit(1)
print("Resultado inesperado: a falha não foi detectada")
raise SystemExit(2)
