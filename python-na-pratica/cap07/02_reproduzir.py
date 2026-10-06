import argparse
from reproducao import CASOS, reproduzir, apresentar

parser = argparse.ArgumentParser()
parser.add_argument("--caso", choices=CASOS, default="concluida")
args = parser.parse_args()
print("Modo: reprodução | origem: sintética | chamadas à API: 0")
resultado = reproduzir(args.caso)
apresentar(resultado)
print("Uso acima é fictício, armazenado no caso; nenhum consumo ocorreu nesta reprodução.")
raise SystemExit(0 if resultado["estado"] == "concluida" else 2)
