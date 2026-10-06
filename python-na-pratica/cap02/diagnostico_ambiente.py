import sys
from pathlib import Path

print("Versão:", sys.version.split()[0])
print("Interpretador:", sys.executable)
print("Pasta atual:", Path.cwd())
print("Ambiente virtual:", sys.prefix != sys.base_prefix)
