-- SQL na Pratica | Capitulo 11 | PostgreSQL 18
-- Dados ficticios; use apenas o banco de estudos.
-- Execute UMA instrucao por vez e confira o resultado.
-- Mantenha a mesma aba e conexao, com autocommit ativado.
-- Execute o arquivo 34 antes deste. O exercicio 2 termina com ROLLBACK.
-- Nao substitua ROLLBACK por COMMIT. Nao execute o arquivo inteiro.

-- Etapa 1: ex1_candidata
-- ERRO DE LOGICA INTENCIONAL: consulta candidata para diagnostico.
SELECT u.id, u.nome,
       COALESCE(SUM(DISTINCT l.valor), 0) AS total
FROM usuarios AS u
LEFT JOIN contas AS c ON c.usuario_id = u.id
LEFT JOIN lancamentos AS l
  ON l.conta_id = c.id
 AND l.tipo = 'despesa'
 AND l.data_competencia >= DATE '2026-05-01'
 AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id, u.nome
ORDER BY u.id;

-- Etapa 2: ex1_contraexemplo
SELECT COUNT(*) AS quantidade,
       SUM(valor) AS total,
       SUM(DISTINCT valor) AS total_distinto
FROM (VALUES
    (900001, 180.00),
    (900002, 180.00)
) AS despesas(id, valor);

-- Etapa 3: ex1_solucao
SELECT u.id, u.nome,
       COALESCE(SUM(l.valor), 0) AS total
FROM usuarios AS u
LEFT JOIN contas AS c ON c.usuario_id = u.id
LEFT JOIN lancamentos AS l
  ON l.conta_id = c.id
 AND l.tipo = 'despesa'
 AND l.data_competencia >= DATE '2026-05-01'
 AND l.data_competencia < DATE '2026-06-01'
GROUP BY u.id, u.nome
ORDER BY u.id;

-- Etapa 4: ex2_filtro_amplo
SELECT id, conta_id, valor, data_liquidacao
FROM lancamentos
WHERE categoria_id = 4
ORDER BY id;

-- Etapa 5: ex2_alvo
SELECT id, conta_id, valor, data_liquidacao
FROM lancamentos
WHERE id = 4
  AND conta_id = 1
  AND tipo = 'despesa'
  AND valor = 120.00
  AND data_liquidacao IS NULL;

-- Etapa 6: ex2_inicio
-- Continue apenas se ex2_alvo retornou ID 4, conta 1, 120.00 e data nula.
BEGIN;

-- Etapa 7: ex2_atualizacao
-- Retorno esperado: UMA linha, ID 4, valor anterior 120.00, novo 125.00.
-- Se falhar ou divergir, pare, investigue e execute ROLLBACK na mesma conexao.
UPDATE lancamentos
SET valor = 125.00
WHERE id = 4
  AND conta_id = 1
  AND tipo = 'despesa'
  AND valor = 120.00
  AND data_liquidacao IS NULL
RETURNING id,
          old.valor AS valor_anterior,
          new.valor AS valor_novo;

-- Etapa 8: ex2_conferencia
SELECT id, valor, data_liquidacao
FROM lancamentos
WHERE id IN (4, 10)
ORDER BY id;

-- Etapa 9: ex2_desfazer
ROLLBACK;

-- Etapa 10: ex2_conferencia_final
SELECT id, valor, data_liquidacao
FROM lancamentos
WHERE id IN (4, 10)
ORDER BY id;

-- Etapa 11: conferencia_final
SELECT COUNT(*) AS lancamentos_originais
FROM lancamentos;

