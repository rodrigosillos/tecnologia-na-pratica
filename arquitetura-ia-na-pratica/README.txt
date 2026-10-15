ARQUITETURA DE IA NA PRÁTICA / AI ARCHITECTURE IN PRACTICE
Rodrigo Sillos | Tecnologia na Prática
Companion labs - source snapshot: complete book R04, 2026-10-15

PORTUGUÊS
Este pacote reúne 18 laboratórios, um por capítulo. Eles compartilham
uma implementação entre os dois idiomas, com guias PT/EN e dados bilíngues.
Não são dois cursos duplicados. Alguns cenários em inglês têm pontos de entrada
próprios; siga sempre o guia do capítulo no idioma escolhido.
Use Python 3.11 ou superior para o percurso inteiro. A validação de origem usou
Python 3.12.14. Apenas biblioteca padrão; não instale dependências aleatórias.
Não são necessárias credenciais nem chamadas a APIs pagas de modelos.
O capítulo 3 usa HTTP local em 127.0.0.1; permita loopback ao testar.
Abra um terminal dentro do laboratorio do capítulo, leia o guia e execute:
  python -m unittest discover -s .
Não junte módulos de capítulos diferentes nem execute todos a partir da raiz.
Os dados e falhas são sintéticos. O código é didático, não uma aplicação
certificada para produção. A suíte do capítulo 18 tem 669 testes cumulativos;
não some as contagens dos capítulos como testes distintos.

ENGLISH
This package contains 18 chapter-specific lab snapshots. The implementation is
shared across languages, with PT/EN guides and bilingual fixtures. Some English
scenarios have dedicated entry points; follow the chapter's English guide.
Use Python 3.11 or later for the complete course (source validation: 3.12.14).
Only the standard library is required. No model API credentials or paid calls.
Chapter 3 serves HTTP on 127.0.0.1 only; allow loopback when running its tests.
Open a terminal inside a chapter's laboratorio directory, read its guide, then:
  python -m unittest discover -s .
Do not merge modules or run every snapshot from the repository root.
Data and faults are synthetic. These educational labs do not certify production
readiness. Chapter 18 contains 669 cumulative tests, not 669 new tests.

CHAPTER GUIDES / GUIAS DOS CAPÍTULOS

01  01_Piloto
PT: laboratorios/01_Piloto/laboratorio/LEIA-ME-PT.txt
EN: laboratorios/01_Piloto/laboratorio/README-EN.txt

02  02_Dependencia_LLM
PT: laboratorios/02_Dependencia_LLM/laboratorio/LEIAME_PT.txt
EN: laboratorios/02_Dependencia_LLM/laboratorio/README_EN.txt

03  03_Arquitetura_Minima
PT: laboratorios/03_Arquitetura_Minima/laboratorio/LEIAME_PT.txt
EN: laboratorios/03_Arquitetura_Minima/laboratorio/README_EN.txt

04  04_Avaliacao
PT: laboratorios/04_Avaliacao/laboratorio/LEIAME_PT.txt
EN: laboratorios/04_Avaliacao/laboratorio/README_EN.txt

05  05_Dados_Versoes_Permissoes
PT: laboratorios/05_Dados_Versoes_Permissoes/laboratorio/LEIAME_PT.txt
EN: laboratorios/05_Dados_Versoes_Permissoes/laboratorio/ENGLISH_EDITION_R04.txt

06  06_Ingestao_Recuperavel
PT: laboratorios/06_Ingestao_Recuperavel/laboratorio/LEIAME_PT.txt
EN: laboratorios/06_Ingestao_Recuperavel/laboratorio/README_EN.txt

07  07_Recuperacao_Hibrida
PT: laboratorios/07_Recuperacao_Hibrida/laboratorio/LEIAME_PT.txt
EN: laboratorios/07_Recuperacao_Hibrida/laboratorio/ENGLISH_EDITION_R04.txt

08  08_Contratos_Saida
PT: laboratorios/08_Contratos_Saida/laboratorio/LEIAME_PT.txt
EN: laboratorios/08_Contratos_Saida/laboratorio/ENGLISH_EDITION_R04.txt

09  09_Prazos_Retries_Circuit_Breakers
PT: laboratorios/09_Prazos_Retries_Circuit_Breakers/laboratorio/LEIAME_PT.txt
EN: laboratorios/09_Prazos_Retries_Circuit_Breakers/laboratorio/README_EN.txt

10  10_Trabalhos_Assincronos
PT: laboratorios/10_Trabalhos_Assincronos/laboratorio/LEIAME_PT.txt
EN: laboratorios/10_Trabalhos_Assincronos/laboratorio/README_EN.txt

11  11_Roteamento_Fallback
PT: laboratorios/11_Roteamento_Fallback/laboratorio/LEIAME_PT.txt
EN: laboratorios/11_Roteamento_Fallback/laboratorio/README_EN.txt

12  12_Cache_Limites_Custo
PT: laboratorios/12_Cache_Limites_Custo/laboratorio/LEIAME_PT.txt
EN: laboratorios/12_Cache_Limites_Custo/laboratorio/README_EN.txt

13  13_Observabilidade
PT: laboratorios/13_Observabilidade/laboratorio/LEIAME_PT.txt
EN: laboratorios/13_Observabilidade/laboratorio/README_EN.txt

14  14_Fluxo_Workflow_Agente
PT: laboratorios/14_Fluxo_Workflow_Agente/laboratorio/LEIAME_PT.txt
EN: laboratorios/14_Fluxo_Workflow_Agente/laboratorio/README_EN.txt

15  15_Acoes_Aprovacao
PT: laboratorios/15_Acoes_Aprovacao/laboratorio/LEIAME_PT.txt
EN: laboratorios/15_Acoes_Aprovacao/laboratorio/README_EN.txt

16  16_Seguranca_Alem_Prompt
PT: laboratorios/16_Seguranca_Alem_Prompt/laboratorio/LEIAME_PT.txt
EN: laboratorios/16_Seguranca_Alem_Prompt/laboratorio/README_EN.txt

17  17_Entrega_Migracoes_Recuperacao
PT: laboratorios/17_Entrega_Migracoes_Recuperacao/laboratorio/LEIAME_PT.txt
EN: laboratorios/17_Entrega_Migracoes_Recuperacao/laboratorio/README_EN.txt

18  18_Ensaio_Producao
PT: laboratorios/18_Ensaio_Producao/laboratorio/LEIAME_PT.txt
EN: laboratorios/18_Ensaio_Producao/laboratorio/README_EN.txt

EDITION NOTES
English corrections from R04 are included. Source filenames intentionally
remain stable across languages. This package does not contain the book
manuscript, EPUB, PDF, KPF, covers, credentials, or payment information.
