# Registro Windows — capítulo 5 R01

**Estado inicial: pendente. Preencher somente depois da execução.**

- Data e fuso:
- Windows (versão informada pelo sistema):
- PowerShell/terminal e versão:
- Python executado:
- Caminho da `.venv`:
- Interpretador do editor confirmado:
- Instalação das dependências concluída:
- `pip check`:
- Porta do servidor manual:
- Arquivo JSON do verificador:
- Status e contagem do verificador:
- Saída do verificador:
- Integridade dos arquivos:

| Execução | Esperado | Observado / saída |
| --- | --- | --- |
| 01 — observação | 200; versão 1; três categorias / 0 | |
| 02 — contrato | três nomes / 0 | |
| 03 — catálogo com servidor | catálogo aceito / 0 | |
| 04 — CSV | 3 únicas; 0 repetidas; 127.50 / 0 | |
| 05 — JSON | igual ao CSV / 0 | |
| 06 — 404 | HTTP 404 / 1 | |
| 06 — 503 | HTTP 503 / 1 | |
| 06 — json | JSON inválido / 1 | |
| 06 — contrato | catálogo fora do contrato / 1 | |
| 06 — tipo | Content-Type rejeitado / 1 | |
| 06 — lenta | tempo limite / 1 | |
| 06 — redirect | 302 rejeitado / 1 | |
| Solução exercício | registro 2 rejeitado; sem total / 1 | |
| Solução desafio | conflito D002 no registro 4; sem total / 1 | |
| 03 — servidor desligado | falha de comunicação / 1 | |

## Observações manuais

- Servidor iniciou e encerrou com Ctrl+C:
- Acentos no console (`Alimentação`, `Versão`, `Catálogo`):
- Acentos no JSON aberto no editor:
- Nenhum total exibido nos casos de falha:
- Ajustes de ambiente eventualmente necessários (descrever, sem credenciais):
- Pendências:

## Conclusão

- Homologação funcional: pendente / aprovada / reprovada
- Legibilidade visual no console: pendente / aprovada / problema identificado
- Evidências anexadas:
