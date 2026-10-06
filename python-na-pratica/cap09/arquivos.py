"""JSON estrito e publicação local de um conjunto de arquivos, uma execução por vez."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile


def pares_unicos(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError("JSON: chave repetida " + chave)
        objeto[chave] = valor
    return objeto


def constante_invalida(valor):
    raise ValueError("JSON: constante não permitida " + valor)


def decodificar(texto):
    if not isinstance(texto, str) or len(texto) > 100000:
        raise ValueError("JSON: texto inválido ou acima de 100.000 caracteres")
    try:
        return json.loads(texto, object_pairs_hook=pares_unicos,
                          parse_constant=constante_invalida)
    except (json.JSONDecodeError, RecursionError) as erro:
        raise ValueError("JSON: conteúdo malformado") from erro


def ler_json(caminho):
    return decodificar(Path(caminho).read_text(encoding="utf-8-sig"))


def serializar(objeto):
    return json.dumps(objeto, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def resumo(objeto):
    texto = json.dumps(objeto, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def gravar_conjunto(destino, arquivos):
    destino = Path(destino)
    if destino.exists():
        raise ValueError("Destino já existe; escolha outra pasta para preservar a execução anterior")
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporaria = Path(tempfile.mkdtemp(prefix=".cap09-", dir=destino.parent))
    try:
        for nome, objeto in arquivos.items():
            if Path(nome).name != nome:
                raise ValueError("Nome de saída inválido")
            (temporaria / nome).write_text(serializar(objeto), encoding="utf-8")
        temporaria.rename(destino)
    finally:
        if temporaria.exists():
            shutil.rmtree(temporaria)
