import argparse
from execucao_real import executar_real

parser = argparse.ArgumentParser()
parser.add_argument("--confirmar-envio", action="store_true")
args = parser.parse_args()
raise SystemExit(executar_real(confirmado=args.confirmar_envio))
