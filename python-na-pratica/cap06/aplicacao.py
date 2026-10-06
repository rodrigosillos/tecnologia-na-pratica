"""Coordena validação, importação e exportação em etapas separadas."""
from pathlib import Path
import psycopg
from arquivos import ler_csv, ler_json
from banco import importar, ESQUEMA
from cliente_catalogo import obter_catalogo
from relatorios import exportar


def executar_importacao(config, caminho, url, esquema=ESQUEMA):
    try:
        if caminho.suffix == ".csv":
            registros = ler_csv(caminho)
        elif caminho.suffix == ".json":
            registros = ler_json(caminho)
        else:
            raise ValueError("Use arquivo .csv ou .json")
        categorias = obter_catalogo(url)
        resumo = importar(config, registros, categorias, esquema)
    except (OSError, UnicodeError, ValueError) as erro:
        print("Lote não confirmado:", str(erro))
        return 1
    except psycopg.Error as erro:
        # Falha de transporte na confirmação pode deixar o resultado incerto.
        print("Falha PostgreSQL; SQLSTATE:", erro.sqlstate or "indisponível")
        print("Confira o banco antes de repetir: a confirmação pode ser incerta.")
        return 1
    print("Importação confirmada")
    print("Novas despesas:", resumo["novas"])
    print("Já existentes e idênticas:", resumo["existentes"])
    print("Repetições idênticas na entrada:", resumo["repetidas_entrada"])
    return 0


def executar_exportacao(config, destino, esquema=ESQUEMA):
    try:
        pasta = exportar(config, destino, esquema)
    except (OSError, ValueError, psycopg.Error):
        print("Exportação pendente: confira conexão, caminho e permissão de escrita.")
        print("Esta etapa não importou nem alterou despesas.")
        return 2
    print("Exportação concluída:", pasta)
    print("Arquivos: despesas.csv, despesas.html, estado.json")
    return 0


def executar_fluxo(config, caminho, url, destino, esquema=ESQUEMA):
    codigo = executar_importacao(config, caminho, url, esquema)
    if codigo != 0:
        return codigo
    codigo = executar_exportacao(config, destino, esquema)
    if codigo != 0:
        print("A importação permanece confirmada; repita somente a exportação.")
    return codigo
