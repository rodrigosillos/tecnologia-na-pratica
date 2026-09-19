# Versão do laboratório

**1.0.0-rc.1 — 19 de setembro de 2026**

Primeira versão candidata do pacote completo de apoio a **SQL na Prática**, de Rodrigo Sillos. A publicação final depende das verificações indicadas abaixo.

## O que mudou desde a revisão 0.13

- README reorganizado para orientar a primeira execução.
- Preparação no pgAdmin, roteiro de execução, resultados esperados e solução de problemas em arquivos próprios.
- Respostas dos capítulos 1 e 2 acrescentadas, completando o conjunto de soluções comentadas por capítulo.
- Arquivo 08 esclarece a configuração de Auto commit e Auto rollback on error. As instruções SQL dos 42 arquivos permanecem iguais.
- Conferência por SHA-256 adicionada para identificar exatamente esta versão.
- Notas históricas de testes substituídas por um estado de validação consolidado.

## Validação realizada

Os 42 scripts foram executados instrução por instrução em **PGlite 0.5.8, com PostgreSQL 18.3 incorporado**. Passaram 329 instruções e 57 grupos de conferência. Os três erros previstos — 23505, 23514 e 25P02 — ocorreram nos pontos documentados e foram recuperados.

Foram comparadas as saídas de 310 instruções com a referência integrada anterior. Dezesseis instruções de identificação do ambiente ou planos não tiveram saída comparada como valor fixo; os três erros intencionais tiveram seus códigos conferidos separadamente. Planos e tempos variam conforme o ambiente.

Ao terminar, as cinco tabelas e os índices originais estavam preservados. A view do capítulo 7 permanecia criada. A tabela temporária de desempenho foi removida. A sequência de lançamentos avançou uma unidade devido a um INSERT desfeito; esse avanço é esperado.

## Verificações ainda pendentes

| Verificação | Estado |
| --- | --- |
| Instalação nativa e autenticação no PostgreSQL 18 | Pendente |
| Execução do percurso em servidor nativo, com duas conexões | Pendente |
| Uso real da interface do pgAdmin | Pendente; instruções conferidas na documentação 9.18 |
| Instalação em cada sistema operacional descrito no capítulo 2 | Pendente de execução por plataforma |
| Alternativa Docker | YAML revisado; execução e obtenção da imagem pendentes |
| Endereço público estável e teste do download | Repositório criado; release final `v1.0.0` ainda pendente |

O banco interno do teste incorporado se chama `postgres`. No percurso do leitor, o banco é `sql_na_pratica`. As verificações de uma modalidade não comprovam as demais.

Endereço do repositório: https://github.com/rodrigosillos/tecnologia-na-pratica  
Pasta deste laboratório: https://github.com/rodrigosillos/tecnologia-na-pratica/tree/main/sql-na-pratica  

A release pública final com o ZIP `sql-na-pratica-laboratorio-v1.0.0.zip` só deve ser publicada após a homologação nativa e o roteiro do pgAdmin. Até lá, trate este material como **versão candidata**.
