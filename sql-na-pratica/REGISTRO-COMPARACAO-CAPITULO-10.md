# Registro da comparação — Capítulo 10

Preencha com observações da sua execução. Não há um tempo universal esperado.

- Data e versão do PostgreSQL:
- Cliente usado e sistema operacional:
- Quantidade de linhas da carga (esperado 100000):
- Consulta principal (conta 42, maio de 2026):
- Resultado esperado: 31 linhas e total 3379.00.

| Observação | Antes do índice | Depois do índice |
| --- | --- | --- |
| Nós do plano | | |
| Condições em Index Cond | | |
| Condições em Filter | | |
| Linhas reais no nó de leitura e loops | | |
| Linhas removidas por filtro | | |
| Buffers do nó superior, separados por rótulo | | |
| Execution Time da primeira execução | | |
| Execution Time de três repetições | | |
| Quantidade e total conferidos | | |

Anexe ou cole os dois planos completos abaixo. Não some contagens inclusivas dos nós. Registre diferenças de plano em vez de forçar o uso do índice. Se a configuração, a consulta ou os dados mudarem, registre outra experiência.

## Plano antes

Cole aqui a saída de plano_antes do arquivo 31.

## Plano depois

Cole aqui a saída de plano_depois do arquivo 31.

## Conclusão

Qual trabalho foi reduzido? Quais resultados provam que a resposta permaneceu correta? Há uma diferença de tempo consistente nas repetições? Que limite do ambiente impede generalizar essa observação?

## Exercícios

- EXTRACT: quais condições usaram o índice e quais filtraram depois?
- BETWEEN: qual linha extra apareceu e por que sua inclusão é incorreta?
