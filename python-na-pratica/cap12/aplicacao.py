"""Importação estruturada ou revisada; exportação independente de IA."""
import banco
from arquivos import ler_entrada
from assistencia import lote_revisado
from extracao.arquivos import ler_json
from extracao.contexto import origens
from catalogo import obter_catalogo
from exportacao import exportar, conferir_destino


def preparar_entrada(args):
    if args.comando == "importar":
        registros, entrada_hash = ler_entrada(args.entrada)
        reservados = {o["id_destino"] for o in origens().values()}
        if any(isinstance(r, dict) and r.get("id") in reservados for r in registros):
            raise ValueError("IDs de origem assistida exigem importar-revisado")
        return registros, entrada_hash, {"tipo": "estruturada", "entrada_sha256": entrada_hash}
    return lote_revisado(ler_json(args.pacote), ler_json(args.revisao))


def executar(args, config, registrar, esquema=banco.ESQUEMA):
    if args.comando == "preparar":
        banco.preparar(config, esquema)
        registrar("esquema_pronto")
        print("Esquema tnp_cap12 pronto; capítulos anteriores preservados.")
        return 0
    recibo = banco.consultar_recibo(config, args.execucao, esquema)
    if args.comando in {"importar", "importar-revisado"}:
        registros, entrada_hash, proveniencia = preparar_entrada(args)
        if recibo is not None:
            if recibo["entrada_sha256"] != entrada_hash or recibo["proveniencia"]["tipo"] != proveniencia["tipo"]:
                raise ValueError("Execução vinculada a outra entrada ou revisão")
            registrar("importacao_ja_confirmada")
        else:
            categorias = obter_catalogo(args.catalogo, args.tentativas, registrar)
            recibo = banco.importar(config, args.execucao, entrada_hash, registros, categorias, proveniencia, esquema)
            registrar("importacao_confirmada", novas=recibo["novas"], existentes=recibo["existentes"])
    if recibo is None:
        registrar("recibo_ausente")
        print("Recibo ausente; nenhuma importação confirmada encontrada.")
        return 1
    r = recibo["retrato"]
    print("Importação confirmada:", args.execucao)
    print("Retrato:", r["quantidade"], "registros /", r["total"])
    print("Origem da importação:", recibo["proveniencia"]["tipo"])
    try:
        if args.comando == "status":
            estado = conferir_destino(recibo, args.destino)
            print("Exportação:", estado)
            registrar("estado_consultado", estado=estado)
            return 0 if estado == "concluida" else 3
        estado = exportar(recibo, args.destino)
    except (OSError, ValueError):
        registrar("exportacao_pendente")
        print("Exportação pendente. A importação permanece confirmada.")
        print("Repita somente exportar com a mesma execução e um destino adequado.")
        return 3
    registrar("exportacao_concluida", estado=estado)
    print("Exportação:", estado)
    return 0
