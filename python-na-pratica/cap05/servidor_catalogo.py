"""Servidor DIDÁTICO local. Não usar como servidor público ou de produção.
O leitor recebe este arquivo pronto. Casos são sintéticos e determinísticos.
"""
import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CATALOGO = {"versao": 1, "categorias": ["Alimentação", "Transporte", "Materiais"]}


def json_bytes(objeto):
    return json.dumps(objeto, ensure_ascii=False).encode("utf-8")


class ServidorLocal(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, endereco):
        self.contagens = {}
        self.trava = threading.Lock()
        super().__init__(endereco, RespostaLocal)


class RespostaLocal(BaseHTTPRequestHandler):
    def log_message(self, formato, *args):
        pass

    def do_GET(self):
        with self.server.trava:
            self.server.contagens[self.path] = self.server.contagens.get(self.path, 0) + 1
        status, tipo, corpo = 200, "application/json; charset=utf-8", json_bytes(CATALOGO)
        rota = self.path
        atraso_corpo = False
        if rota == "/categorias":
            pass
        elif rota == "/cenarios/indisponivel":
            status, corpo = 503, json_bytes({"erro": "manutenção simulada"})
        elif rota == "/cenarios/json-invalido":
            corpo = b'{"versao": 1, "categorias": ['
        elif rota == "/cenarios/contrato-invalido":
            corpo = json_bytes({"versao": 1, "categorias": "Transporte"})
        elif rota == "/cenarios/tipo-incorreto":
            tipo = "text/html; charset=utf-8"
        elif rota == "/cenarios/sem-transporte":
            corpo = json_bytes({"versao": 1, "categorias": ["Alimentação", "Materiais"]})
        elif rota == "/cenarios/extra":
            corpo = json_bytes({"versao": 1, "categorias": CATALOGO["categorias"] + ["Livros"]})
        elif rota == "/cenarios/lenta":
            time.sleep(3)
        elif rota == "/cenarios/lenta-corpo":
            atraso_corpo = True
        elif rota == "/cenarios/redirecionamento":
            status = 302
        elif rota == "/cenarios/sem-conteudo":
            status, corpo = 204, b""
        elif rota == "/cenarios/chave-repetida":
            corpo = b'{"versao": 1, "versao": 1, "categorias": ["Transporte"]}'
        elif rota == "/cenarios/nao-finito":
            corpo = b'{"versao": NaN, "categorias": ["Transporte"]}'
        elif rota == "/cenarios/utf8-invalido":
            corpo = b'\xff'
        elif rota == "/cenarios/limite":
            corpo = corpo + b" " * (32768 - len(corpo))
        elif rota == "/cenarios/grande":
            corpo = corpo + b" " * (32769 - len(corpo))
        elif rota == "/cenarios/sem-tipo":
            tipo = None
        else:
            status, corpo = 404, json_bytes({"erro": "rota não encontrada"})
        try:
            self.send_response(status)
            if tipo is not None:
                self.send_header("Content-Type", tipo)
            if status == 302:
                self.send_header("Location", "/categorias")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            if atraso_corpo:
                time.sleep(3)
            self.wfile.write(corpo)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            # Esperado se o cliente desistir por timeout ou limite de tamanho.
            pass

    def do_POST(self):
        self.send_response(405)
        self.send_header("Allow", "GET")
        self.send_header("Content-Length", "0")
        self.end_headers()


def criar_servidor(porta=8765):
    return ServidorLocal(("127.0.0.1", porta))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API local de categorias — capítulo 5")
    parser.add_argument("--porta", type=int, default=8765)
    args = parser.parse_args()
    if not 1 <= args.porta <= 65535:
        parser.error("porta deve estar entre 1 e 65535")
    try:
        servidor = criar_servidor(args.porta)
    except OSError:
        print("Não foi possível abrir a porta. Confira se seu servidor já está em execução.")
        raise SystemExit(1)
    with servidor:
        print("API local em http://127.0.0.1:" + str(args.porta), flush=True)
        print("Encerre com Ctrl+C. Dados fictícios; nenhuma gravação.", flush=True)
        try:
            servidor.serve_forever(poll_interval=0.1)
        except KeyboardInterrupt:
            print("Servidor encerrado.")
