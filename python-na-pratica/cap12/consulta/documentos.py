"""Corpus Markdown controlado: um trecho por seção de nível dois."""
import re
from pathlib import Path
from .arquivos import ler_json, resumo
from .configuracao_ia import PASTA

CABECALHO = re.compile(r"^## \[([A-Z]+-\d{3})\] (.+)$", re.MULTILINE)


def separar_secoes(texto, documento, titulo_documento):
    cabecalhos = list(CABECALHO.finditer(texto))
    if not cabecalhos or len(re.findall(r"^## ", texto, re.MULTILINE)) != len(cabecalhos):
        raise ValueError("Documento sem seções válidas ou com cabeçalho sem ID")
    trechos = []
    for i, cabecalho in enumerate(cabecalhos):
        fim = cabecalhos[i + 1].start() if i + 1 < len(cabecalhos) else len(texto)
        corpo = texto[cabecalho.end():fim].strip()
        if not corpo or len(corpo) > 3000:
            raise ValueError("Seção vazia ou acima de 3.000 caracteres")
        trechos.append({"id": cabecalho[1], "documento": documento,
                        "titulo_documento": titulo_documento,
                        "secao": cabecalho[2], "texto": corpo})
    return trechos


def carregar_corpus(pasta=None):
    pasta = Path(pasta) if pasta is not None else PASTA / "corpus"
    catalogo = ler_json(pasta / "catalogo.json")
    if (not isinstance(catalogo, dict) or set(catalogo) != {"versao", "natureza", "documentos"}
            or not isinstance(catalogo["versao"], str) or not catalogo["versao"].strip()
            or catalogo["natureza"] != "politica_ficticia_para_estudo"
            or not isinstance(catalogo["documentos"], list) or not 1 <= len(catalogo["documentos"]) <= 12):
        raise ValueError("Catálogo do corpus inválido")
    trechos, nomes = [], set()
    for doc in catalogo["documentos"]:
        if not isinstance(doc, dict) or set(doc) != {"arquivo", "titulo"}:
            raise ValueError("Documento do catálogo inválido")
        nome, titulo = doc["arquivo"], doc["titulo"]
        if (not isinstance(nome, str) or not re.fullmatch(r"[a-z0-9_-]+\.md", nome)
                or nome in nomes or not isinstance(titulo, str) or not titulo.strip()):
            raise ValueError("Nome ou título de documento inválido")
        caminho = pasta / nome
        if caminho.is_symlink() or caminho.stat().st_size > 50000:
            raise ValueError("Documento fora do contrato local")
        nomes.add(nome)
        trechos.extend(separar_secoes(caminho.read_text(encoding="utf-8-sig"), nome, titulo))
    ids = [t["id"] for t in trechos]
    if len(ids) != len(set(ids)) or len(ids) > 50:
        raise ValueError("ID de seção repetido ou mais de 50 seções")
    base = {"versao": catalogo["versao"], "natureza": catalogo["natureza"], "trechos": trechos}
    if sum(len(t["texto"]) for t in trechos) > 30000:
        raise ValueError("Corpus acima de 30.000 caracteres de conteúdo")
    return {**base, "sha256": resumo(base)}
