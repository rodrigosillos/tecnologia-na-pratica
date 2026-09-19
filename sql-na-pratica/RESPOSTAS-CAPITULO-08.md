# Capítulo 8 — Respostas do laboratório

Use a base inicial e competência de maio de 2026, exceto na comparação mensal, que inclui maio e junho. As soluções completas estão em `laboratorio/25_exercicios_capitulo_08.sql`. Todos os exemplos do capítulo apenas consultam dados.

## Exercício 1 — Três maiores faixas com empates

Use DENSE_RANK ordenado apenas por valor decrescente dentro da janela. Filtre faixa <= 3 na consulta externa; ordene a apresentação por valor decrescente e id crescente.

| id | valor | faixa |
| --- | --- | --- |
| 9 | 200.00 | 1 |
| 2 | 180.00 | 2 |
| 4 | 120.00 | 3 |
| 10 | 120.00 | 3 |

Três valores distintos produzem quatro despesas. ROW_NUMBER com limite 3 perderia uma despesa de 120.00. RANK coincide nessa amostra, mas não expressa a regra de contar faixas sem intervalos. Incluir id no ORDER BY de DENSE_RANK desfaz o empate de valor.

## Exercício 2 — Total antes do filtro de apresentação

Calcule SUM(valor) OVER (PARTITION BY usuario) na CTE que contém todas as despesas de maio. Só depois aplique valor >= 100.

| id | usuario | valor | total_mes |
| --- | --- | --- | --- |
| 2 | 1 | 180.00 | 455.00 |
| 4 | 1 | 120.00 | 455.00 |
| 9 | 2 | 200.00 | 320.00 |
| 10 | 2 | 120.00 | 320.00 |

A versão incorreta retirava as despesas de 45, 30 e 80 antes da janela. O total de Ana caía para 300.00; o de Bruno permanecia 320.00 por coincidência com o filtro.

## Conferências dos exemplos

- Sete despesas em maio, somando 775.00. Ana totaliza 455.00 e Bruno 320.00. Carla não tem linha de despesa.
- Mercado de Ana, id 2, corresponde a 39.56% do gasto dela; em relação ao total de todos os usuários, corresponde a 23.23%.
- As duas maiores despesas de cada usuário são IDs 2, 4, 9 e 10.
- Acumulados cronológicos de Ana: 180, 225, 255, 375 e 455, nos IDs 2, 3, 7, 4 e 5. Bruno: 200 e 320.
- Na comparação das molduras por valor, os IDs 4 e 10 recebem 395 na moldura padrão. Com ROWS e desempate por id, recebem 275 e 395.
- Junho: Ana totaliza 180.00, diferença de -275.00 para maio; Bruno totaliza 200.00, diferença de -120.00. Em maio, anterior e diferença são NULL no recorte.
- LAG busca a linha anterior disponível. Meses ausentes não são criados nem convertidos automaticamente em zero.

Os diagnósticos do arquivo 24 alteram uma regra por vez. Compare-os com as consultas corretas do arquivo 23 e com as soluções do arquivo 25. Não recarregue a base para repetir consultas.
