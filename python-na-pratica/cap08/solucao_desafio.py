"""Uma categoria permitida e um trecho existente podem não combinar."""
from configuracao_ia import PASTA
from arquivos import ler_json
from contexto import origens, categorias
from validacao import analisar


if __name__ == "__main__":
    caso = next(c for c in ler_json(PASTA / "casos/erros.json") if c["nome"] == "categoria_sem_suporte")
    analise = analisar(caso["resposta"], origens()[caso["origem_id"]]["texto"], categorias())
    print("Estado técnico:", analise["estado"])
    print("Categoria sugerida:", analise["sugestao"]["categoria"])
    print("Trecho existente:", analise["sugestao"]["evidencias"]["categoria"])
    print("Decisão comentada: corrigir para Alimentação após conferir o comprovante.")
    print("Formato e trecho válidos não substituem a revisão do significado.")
