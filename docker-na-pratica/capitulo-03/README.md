# Capítulo 3 — Imagens: de onde os containers nascem

Material correspondente ao manuscrito R02 de **Docker na Prática**, de Rodrigo Sillos.

## Antes de começar

Nginx e hello-world dos capítulos anteriores. Nenhum fonte da aplicação nesta etapa.

Abra o terminal em: **Terminal do host.** (em relação a esta pasta de capítulo).

A tag temporária tnp-web:lab muda de Nginx para hello-world de propósito. Não a use como versão permanente da aplicação.

## Como usar os arquivos

Leia a seção de retomada no livro. Compare os arquivos da etapa e o estado real do Engine antes de criar, iniciar, remover ou reconstruir recursos. Abrir outra pasta não cria outro ambiente Docker. Os nomes usuais do livro podem colidir com objetos de outra sessão.

[Trechos e comandos para consulta](TRECHOS_E_COMANDOS.md) conserva os blocos da R02 com os títulos das seções e lembretes de contexto. Não execute a coletânea inteira. Algumas instruções são alternativas, falhas deliberadas ou modelos incompletos.

Este capítulo utiliza imagens oficiais obtidas durante a prática. Não há um Dockerfile do catálogo a executar aqui; não inventamos uma aplicação para preencher a pasta.

## Estado a preservar ao concluir

Retirar containers/referências temporárias do exercício; preservar as imagens oficiais.

Esse é um estado **esperado**, não um registro de que você já executou o capítulo. Confira a identificação dos recursos e os dados antes de avançar. Os arquivos de estado fornecidos nas etapas posteriores detalham a retomada; eles não são scripts.

## Segurança e limites

Trabalhe somente no laboratório identificado. Não use dados pessoais, credenciais reais, `prune` ou remoção global para ajustar a máquina ao exemplo. Um erro exige ler a mensagem e confirmar o alvo, não elevar permissões por tentativa.

O servidor de anotações continua sendo um exemplo didático de arquivo JSON e não coordena múltiplos gravadores. Confira o [guia de uso](../LEIA_PRIMEIRO.md) e o [mapa das etapas](../MAPA_DOS_CAPITULOS.md).
