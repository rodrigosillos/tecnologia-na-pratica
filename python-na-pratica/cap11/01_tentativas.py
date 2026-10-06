"""Ensaio HTTP de loopback: servidor fornecido, cliente sequencial."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from catalogo import obter_catalogo
from tentativas import FalhaTransitoria


def main():
    p = argparse.ArgumentParser(description=__doc__, color=False)
    p.add_argument("--cenario", choices=["recupera", "esgota", "contrato"], default="recupera")
    args = p.parse_args()
    recebidas = []

    class Servidor(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            recebidas.append(self.path)
            if args.cenario == "contrato":
                status, corpo = 200, b'{"versao": 1, "categorias": "incorreto"}'
            elif args.cenario == "esgota" or len(recebidas) <= 2:
                status, corpo = 503, b'{}'
            else:
                status, corpo = 200, '{"versao":1,"categorias":["Alimentação","Transporte","Materiais"]}'.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

    servidor = HTTPServer(("127.0.0.1", 0), Servidor)
    thread = Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    try:
        url = "http://127.0.0.1:" + str(servidor.server_port) + "/categorias"
        def registrar(evento, **campos):
            print(evento, campos)
        try:
            categorias = obter_catalogo(url, 3, registrar)
            print("Catálogo aceito:", len(categorias), "categorias")
            codigo = 0
        except (ValueError, FalhaTransitoria):
            print("Catálogo não obtido; nenhuma importação iniciada.")
            codigo = 1
        print("Tentativas HTTP:", len(recebidas))
        return codigo
    finally:
        servidor.shutdown()
        thread.join()
        servidor.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
