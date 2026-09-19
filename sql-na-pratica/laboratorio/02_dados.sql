-- Dados inteiramente ficticios, em reais. Execute uma vez apos 01_estrutura.sql.
BEGIN;
SET LOCAL search_path TO sql_pratica, public;
INSERT INTO usuarios (id, nome) VALUES (1, 'Ana'), (2, 'Bruno'), (3, 'Carla');
INSERT INTO contas (id, usuario_id, nome) VALUES
    (1, 1, 'Conta corrente'), (2, 1, 'Carteira'),
    (3, 2, 'Conta corrente'), (4, 3, 'Conta corrente');
INSERT INTO categorias (id, nome, tipo) VALUES
    (1, 'Salario', 'receita'), (2, 'Mercado', 'despesa'),
    (3, 'Transporte', 'despesa'), (4, 'Internet', 'despesa'),
    (5, 'Saude', 'despesa'), (6, 'Lazer', 'despesa'),
    (7, 'Freelance', 'receita');
INSERT INTO lancamentos
    (id, conta_id, categoria_id, tipo, descricao, valor,
     data_competencia, data_liquidacao)
VALUES
    (1, 1, 1, 'receita', 'Salario', 3000.00, '2026-05-05', '2026-05-05'),
    (2, 1, 2, 'despesa', 'Mercado', 180.00, '2026-05-10', '2026-05-10'),
    (3, 1, 3, 'despesa', 'Transporte', 45.00, '2026-05-12', '2026-05-12'),
    (4, 1, 4, 'despesa', 'Internet', 120.00, '2026-05-15', NULL),
    (5, 1, 5, 'despesa', 'Farmacia', 80.00, '2026-05-20', '2026-05-20'),
    (6, 1, 2, 'despesa', 'Mercado', 180.00, '2026-06-01', '2026-06-01'),
    (7, 2, 3, 'despesa', 'Transporte', 30.00, '2026-05-13', '2026-05-13'),
    (8, 3, 1, 'receita', 'Salario', 2500.00, '2026-05-05', '2026-05-05'),
    (9, 3, 2, 'despesa', 'Mercado', 200.00, '2026-05-11', '2026-05-11'),
    (10, 3, 4, 'despesa', 'Internet', 120.00, '2026-05-16', '2026-06-02'),
    (11, 3, 2, 'despesa', 'Mercado', 200.00, '2026-06-01', NULL),
    (12, 2, 7, 'receita', 'Freelance', 300.00, '2026-05-22', '2026-05-22');
INSERT INTO orcamentos
    (id, usuario_id, categoria_id, mes_referencia, valor_limite)
VALUES
    (1, 1, 2, '2026-05-01', 300.00),
    (2, 1, 2, '2026-06-01', 150.00),
    (3, 1, 4, '2026-05-01', 100.00),
    (4, 2, 2, '2026-05-01', 250.00),
    (5, 3, 6, '2026-05-01', 100.00);

-- Os IDs fixos tornam os exemplos repetiveis. Ajuste das sequencias para novos INSERTs.
SELECT setval(pg_get_serial_sequence('usuarios', 'id'), (SELECT MAX(id) FROM usuarios));
SELECT setval(pg_get_serial_sequence('contas', 'id'), (SELECT MAX(id) FROM contas));
SELECT setval(pg_get_serial_sequence('categorias', 'id'), (SELECT MAX(id) FROM categorias));
SELECT setval(pg_get_serial_sequence('lancamentos', 'id'), (SELECT MAX(id) FROM lancamentos));
SELECT setval(pg_get_serial_sequence('orcamentos', 'id'), (SELECT MAX(id) FROM orcamentos));
COMMIT;
