"""Orquestração sequencial; exportar não acessa entrada, catálogo ou modelo."""
import psycopg
import banco
from arquivos import ler_entrada
from catalogo import obter_catalogo
from exportacao import exportar, conferir_destino
from recibos import validar_id
from tentativas import FalhaTransitoria


def executar(args, config, registrar):
    if args.comando == "preparar":
        banco.preparar(config)
        registrar("esquema_pronto")
        print("Esquema tnp_cap11 pronto; dados anteriores preservados.")
        return 0
    validar_id(args.execucao)
    recibo = banco.consultar_recibo(config, args.execucao)
    if args.comando == "executar":
        registros, entrada_hash = ler_entrada(args.entrada)
        if recibo is not None:
            if recibo["entrada_sha256"] != entrada_hash:
                raise ValueError("Execução já vinculada a outra entrada")
            registrar("importacao_ja_confirmada")
        else:
            categorias = obter_catalogo(args.catalogo, args.tentativas, registrar)
            recibo = banco.importar(config, args.execucao, entrada_hash, registros, categorias)
            registrar("importacao_confirmada", novas=recibo["novas"], existentes=recibo["existentes"])
    if recibo is None:
        registrar("recibo_ausente")
        print("Recibo ausente; nenhuma importação confirmada foi encontrada para esta execução.")
        return 1
    r = recibo["retrato"]
    print("Importação confirmada:", args.execucao)
    print("Retrato:", r["quantidade"], "registros /", r["total"])
    try:
        if args.comando == "status":
            estado = conferir_destino(recibo, args.destino)
            registrar("estado_consultado", estado=estado, quantidade=r["quantidade"], total=r["total"])
            print("Exportação:", estado)
            return 0 if estado == "concluida" else 3
        estado = exportar(recibo, args.destino)
    except (OSError, ValueError):
        registrar("exportacao_pendente")
        print("Exportação pendente. A importação permanece confirmada.")
        print("Confira caminho/permissões/arquivos; repita somente exportar com a mesma execução.")
        return 3
    registrar("exportacao_concluida", estado=estado, quantidade=r["quantidade"], total=r["total"])
    print("Exportação:", estado)
    return 0
