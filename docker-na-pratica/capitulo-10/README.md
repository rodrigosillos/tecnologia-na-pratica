# Capítulo 10 — Projeto prático completo

Material correspondente ao manuscrito R02 de **Docker na Prática**, de Rodrigo Sillos.

## Antes de começar

Projeto principal do capítulo 9 parado com 1.5; imagem anterior, volume e dados preservados.

Abra o terminal em: **laboratorio** (em relação a esta pasta de capítulo).

Não comece pelo capítulo 10 em um Engine vazio esperando um ambiente completo. Compose exige volume externo; imagens não estão neste ZIP. A criação do volume de aceite é explícita e separada. Não promova as anotações de teste.

## Como usar os arquivos

Leia a seção de retomada no livro. Compare os arquivos da etapa e o estado real do Engine antes de criar, iniciar, remover ou reconstruir recursos. Abrir outra pasta não cria outro ambiente Docker. Os nomes usuais do livro podem colidir com objetos de outra sessão.

[Trechos e comandos para consulta](TRECHOS_E_COMANDOS.md) conserva os blocos da R02 com os títulos das seções e lembretes de contexto. Não execute a coletânea inteira. Algumas instruções são alternativas, falhas deliberadas ou modelos incompletos.

A pasta `laboratorio` contém os arquivos de aplicação e configuração desta etapa. Imagens Docker, volumes, backups e dados produzidos pelo leitor não acompanham o pacote. Não sobrescreva a pasta em que você guarda anotações ou cópias de recuperação.

## Estado a preservar ao concluir

Caminho de sucesso: 1.6/Edição 4/quatro temas no principal, dados originais, 1.5 preservada para retorno e serviços parados.

Esse é um estado **esperado**, não um registro de que você já executou o capítulo. Confira a identificação dos recursos e os dados antes de avançar. Os arquivos de estado fornecidos nas etapas posteriores detalham a retomada; eles não são scripts.

## Segurança e limites

Trabalhe somente no laboratório identificado. Não use dados pessoais, credenciais reais, `prune` ou remoção global para ajustar a máquina ao exemplo. Um erro exige ler a mensagem e confirmar o alvo, não elevar permissões por tentativa.

O servidor de anotações continua sendo um exemplo didático de arquivo JSON e não coordena múltiplos gravadores. Confira o [guia de uso](../LEIA_PRIMEIRO.md) e o [mapa das etapas](../MAPA_DOS_CAPITULOS.md).

## Quando o arquivo de anotações estiver cheio

Se já houver 100 anotações, não apague dados para forçar o teste de escrita. Registre essa prova como não concluída naquele conjunto. O pacote público não contém os executores internos mencionados na R02; uma prova adicional precisa de uma prática separada com dados fictícios, preservando o backup e o volume original. As provas de leitura, retorno e restauração não equivalem à escrita adicional.
