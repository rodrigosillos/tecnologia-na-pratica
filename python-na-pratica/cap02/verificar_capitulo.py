"""Verificações auxiliares do capítulo 2; não é uma aula de sintaxe.

Executa somente exemplos locais do pacote e grava um relatório novo em
resultados/. Usa a biblioteca padrão e o interpretador que o iniciou.
Não instala dependências nem executa comandos de PowerShell.
"""

import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


RAIZ = Path(__file__).resolve().parent
RESULTADOS = []
AMBIENTE = os.environ.copy()
AMBIENTE["PYTHONIOENCODING"] = "utf-8"
AMBIENTE["PYTHON_COLORS"] = "0"


def registrar(nome, aprovado, evidencia):
    RESULTADOS.append({
        "nome": nome,
        "status": "aprovado" if aprovado else "falhou",
        "evidencia": evidencia,
    })


def executar(argumentos, pasta=RAIZ):
    return subprocess.run(
        [sys.executable, *argumentos],
        cwd=pasta,
        env=AMBIENTE,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=20,
        check=False,
    )


def conferir_programa(arquivo, quantidade):
    resultado = executar([str(RAIZ / arquivo)])
    esperado = [
        "Assistente de despesas",
        f"Registros previstos: {quantidade}",
        "IA: nenhuma chamada executada",
    ]
    registrar(
        arquivo,
        resultado.returncode == 0
        and resultado.stdout.splitlines() == esperado
        and not resultado.stderr,
        {"codigo_saida": resultado.returncode,
         "saida": resultado.stdout, "erro": resultado.stderr},
    )


def main():
    registrar("linha_python_3_14", sys.version_info[:2] == (3, 14),
              platform.python_version())
    registrar("ambiente_virtual", sys.prefix != sys.base_prefix,
              {"prefix": sys.prefix, "base_prefix": sys.base_prefix})

    pip = executar(["-m", "pip", "--version"])
    registrar("pip_do_interpretador", pip.returncode == 0
              and "(python 3.14)" in pip.stdout,
              {"codigo_saida": pip.returncode, "saida": pip.stdout,
               "erro": pip.stderr})

    conferir_programa("primeiro_programa.py", 3)
    conferir_programa("variacao_programa.py", 4)
    conferir_programa("solucoes/desafio.py", 5)

    diagnostico = executar([str(RAIZ / "diagnostico_ambiente.py")])
    esperado = [
        f"Versão: {platform.python_version()}",
        f"Interpretador: {sys.executable}",
        f"Pasta atual: {RAIZ}",
        f"Ambiente virtual: {sys.prefix != sys.base_prefix}",
    ]
    registrar("diagnostico_na_pasta_cap02", diagnostico.returncode == 0
              and diagnostico.stdout.splitlines() == esperado,
              {"codigo_saida": diagnostico.returncode,
               "saida": diagnostico.stdout, "erro": diagnostico.stderr})

    with tempfile.TemporaryDirectory(prefix="tnp-cap02-") as temporario:
        pasta = Path(temporario).resolve()
        ausente = executar(["primeiro_programa.py"], pasta)
        registrar("caminho_relativo_em_pasta_errada",
                  ausente.returncode == 2
                  and "can't open file" in ausente.stderr,
                  {"erro_intencional": True,
                   "codigo_saida": ausente.returncode,
                   "erro": ausente.stderr})

        absoluto = executar([str(RAIZ / "primeiro_programa.py")], pasta)
        registrar("arquivo_absoluto_em_outra_pasta",
                  absoluto.returncode == 0
                  and absoluto.stdout.splitlines() == [
                      "Assistente de despesas", "Registros previstos: 3",
                      "IA: nenhuma chamada executada"],
                  {"codigo_saida": absoluto.returncode,
                   "saida": absoluto.stdout, "erro": absoluto.stderr})

        outra_pasta = executar([str(RAIZ / "diagnostico_ambiente.py")], pasta)
        registrar("pasta_atual_difere_da_pasta_do_arquivo",
                  outra_pasta.returncode == 0
                  and f"Pasta atual: {pasta}" in outra_pasta.stdout.splitlines(),
                  {"codigo_saida": outra_pasta.returncode,
                   "saida": outra_pasta.stdout, "erro": outra_pasta.stderr})

    for arquivo, tipo in [
        ("erros_intencionais/aspas_incompletas.py", "SyntaxError"),
        ("erros_intencionais/nome_incorreto.py", "NameError"),
    ]:
        falha = executar([str(RAIZ / arquivo)])
        registrar(arquivo, falha.returncode == 1
                  and tipo in falha.stderr and not falha.stdout,
                  {"erro_intencional": True,
                   "codigo_saida": falha.returncode, "erro": falha.stderr})

    instante = datetime.now(timezone.utc)
    arquivos = {}
    for arquivo in sorted(RAIZ.rglob("*.py")):
        if "resultados" not in arquivo.relative_to(RAIZ).parts:
            arquivos[arquivo.relative_to(RAIZ).as_posix()] = (
                hashlib.sha256(arquivo.read_bytes()).hexdigest()
            )
    falhas = sum(item["status"] != "aprovado" for item in RESULTADOS)
    relatorio = {
        "capitulo": 2,
        "data_utc": instante.isoformat(),
        "sistema": platform.system(),
        "arquitetura": platform.machine(),
        "python": platform.python_version(),
        "interpretador": sys.executable,
        "escopo": "exemplos Python; não testa instalação, editor ou PowerShell",
        "codificacao_subprocessos": "PYTHONIOENCODING=utf-8",
        "status": "aprovado" if falhas == 0 else "reprovado",
        "total": len(RESULTADOS),
        "aprovados": len(RESULTADOS) - falhas,
        "falhas": falhas,
        "sha256_fontes": arquivos,
        "verificacoes": RESULTADOS,
    }
    destino = RAIZ / "resultados"
    destino.mkdir(exist_ok=True)
    arquivo_saida = destino / (
        f"relatorio-cap02-{instante:%Y%m%dT%H%M%S%fZ}.json"
    )
    arquivo_saida.write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Status: {relatorio['status']}")
    print(f"Verificações: {relatorio['aprovados']}/{relatorio['total']}")
    print(f"Sistema: {relatorio['sistema']} | Python: {relatorio['python']}")
    print(f"Relatório: {arquivo_saida}")
    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
