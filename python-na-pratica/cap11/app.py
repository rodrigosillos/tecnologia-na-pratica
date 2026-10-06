"""Interface do capítulo 11. Nenhuma chave de IA é solicitada ou utilizada."""
import argparse
from pathlib import Path
import psycopg
from aplicacao import executar
from conexao import configuracao_banco
from eventos import abrir_log
from recibos import validar_id
from catalogo import validar_url
from tentativas import FalhaTransitoria

BASE = Path(__file__).resolve().parent


def criar_parser():
    parser = argparse.ArgumentParser(description="Capítulo 11 — execução confiável", allow_abbrev=False, color=False)
    sub = parser.add_subparsers(dest="comando", required=True)
    for nome in ("preparar", "executar", "status", "exportar"):
        p = sub.add_parser(nome, allow_abbrev=False)
        p.add_argument("--logs", type=Path, default=BASE / "gerados/logs")
        if nome != "preparar":
            p.add_argument("--execucao", required=True)
            p.add_argument("--destino", type=Path, default=BASE / "gerados/relatorios")
        if nome == "executar":
            p.add_argument("--entrada", type=Path, required=True)
            p.add_argument("--catalogo", default="http://127.0.0.1:8765/categorias")
            p.add_argument("--tentativas", type=int, choices=range(1, 6), default=3)
    return parser


def main(argv=None):
    parser = criar_parser()
    args = parser.parse_args(argv)
    fechar = lambda: None
    try:
        if args.comando != "preparar":
            validar_id(args.execucao)
        if args.comando == "executar":
            validar_url(args.catalogo)
        registrar, fechar, caminho = abrir_log(args.logs, getattr(args, "execucao", None), args.comando)
        registrar("inicio")
        config = configuracao_banco()
        try:
            codigo = executar(args, config, registrar)
        except (ValueError, UnicodeError, FalhaTransitoria):
            registrar("operacao_bloqueada")
            print("Operação bloqueada: confira entrada, catálogo e vínculo da execução.")
            codigo = 1
        except psycopg.Error as erro:
            registrar("banco_indisponivel_ou_incerto", sqlstate=erro.sqlstate)
            print("Estado não confirmado nesta tentativa; consulte status antes de repetir uma escrita.")
            codigo = 4
        registrar("fim", estado=str(codigo))
        print("Log:", caminho)
        return codigo
    except (ValueError, UnicodeError, EOFError):
        print("Configuração ou identificação inválida; confira --help.")
        return 1
    except OSError:
        print("Falha de arquivo/log. Consulte status: não conclua que a importação foi desfeita.")
        return 4
    finally:
        fechar()


if __name__ == "__main__":
    raise SystemExit(main())
