"""Configuração local e abertura da conexão; não registra senha."""
import getpass
import os
import psycopg


def configuracao_banco(senha=None):
    porta = int(os.environ.get("PYTHON_PRATICA_PG_PORTA", "5432"))
    if not 1 <= porta <= 65535:
        raise ValueError("Porta PostgreSQL inválida")
    if senha is None:
        senha = getpass.getpass("Senha de python_leitor: ")
    if not senha:
        raise ValueError("Informe a senha definida para python_leitor")
    return {"host": "127.0.0.1", "port": porta,
            "dbname": "python_na_pratica", "user": "python_leitor", "password": senha}


def conectar(config):
    if (config.get("host") != "127.0.0.1" or config.get("dbname") != "python_na_pratica"
            or config.get("user") != "python_leitor"):
        raise ValueError("Use apenas o banco e o usuário exclusivos do laboratório")
    con = psycopg.connect(**config, connect_timeout=3, application_name="tnp_cap12",
                          options="-c statement_timeout=5000 -c lock_timeout=2000")
    if not 180000 <= con.info.server_version < 190000:
        con.close()
        raise ValueError("Este laboratório requer PostgreSQL 18; registre o patch executado")
    return con
