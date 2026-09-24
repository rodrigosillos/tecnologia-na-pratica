# Mapa dos capítulos e da continuidade

Base: manuscrito consolidado R02. Os estados abaixo são expectativas após o percurso, não capturas de uma execução.

| Capítulo | Aplicação e saída esperada | Pasta do terminal |
|---|---|---|
| [01](capitulo-01/README.md) | hello-world imprime e termina; observar imagem, container parado e processo separadamente. | `Terminal do host.` |
| [02](capitulo-02/README.md) | Remover somente web-lab e web-pratica após as provas; conservar nginx:alpine. | `Terminal do host.` |
| [03](capitulo-03/README.md) | Retirar containers/referências temporárias do exercício; preservar as imagens oficiais. | `Terminal do host.` |
| [04](capitulo-04/README.md) | catalogo-web parado com tnp-catalogo:1.1; Edição 2; três temas; imagens 1.0 e 1.1 preservadas. | `laboratorio/catalogo-estudos` |
| [05](capitulo-05/README.md) | catalogo-web parado em 1.3, .env.cap05, porta 8084:3000, Edição 2 e três temas. | `laboratorio/catalogo-estudos` |
| [06](capitulo-06/README.md) | catalogo-web parado em 1.4, Edição 3, três temas e volume tnp-catalogo-dados em /app/dados; conservar anotações e backups. | `laboratorio/catalogo-estudos` |
| [07](capitulo-07/README.md) | catalogo-web e catalogo-entrada parados; rede manual tnp-catalogo-rede; somente Nginx publica 8084. | `laboratorio` |
| [08](capitulo-08/README.md) | Projeto tnp-catalogo parado, serviços catalogo/entrada, rede tnp-catalogo_rede e mesmo volume externo; operação manual retirada após a prova. | `laboratorio` |
| [09](capitulo-09/README.md) | Catálogo 1.5, Edição 3/três temas, entrada 1.0, controles aplicados, volume preservado e conjunto parado. | `laboratorio` |
| [10](capitulo-10/README.md) | Caminho de sucesso: 1.6/Edição 4/quatro temas no principal, dados originais, 1.5 preservada para retorno e serviços parados. | `laboratorio` |

## Três distinções que não podem desaparecer

Edição da página e tag da imagem não são a mesma coisa: 1.5 continua em Edição 3. A rede manual `tnp-catalogo-rede` é diferente da rede Compose `tnp-catalogo_rede`. Retornar a imagem 1.5 não restaura automaticamente um backup nem apaga anotações novas.

## Retomada

Não há restauração automática de estados apenas por copiar esta pasta. Volumes e imagens permanecem no Engine. Leia a entrada de cada capítulo antes de continuar e preserve suas substituições conscientes de nomes ou portas. No caminho alternativo de retorno do capítulo 10, mantenha `.env.retorno` selecionado; executar a definição padrão voltaria a selecionar 1.6.
