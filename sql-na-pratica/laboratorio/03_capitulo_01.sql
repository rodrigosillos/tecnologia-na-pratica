-- Preparacao: selecione o schema do laboratorio nesta sessao.
SET search_path TO sql_pratica, public;

-- Q1: recorte exibido no inicio do capitulo (6 linhas).
SELECT id, descricao, tipo, valor
FROM lancamentos
WHERE conta_id = 1
ORDER BY id;

-- Q2: resposta correta (IDs 2, 4 e 6).
SELECT id, descricao, valor
FROM lancamentos
WHERE conta_id = 1
  AND tipo = 'despesa'
  AND valor >= 100
ORDER BY id;

-- Q3: ERRO LOGICO INTENCIONAL. Omite o filtro do tipo e inclui o salario.
SELECT id, descricao, valor
FROM lancamentos
WHERE conta_id = 1
  AND valor >= 100
ORDER BY id;

-- Q4: resposta do exercicio 2 (IDs 2 e 6).
SELECT id, descricao, valor
FROM lancamentos
WHERE conta_id = 1
  AND tipo = 'despesa'
  AND valor >= 180
ORDER BY id;
