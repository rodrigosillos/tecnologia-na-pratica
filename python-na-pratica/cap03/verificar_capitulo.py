"""Verificador auxiliar do capítulo 3, sem dependências externas.

Executa apenas os arquivos locais deste pacote. Casos adicionais usam cópias
do código em memória, substituindo dados de entrada pela árvore sintática;
nenhum exemplo é reescrito. Não é um validador genérico de dados externos.
"""

import ast
import contextlib
import copy
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
RESULTADOS = []
AMBIENTE = os.environ.copy()
AMBIENTE["PYTHONIOENCODING"] = "utf-8"
AMBIENTE["PYTHON_COLORS"] = "0"
BASE = [
    {"id": "D001", "data": "2026-09-10", "descricao": "Café em reunião",
     "categoria": "Alimentação", "valor": "12.50"},
    {"id": "D002", "data": "2026-09-10", "descricao": "Corrida para visitar cliente",
     "categoria": "Transporte", "valor": "35.00"},
    {"id": "D003", "data": "2026-09-10", "descricao": "Cabo para o escritório",
     "categoria": "Materiais", "valor": "80.00"},
]


def registrar(nome, aprovado, evidencia):
    RESULTADOS.append({"nome": nome,
                       "status": "aprovado" if aprovado else "falhou",
                       "evidencia": evidencia})


def saida_resumo(qtd, total, categoria, qtd_categoria, subtotal):
    return [f"Despesas no período: {qtd}", f"Total em reais: {total}",
            f"Categoria: {categoria}", f"Despesas da categoria: {qtd_categoria}",
            f"Subtotal em reais: {subtotal}"]


def executar_arquivo(arquivo, esperado=None, erro_esperado=None):
    try:
        processo = subprocess.run(
            [sys.executable, str(RAIZ / arquivo)], cwd=RAIZ, env=AMBIENTE,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=15, check=False,
        )
        if erro_esperado:
            aprovado = (processo.returncode == 1 and not processo.stdout
                        and processo.stderr.splitlines()[-1].startswith(erro_esperado + ":"))
        else:
            aprovado = (processo.returncode == 0 and not processo.stderr
                        and processo.stdout.splitlines() == esperado)
        registrar(arquivo, aprovado, {"codigo_saida": processo.returncode,
                  "saida": processo.stdout, "erro": processo.stderr,
                  "erro_intencional": erro_esperado is not None,
                  "esperado": erro_esperado or esperado})
    except Exception as exc:
        registrar(arquivo, False, {"erro_verificacao": f"{type(exc).__name__}: {exc}"})


def executar_variacao(arquivo, substituicoes):
    caminho = RAIZ / arquivo
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    encontrados = set()
    for instrucao in arvore.body:
        if isinstance(instrucao, ast.Assign) and len(instrucao.targets) == 1:
            alvo = instrucao.targets[0]
            if isinstance(alvo, ast.Name) and alvo.id in substituicoes:
                instrucao.value = ast.parse(repr(substituicoes[alvo.id]), mode="eval").body
                encontrados.add(alvo.id)
    if encontrados != set(substituicoes):
        raise ValueError(f"Entradas não localizadas: {set(substituicoes) - encontrados}")
    ast.fix_missing_locations(arvore)
    nomes = {"__name__": "__main__", "__file__": str(caminho)}
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        exec(compile(arvore, str(caminho), "exec"), nomes)
    return nomes, saida.getvalue().splitlines()


def conferir_resumo(nome, dados, quantidade, total, qtd_categoria, subtotal,
                    categoria="Transporte"):
    esperado = saida_resumo(quantidade, total, categoria, qtd_categoria, subtotal)
    try:
        nomes, linhas = executar_variacao("10_resumo.py", {
            "despesas": dados, "categoria_alvo": categoria,
        })
        tipos_corretos = (isinstance(nomes["total"], Decimal)
                         and isinstance(nomes["total_categoria"], Decimal)
                         and type(nomes["quantidade"]) is int
                         and type(nomes["quantidade_categoria"]) is int)
        aprovado = (linhas == esperado and tipos_corretos
                    and nomes["despesas"] == dados
                    and nomes["total"] == Decimal(total)
                    and nomes["total_categoria"] == Decimal(subtotal))
        registrar(nome, aprovado, {"saida": linhas, "esperado": esperado,
                  "origem_preservada": nomes["despesas"] == dados,
                  "tipos_corretos": tipos_corretos})
    except Exception as exc:
        registrar(nome, False, {"erro_verificacao": f"{type(exc).__name__}: {exc}"})


def conferir_propostas(nome, propostas, linhas_esperadas):
    try:
        nomes, linhas = executar_variacao("solucoes/desafio.py", {"propostas": propostas})
        registrar(nome, linhas == linhas_esperadas and nomes["propostas"] == propostas,
                  {"saida": linhas, "esperado": linhas_esperadas,
                   "origem_preservada": nomes["propostas"] == propostas})
    except Exception as exc:
        registrar(nome, False, {"erro_verificacao": f"{type(exc).__name__}: {exc}"})


def main():
    registrar("python_3_14", sys.version_info[:2] == (3, 14), platform.python_version())
    registrar("ambiente_virtual", sys.prefix != sys.base_prefix,
              {"prefix": sys.prefix, "base_prefix": sys.base_prefix})
    exemplos = {
        "01_tipos.py": ["Café em reunião", "Quantidade: 3", "Revisada: False",
                        "Data ausente: None", "<class 'str'>", "<class 'int'>", "<class 'bool'>"],
        "02_conversoes.py": ["31", "4", "3 despesas", "True"],
        "03_dinheiro.py": ["0.30000000000000004", "0.30", "False", "Subtotal em reais: 47.50"],
        "04_datas.py": ["2026-09-10", "Ano: 2026", "No período: True"],
        "05_listas.py": ["Quantidade: 3", "Primeiro: D001", "Segundo: D002",
                         "D002 presente: True", "Quantidade no exemplo: 4"],
        "06_dicionarios.py": ["D001", "Café em reunião", "Campo valor presente: True",
                              "Valor em reais: 12.50"],
        "07_condicoes.py": ["Pendente: informar a data"],
        "08_repeticoes.py": ["Acumulado: 12.50", "Acumulado: 47.50", "Acumulado: 127.50",
                             "Quantidade: 3", "Total em reais: 127.50"],
        "09_selecao.py": ["IDs selecionados: ['D002']", "Registros de origem: 3"],
        "10_resumo.py": saida_resumo(3, "127.50", "Transporte", 1, "35.00"),
        "solucoes/exercicio_01.py": saida_resumo(3, "127.50", "Materiais", 1, "80.00"),
        "solucoes/exercicio_02.py": saida_resumo(0, "0.00", "Transporte", 0, "0.00"),
        "solucoes/exercicio_03.py": saida_resumo(2, "92.50", "Transporte", 0, "0.00"),
        "desafio_base.py": ["Implemente a triagem de propostas antes de abrir a solução"],
        "solucoes/desafio.py": ["P001 Pendente: informar a data", "P002 Pendente: informar a data",
                               "Propostas pendentes: 2", "Nenhuma proposta foi importada"],
    }
    for arquivo, esperado in exemplos.items():
        executar_arquivo(arquivo, esperado)
    for arquivo, erro in [
        ("data_impossivel.py", "ValueError"),
        ("chave_ausente.py", "KeyError"),
        ("texto_com_inteiro.py", "TypeError"),
    ]:
        executar_arquivo("erros_intencionais/" + arquivo, erro_esperado=erro)

    # Os totais esperados abaixo são casos de referência fixos, não recalculados
    # repetindo o algoritmo do exemplo que está sendo verificado.
    conferir_resumo("base_e_tipos_monetarios", BASE, 3, "127.50", 1, "35.00")
    conferir_resumo("lista_vazia", [], 0, "0.00", 0, "0.00")
    for data, qtd, total, qtd_cat, subtotal, nome in [
        ("2026-08-31", 2, "92.50", 0, "0.00", "antes_do_inicio"),
        ("2026-09-01", 3, "127.50", 1, "35.00", "inicio_inclusivo"),
        ("2026-09-30", 3, "127.50", 1, "35.00", "ultimo_dia_do_mes"),
        ("2026-10-01", 2, "92.50", 0, "0.00", "fim_exclusivo"),
    ]:
        dados = copy.deepcopy(BASE)
        dados[1]["data"] = data
        conferir_resumo(nome, dados, qtd, total, qtd_cat, subtotal)
    dados = copy.deepcopy(BASE)
    for despesa in dados:
        despesa["data"] = "2026-10-02"
    conferir_resumo("nenhum_registro_no_periodo", dados, 0, "0.00", 0, "0.00")
    dados = copy.deepcopy(BASE)
    for despesa, valor in zip(dados, ["0.10", "0.20", "0.30"]):
        despesa["valor"] = valor
    conferir_resumo("soma_decimal_sem_passagem_por_float", dados, 3, "0.60", 1, "0.20")
    dados = copy.deepcopy(BASE)
    dados[0]["categoria"] = "Transporte"
    conferir_resumo("duas_despesas_na_categoria", dados, 3, "127.50", 2, "47.50")
    conferir_resumo("ordem_invertida", list(reversed(BASE)), 3, "127.50", 1, "35.00")
    conferir_resumo("categoria_sem_ocorrencias", BASE, 3, "127.50", 0, "0.00", "Hospedagem")
    dados = copy.deepcopy(BASE)
    dados.append({"id": "D004", "data": "2026-09-11", "descricao": "Pasta para documentos",
                  "categoria": "Materiais", "valor": "20.00"})
    conferir_resumo("quarta_despesa_sem_contagem_fixa", dados, 4, "147.50", 1, "35.00")

    proposta = {"id_proposta": "P001", "data": "2026-09-10", "revisada": False}
    conferir_propostas("proposta_com_data_sem_revisao", [proposta], [
        "P001 Pendente: revisão humana", "Propostas pendentes: 1", "Nenhuma proposta foi importada"])
    proposta["revisada"] = True
    conferir_propostas("proposta_revisada_nao_e_importada", [proposta], [
        "P001 Seguir para validação completa", "Propostas pendentes: 0", "Nenhuma proposta foi importada"])
    proposta["data"] = None
    conferir_propostas("data_ausente_prevalece_sobre_revisao", [proposta], [
        "P001 Pendente: informar a data", "Propostas pendentes: 1", "Nenhuma proposta foi importada"])
    conferir_propostas("nenhuma_proposta", [], [
        "Propostas pendentes: 0", "Nenhuma proposta foi importada"])

    instante = datetime.now(timezone.utc)
    fontes = {arquivo.relative_to(RAIZ).as_posix(): hashlib.sha256(arquivo.read_bytes()).hexdigest()
              for arquivo in sorted(RAIZ.rglob("*.py"))
              if "resultados" not in arquivo.relative_to(RAIZ).parts}
    falhas = sum(item["status"] == "falhou" for item in RESULTADOS)
    relatorio = {
        "capitulo": 3, "revisao": "R01", "data_utc": instante.isoformat(),
        "sistema": platform.system(), "arquitetura": platform.machine(),
        "python": platform.python_version(), "interpretador": sys.executable,
        "escopo": "arquivos Python locais e variações em memória; não valida editor, PowerShell, importação ou API",
        "status": "aprovado" if falhas == 0 else "reprovado",
        "total": len(RESULTADOS), "aprovados": len(RESULTADOS) - falhas, "falhas": falhas,
        "sha256_fontes": fontes, "verificacoes": RESULTADOS,
    }
    pasta = RAIZ / "resultados"
    pasta.mkdir(exist_ok=True)
    destino = pasta / f"relatorio-cap03-{instante:%Y%m%dT%H%M%S%fZ}.json"
    destino.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Status: {relatorio['status']}")
    print(f"Verificações: {relatorio['aprovados']}/{relatorio['total']}")
    print(f"Sistema: {relatorio['sistema']} | Python: {relatorio['python']}")
    print(f"Relatório: {destino}")
    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
