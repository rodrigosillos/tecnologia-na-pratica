# Capítulo 8 — Docker Compose: a aplicação descrita em um arquivo

Material correspondente ao manuscrito R02 de **Docker na Prática**, de Rodrigo Sillos.

## Antes de começar

Containers manuais e imagens 1.4/entrada 1.0; volume original existente.

Abra o terminal em: **laboratorio** (em relação a esta pasta de capítulo).

A rede nova usa sublinhado; a anterior usava hífen. .env da raiz é interpolação e .env.cap08 é ambiente da aplicação. Nunca crie volume vazio para ocultar ausência do original.

## Como usar os arquivos

Leia a seção de retomada no livro. Compare os arquivos da etapa e o estado real do Engine antes de criar, iniciar, remover ou reconstruir recursos. Abrir outra pasta não cria outro ambiente Docker. Os nomes usuais do livro podem colidir com objetos de outra sessão.

[Trechos e comandos para consulta](TRECHOS_E_COMANDOS.md) conserva os blocos da R02 com os títulos das seções e lembretes de contexto. Não execute a coletânea inteira. Algumas instruções são alternativas, falhas deliberadas ou modelos incompletos.

A pasta `laboratorio` contém os arquivos de aplicação e configuração desta etapa. Imagens Docker, volumes, backups e dados produzidos pelo leitor não acompanham o pacote. Não sobrescreva a pasta em que você guarda anotações ou cópias de recuperação.

## Estado a preservar ao concluir

Projeto tnp-catalogo parado, serviços catalogo/entrada, rede tnp-catalogo_rede e mesmo volume externo; operação manual retirada após a prova.

Esse é um estado **esperado**, não um registro de que você já executou o capítulo. Confira a identificação dos recursos e os dados antes de avançar. Os arquivos de estado fornecidos nas etapas posteriores detalham a retomada; eles não são scripts.

## Segurança e limites

Trabalhe somente no laboratório identificado. Não use dados pessoais, credenciais reais, `prune` ou remoção global para ajustar a máquina ao exemplo. Um erro exige ler a mensagem e confirmar o alvo, não elevar permissões por tentativa.

O servidor de anotações continua sendo um exemplo didático de arquivo JSON e não coordena múltiplos gravadores. Confira o [guia de uso](../LEIA_PRIMEIRO.md) e o [mapa das etapas](../MAPA_DOS_CAPITULOS.md).
