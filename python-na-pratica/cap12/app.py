"""Projeto final — ações explícitas, dados sintéticos e revisão obrigatória."""
import argparse
from pathlib import Path
import psycopg
from aplicacao import executar
from assistencia import preparar_sugestoes, inspecionar, revisar_sugestoes, consulta_sintetica
from conexao import configuracao_banco
from eventos import abrir_log
from recibos import validar_id
from catalogo import validar_url
from tentativas import FalhaTransitoria

BASE = Path(__file__).resolve().parent
BANCARIOS = {"preparar", "importar", "importar-revisado", "status", "exportar"}


def criar_parser():
    parser = argparse.ArgumentParser(description="Capítulo 12 — assistente de despesas com IA", allow_abbrev=False, color=False)
    sub = parser.add_subparsers(dest="comando", required=True)
    for nome in sorted(BANCARIOS):
        p = sub.add_parser(nome, allow_abbrev=False)
        p.add_argument("--logs", type=Path, default=BASE / "gerados/logs")
        if nome != "preparar":
            p.add_argument("--execucao", required=True)
            p.add_argument("--destino", type=Path, default=BASE / "gerados/relatorios")
        if nome in {"importar", "importar-revisado"}:
            p.add_argument("--catalogo", default="http://127.0.0.1:8765/categorias")
            p.add_argument("--tentativas", type=int, choices=range(1,6), default=3)
        if nome == "importar":
            p.add_argument("--entrada", type=Path, required=True)
        elif nome == "importar-revisado":
            p.add_argument("--pacote", type=Path, required=True)
            p.add_argument("--revisao", type=Path, required=True)
    p = sub.add_parser("sugerir", allow_abbrev=False)
    p.add_argument("--cenario", choices=["padrao", "incompleta", "recusa"], default="padrao")
    p.add_argument("--destino", type=Path, required=True)
    p = sub.add_parser("inspecionar", allow_abbrev=False)
    p.add_argument("--pacote", type=Path, required=True)
    p = sub.add_parser("revisar", allow_abbrev=False)
    p.add_argument("--pacote", type=Path, required=True)
    p.add_argument("--revisao", type=Path, required=True)
    p.add_argument("--destino", type=Path, required=True)
    p = sub.add_parser("consultar", allow_abbrev=False)
    p.add_argument("--caso", choices=["P01","P02","P03","P04","P05"], required=True)
    p.add_argument("--destino", type=Path, required=True)
    for nome, campo in [("extrair-real", "origem"), ("consultar-real", "pergunta")]:
        p = sub.add_parser(nome, allow_abbrev=False)
        p.add_argument("--"+campo, required=True)
        p.add_argument("--destino", type=Path, required=True)
        p.add_argument("--confirmar-envio", action="store_true")
        p.add_argument("--orcamento-usd", default="0.010000")
    return parser


def main(argv=None):
    args = criar_parser().parse_args(argv)
    fechar = lambda: None
    try:
        if args.comando == "sugerir": return preparar_sugestoes(args.destino, args.cenario)
        if args.comando == "inspecionar": return inspecionar(args.pacote)
        if args.comando == "revisar": return revisar_sugestoes(args.pacote, args.revisao, args.destino)
        if args.comando == "consultar": return consulta_sintetica(args.caso, args.destino)
        if args.comando in {"extrair-real", "consultar-real"}:
            from ia_real import executar_real
            tipo, entrada = ("extracao", args.origem) if args.comando == "extrair-real" else ("consulta", args.pergunta)
            return executar_real(tipo, entrada, args.destino, args.confirmar_envio, args.orcamento_usd)
        if args.comando != "preparar": validar_id(args.execucao)
        if args.comando in {"importar", "importar-revisado"}: validar_url(args.catalogo)
        registrar, fechar, caminho = abrir_log(args.logs, getattr(args, "execucao", None), args.comando)
        registrar("inicio")
        config = configuracao_banco()
        try:
            codigo = executar(args, config, registrar)
        except (ValueError, UnicodeError, FalhaTransitoria):
            registrar("operacao_bloqueada")
            print("Operação bloqueada: confira revisão, origem, entrada e catálogo.")
            codigo = 1
        except psycopg.Error as erro:
            registrar("banco_indisponivel_ou_incerto", sqlstate=erro.sqlstate)
            print("Estado não confirmado; consulte status antes de repetir escrita.")
            codigo = 4
        registrar("fim", estado=str(codigo))
        print("Log:", caminho)
        return codigo
    except (ValueError, UnicodeError, EOFError):
        print("Operação bloqueada: configuração, pacote, revisão ou destino incompatível.")
        return 1
    except OSError:
        print("Falha de arquivo/log. Preserve os dados e confira o estado antes de repetir.")
        return 4
    finally:
        fechar()


if __name__ == "__main__":
    raise SystemExit(main())
