"""Verificador auxiliar do capítulo 4. Sem rede e sem dependências externas.

Os testes usam entradas de referência, arquivos temporários e processos locais.
O único resultado persistente novo é o relatório em resultados/.
"""
import sys
sys.dont_write_bytecode = True

import contextlib
import copy
import hashlib
import io
import json
import os
import platform
import subprocess
import tempfile
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from aplicacao import executar
from arquivos import LIMITE_BYTES, ler_csv, ler_json, ler_texto
from calculos import somar_valores
from regras import converter_data, converter_valor, validar_despesa, validar_lote

RAIZ = Path(__file__).resolve().parent
RESULTADOS = []
BASE = [
    {"id":"D001","data":"2026-09-10","descricao":"Café em reunião","categoria":"Alimentação","valor":"12.50"},
    {"id":"D002","data":"2026-09-10","descricao":"Corrida para visitar cliente","categoria":"Transporte","valor":"35.00"},
    {"id":"D003","data":"2026-09-10","descricao":"Cabo para o escritório","categoria":"Materiais","valor":"80.00"},
]
AMBIENTE = os.environ.copy()
AMBIENTE["PYTHONIOENCODING"] = "utf-8"
AMBIENTE["PYTHONDONTWRITEBYTECODE"] = "1"
AMBIENTE["PYTHON_COLORS"] = "0"


def exigir(condicao, mensagem):
    if not condicao:
        raise AssertionError(mensagem)


def igual(obtido, esperado):
    exigir(obtido == esperado, f"Esperado {esperado!r}; obtido {obtido!r}")


def rejeita(funcao, valor, mensagem, tipo=ValueError):
    try:
        funcao(valor)
    except tipo as erro:
        exigir(mensagem in str(erro), f"Diagnóstico diferente: {erro}")
        return {"excecao": type(erro).__name__, "mensagem": str(erro)}
    raise AssertionError("Entrada inválida foi aceita")


def caso(nome, funcao):
    try:
        evidencia = funcao()
    except Exception as erro:
        RESULTADOS.append({"nome":nome, "status":"falhou",
                           "evidencia":f"{type(erro).__name__}: {erro}"})
    else:
        RESULTADOS.append({"nome":nome, "status":"aprovado",
                           "evidencia":evidencia or "expectativa conferida"})


def conferir_programa(nome, linhas, codigo=0, pasta=None):
    processo = subprocess.run([sys.executable,str(RAIZ/nome)], cwd=pasta or RAIZ,
        env=AMBIENTE,capture_output=True,text=True,encoding="utf-8",timeout=20)
    igual(processo.returncode,codigo)
    igual(processo.stdout.splitlines(),linhas)
    igual(processo.stderr,"")
    return {"codigo_saida":processo.returncode,"saida":processo.stdout}


def linhas_resumo(qtd=3,total="127.50",repetidos=0):
    return ["Lote validado em memória",f"Despesas únicas: {qtd}",
            f"Repetições idênticas: {repetidos}",f"Total em reais: {total}",
            "Nenhuma despesa foi gravada"]


def caso_registro(campo, valor, mensagem):
    entrada = copy.deepcopy(BASE[0])
    entrada[campo] = valor
    return rejeita(validar_despesa,entrada,mensagem)


def resumo(dados, quantidade, total, repetidos=0):
    original = copy.deepcopy(dados)
    resultado = validar_lote(dados)
    igual(resultado["erros"],[])
    igual(len(resultado["despesas"]),quantidade)
    igual(resultado["repetidos"],repetidos)
    valores = [d["valor"] for d in resultado["despesas"]]
    exigir(all(isinstance(v,Decimal) for v in valores),"Tipo monetário incorreto")
    igual(somar_valores(valores),Decimal(total))
    igual(dados,original)
    return {"despesas":quantidade,"total":total,"repetidos":repetidos,"origem_preservada":True}


def bloqueado(dados, trechos):
    original = copy.deepcopy(dados)
    resultado = validar_lote(dados)
    igual(resultado["despesas"],[])
    igual(len(resultado["erros"]),len(trechos))
    for mensagem,trecho in zip(resultado["erros"],trechos):
        exigir(trecho in mensagem,mensagem)
    igual(dados,original)
    return {"despesas_devolvidas":0,"diagnosticos":resultado["erros"],"origem_preservada":True}


def executar_capturado(caminho, codigo, trecho):
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        retorno = executar(caminho)
    igual(retorno,codigo)
    exigir(trecho in saida.getvalue(),saida.getvalue())
    if codigo != 0:
        exigir("Total em reais:" not in saida.getvalue(),"Falha apresentou total parcial")
    return {"codigo_saida":retorno,"saida":saida.getvalue()}


def main():
    fontes_iniciais = inventario()
    caso("ambiente_python_3_14",lambda:igual(sys.version_info[:2],(3,14)))
    caso("ambiente_virtual",lambda:exigir(sys.prefix!=sys.base_prefix,"Fora da .venv"))
    saidas = {
        "01_funcoes.py":(["Total em reais: 127.50","Lista vazia: 0.00"],0),
        "02_objetos.py":(["É Decimal: True","É finito: True","É texto: False"],0),
        "03_importacao_escopo.py":(["Calculado: 127.50","Outra chamada: 127.50","Variável externa: 999.00"],0),
        "04_tratar_erro.py":(["Entrada rejeitada: valor: deve ser maior que zero","Conferência encerrada"],0),
        "05_ler_csv.py":(["Registros lidos, ainda sem validação: 3","Primeiro valor: 12.50","Valor ainda é texto: True"],0),
        "06_ler_json.py":(["Registros lidos, ainda sem validação: 3","Primeiro valor: 12.50","Valor ainda é texto: True"],0),
        "07_resumo_csv.py":(linhas_resumo(),0),
        "08_resumo_json.py":(linhas_resumo(),0),
        "09_lote_invalido.py":(["Lote bloqueado","Registro 2: data: dia, mês ou ano impossível",
            "Registro 3: valor: use 1 a 7 dígitos, ponto e 2 casas decimais","Nenhuma despesa foi gravada"],1),
        "10_primeiro_teste.py":(["Valor zero rejeitado como esperado","Verificações da regra: 2/2"],0),
        "solucao_exercicio_02.py":(linhas_resumo(repetidos=1),0),
        "solucao_exercicio_03.py":(["Lote bloqueado","Registro 1: valor: informe texto, por exemplo 12.50",
                                   "Nenhuma despesa foi gravada"],1),
        "solucao_desafio.py":(["Lote bloqueado","Registro 4: id: conteúdo conflitante para D002",
                              "Nenhuma despesa foi gravada"],1),
    }
    for nome,(linhas,codigo) in saidas.items():
        caso("programa_"+nome,lambda n=nome,l=linhas,c=codigo:conferir_programa(n,l,c))

    for entrada,esperado in [("0.01","0.01"),("12.50","12.50"),("00012.50","12.50"),("9999999.99","9999999.99")]:
        caso("valor_aceito_"+entrada,lambda e=entrada,s=esperado:igual(converter_valor(e),Decimal(s)))
    valores_ruins = ["0.00","-1.00","+1.00","12,50","12.5","12.500","12.505","1e2","NaN","sNaN",
                    "Infinity","-Infinity","10000000.00"," 12.50","12.50 ","12.50\n","R$ 12.50","１.00","",None,12.5,True]
    for numero,entrada in enumerate(valores_ruins,1):
        caso(f"valor_rejeitado_{numero:02d}",lambda e=entrada:rejeita(converter_valor,e,"valor:"))
    for entrada,esperado in [("2026-09-10",date(2026,9,10)),("2024-02-29",date(2024,2,29))]:
        caso("data_aceita_"+entrada,lambda e=entrada,s=esperado:igual(converter_data(e),s))
    for numero,entrada in enumerate(["2026-02-29","2026-02-30","2026-13-01","0000-01-01","20260910",
                                     "2026-W37-4","2026-9-10","2026-09-10T00:00:00"," 2026-09-10",None],1):
        caso(f"data_rejeitada_{numero:02d}",lambda e=entrada:rejeita(converter_data,e,"data:"))

    caso("csv_base_canonica",lambda:igual(ler_csv(RAIZ/"dados/validas.csv"),BASE))
    caso("json_base_canonica",lambda:igual(ler_json(RAIZ/"dados/validas.json"),BASE))
    def normalizacao():
        dados = copy.deepcopy(BASE[0])
        novo = validar_despesa(dados)
        igual(novo["data"],date(2026,9,10))
        igual(novo["valor"],Decimal("12.50"))
        exigir(novo is not dados,"Registro original reutilizado")
        igual(dados,BASE[0])
    caso("normalizacao_sem_alterar_origem",normalizacao)
    for numero,(campo,valor,mensagem) in enumerate([
        ("id","D01","id:"),("id","d001","id:"),("id","D123456789","id:"),("id","D00A","id:"),
        ("descricao","","descricao:"),("descricao","   ","descricao:"),("descricao","x"*121,"descricao:"),
        ("descricao",None,"descricao:"),("categoria","Hospedagem","categoria:"),
        ("categoria"," Transporte ","categoria:"),("categoria",True,"categoria:")],1):
        caso(f"campo_rejeitado_{numero:02d}",lambda c=campo,v=valor,m=mensagem:caso_registro(c,v,m))
    ausente=copy.deepcopy(BASE[0]); del ausente["valor"]
    extra=copy.deepcopy(BASE[0]); extra["aprovada"]=True
    caso("campo_ausente",lambda:rejeita(validar_despesa,ausente,"campos ausentes ou extras"))
    caso("campo_extra",lambda:rejeita(validar_despesa,extra,"campos ausentes ou extras"))
    caso("registro_nao_objeto",lambda:rejeita(validar_despesa,[],"esperado um objeto"))
    caso("lote_nao_lista",lambda:rejeita(validar_lote,{},"esperado uma lista"))
    caso("lote_vazio",lambda:resumo([],0,"0.00"))
    caso("lote_base",lambda:resumo(BASE,3,"127.50"))
    caso("lote_repeticao_identica",lambda:resumo(BASE+[copy.deepcopy(BASE[1])],3,"127.50",1))
    caso("lote_ordem_invertida",lambda:resumo(list(reversed(BASE)),3,"127.50"))
    diferente=copy.deepcopy(BASE[1]); diferente["valor"]="53.00"
    caso("conflito_bloqueia_lote_completo",lambda:bloqueado(BASE+[diferente],["Registro 4: id: conteúdo conflitante"]))
    caso("dois_erros_diagnosticados",lambda:bloqueado(ler_csv(RAIZ/"dados/invalidas.csv"),["Registro 2: data:","Registro 3: valor:"]))
    corrigido=ler_json(RAIZ/"dados/desafio.json"); corrigido[3]["valor"]="35.00"
    caso("desafio_corrigido",lambda:resumo(corrigido,4,"147.50",1))
    zeros=copy.deepcopy(BASE[0]); zeros["valor"]="00012.50"
    caso("repeticao_com_mesmo_valor_normalizado",lambda:resumo(BASE+[zeros],3,"127.50",1))
    caso("limite_1000_registros",lambda:resumo([BASE[0]]*1000,1,"12.50",999))
    caso("limite_1001_registros",lambda:rejeita(validar_lote,[BASE[0]]*1001,"limite de 1000"))

    with tempfile.TemporaryDirectory(prefix="cap04 leitura ") as temporario:
        pasta=Path(temporario)
        def arquivo(nome,conteudo):
            destino=pasta/nome
            destino.write_bytes(conteudo if isinstance(conteudo,bytes) else conteudo.encode("utf-8"))
            return destino
        csv_base=(RAIZ/"dados/validas.csv").read_text(encoding="utf-8")
        json_base=(RAIZ/"dados/validas.json").read_text(encoding="utf-8")
        bomcsv=arquivo("bom.csv",b"\xef\xbb\xbf"+csv_base.encode("utf-8"))
        bomjson=arquivo("bom.json",b"\xef\xbb\xbf"+json_base.encode("utf-8"))
        caso("csv_utf8_bom",lambda:igual(ler_csv(bomcsv),BASE))
        caso("json_utf8_bom",lambda:igual(ler_json(bomjson),BASE))
        crlf=arquivo("windows.csv",csv_base.replace("\n","\r\n"))
        caso("csv_quebras_crlf",lambda:igual(ler_csv(crlf),BASE))
        caso("csv_descricao_entre_aspas",lambda:igual(ler_csv(RAIZ/"dados/descricao_com_virgula.csv")[0]["descricao"],"Café, reunião com cliente"))
        vazio_csv=arquivo("vazio.csv","id,data,descricao,categoria,valor\n")
        vazio_json=arquivo("vazio.json","[]")
        caso("csv_apenas_cabecalho",lambda:igual(ler_csv(vazio_csv),[]))
        caso("json_lista_vazia",lambda:igual(ler_json(vazio_json),[]))
        for nome,texto,mensagem in [
            ("separador.csv",csv_base.replace(",",";"),"cabeçalho"),
            ("cabecalho_repetido.csv","id,id,descricao,categoria,valor\n","cabeçalho"),
            ("sem_conteudo.csv","","cabeçalho"),
            ("aspas.csv",'id,data,descricao,categoria,valor\nD001,2026-09-10,"texto,Alimentação,12.50\n',"estrutura inválida"),
        ]:
            caminho=arquivo(nome,texto)
            caso(nome,lambda c=caminho,m=mensagem:rejeita(ler_csv,c,m))
        coluna_extra=arquivo("coluna_extra.csv",csv_base.replace("12.50\n","12.50,extra\n"))
        coluna_ausente=arquivo("coluna_ausente.csv",csv_base.replace(",12.50\n","\n"))
        caso("csv_coluna_extra",lambda:bloqueado(ler_csv(coluna_extra),["Registro 1: registro:"]))
        caso("csv_coluna_ausente",lambda:bloqueado(ler_csv(coluna_ausente),["Registro 1: valor:"]))
        for nome,texto,mensagem in [
            ("raiz.json",'{}',"raiz deve ser uma lista"),
            ("malformado.json",'[{',"estrutura inválida"),
            ("sem_conteudo.json",'',"estrutura inválida"),
            ("chave_repetida.json",'[{"id":"D001","id":"D002"}]',"chave repetida"),
            ("nan.json",'[NaN]',"constante não permitida"),
            ("infinito.json",'[Infinity]',"constante não permitida"),
        ]:
            caminho=arquivo(nome,texto)
            caso(nome,lambda c=caminho,m=mensagem:rejeita(ler_json,c,m))
        profundo=arquivo("profundo.json",'['*2000+']'*2000)
        def rejeitar_registro_aninhado():
            # A profundidade tolerada pelo decodificador varia; estrutura JSON
            # interpretável continua sujeita ao contrato de registros planos.
            try:
                dados=ler_json(profundo)
            except ValueError as erro:
                exigir("aninhamento excessivo" in str(erro),str(erro))
                return {"rejeicao":"leitura","mensagem":str(erro)}
            resultado=validar_lote(dados)
            igual(resultado["despesas"],[])
            igual(resultado["erros"],["Registro 1: registro: esperado um objeto com campos"])
            return {"rejeicao":"validação de registros","diagnosticos":resultado["erros"]}
        caso("json_aninhado_nao_e_despesa",rejeitar_registro_aninhado)
        caso("json_numero_no_campo_monetario",lambda:bloqueado(ler_json(RAIZ/"dados/valor_numerico.json"),["Registro 1: valor:"]))
        grande=arquivo("grande.json",b" "*(LIMITE_BYTES+1))
        limite=arquivo("limite.json",b"[]"+b" "*(LIMITE_BYTES-2))
        caso("arquivo_1mib_aceito",lambda:igual(ler_json(limite),[]))
        caso("arquivo_acima_1mib",lambda:rejeita(ler_json,grande,"limite de 1 MiB"))
        muitos_json=arquivo("muitos.json",json.dumps([BASE[0]]*1001))
        muitos_csv=arquivo("muitos.csv",csv_base.splitlines()[0]+"\n"+(csv_base.splitlines()[1]+"\n")*1001)
        caso("json_acima_1000",lambda:rejeita(ler_json,muitos_json,"limite de 1000"))
        caso("csv_acima_1000",lambda:rejeita(ler_csv,muitos_csv,"limite de 1000"))
        ruim_utf8=arquivo("codificacao.json",b"\xff\xfe")
        caso("utf8_invalido",lambda:rejeita(ler_texto,ruim_utf8,"",UnicodeDecodeError))
        caso("aplicacao_arquivo_ausente",lambda:executar_capturado(pasta/"nao_existe.csv",1,"Falha de entrada:"))
        caso("aplicacao_formato_nao_suportado",lambda:executar_capturado(pasta/"qualquer.txt",1,"use extensão .csv ou .json"))
        caso("aplicacao_json_malformado",lambda:executar_capturado(pasta/"malformado.json",1,"JSON: estrutura inválida"))
        caso("aplicacao_codificacao_invalida",lambda:executar_capturado(ruim_utf8,1,"Falha de entrada:"))
        caso("pasta_atual_diferente_e_caminho_com_espacos",lambda:conferir_programa("07_resumo_csv.py",linhas_resumo(),pasta=pasta))

    def erro_intencional():
        p=subprocess.run([sys.executable,str(RAIZ/"erros_intencionais/data_impossivel.py")],
                         capture_output=True,encoding="utf-8",env=AMBIENTE,timeout=15)
        igual(p.returncode,1)
        igual(p.stdout,"")
        exigir(p.stderr.splitlines()[-1].startswith("ValueError:"),p.stderr)
        return {"codigo_saida":1,"erro_intencional":"ValueError"}
    caso("excecao_nao_tratada_intencional",erro_intencional)
    caso("fontes_e_dados_preservados",lambda:igual(inventario(),fontes_iniciais))
    return salvar(fontes_iniciais)


def inventario():
    return {p.relative_to(RAIZ).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(RAIZ.rglob("*")) if p.is_file()
            and (p.suffix==".py" or p.parent==RAIZ/"dados")
            and "__pycache__" not in p.parts and "resultados" not in p.parts}


def salvar(fontes):
    agora=datetime.now(timezone.utc)
    falhas=sum(v["status"]=="falhou" for v in RESULTADOS)
    relatorio={"capitulo":4,"revisao":"R01","data_utc":agora.isoformat(),
        "sistema":platform.system(),"arquitetura":platform.machine(),
        "python":platform.python_version(),"interpretador":sys.executable,
        "escopo":"regras, arquivos CSV/JSON, programas locais; não valida editor, console visual, banco ou API",
        "status":"aprovado" if falhas==0 else "reprovado","total":len(RESULTADOS),
        "aprovados":len(RESULTADOS)-falhas,"falhas":falhas,
        "sha256_fontes_e_dados":fontes,"verificacoes":RESULTADOS}
    pasta=RAIZ/"resultados"; pasta.mkdir(exist_ok=True)
    destino=pasta/f"relatorio-cap04-{agora:%Y%m%dT%H%M%S%fZ}.json"
    destino.write_text(json.dumps(relatorio,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Status: {relatorio['status']}")
    print(f"Verificações: {relatorio['aprovados']}/{relatorio['total']}")
    print(f"Sistema: {relatorio['sistema']} | Python: {relatorio['python']}")
    print(f"Relatório: {destino}")
    return 0 if falhas==0 else 1


if __name__=="__main__":
    raise SystemExit(main())
