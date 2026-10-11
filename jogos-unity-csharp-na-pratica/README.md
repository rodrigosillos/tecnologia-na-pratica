# Jogos com Unity e C# na Prática

Material de apoio da coleção Tecnologia na Prática, de Rodrigo Sillos.
Versão candidata: **1.0.0-rc.1**. Editor de referência: **Unity 6000.3.15f1**.

Três projetos independentes: **Ruínas em Jogo**, **Arena das Ruínas** e **Caminho do Portal**.
O percurso principal utiliza Windows de 64 bits, renderização Built-in e backend Mono.
Input System 1.19.0, uGUI 2.0.0 e Test Framework 1.6.0 estão registrados nos projetos.

## Downloads da versão 1.0.0-rc.1

- [Projetos Unity completos](https://github.com/rodrigosillos/tecnologia-na-pratica/releases/download/jogos-unity-csharp-laboratorio-v1.0.0-rc.1/Jogos_Unity_CSharp_Tres_Projetos_RC1_L01.zip) — para estudar e modificar.
- [Três jogos para Windows](https://github.com/rodrigosillos/tecnologia-na-pratica/releases/download/jogos-unity-csharp-laboratorio-v1.0.0-rc.1/Jogos_Unity_CSharp_Tres_Windows_RC1_L01.zip) — para jogar sem o Editor.
- [Página desta versão](https://github.com/rodrigosillos/tecnologia-na-pratica/releases/tag/jogos-unity-csharp-laboratorio-v1.0.0-rc.1) — arquivos e SHA-256.

Revisão documental **L01**: aplica as permissões aprovadas pelo autor; código, cenas, recursos e binários preservam a versão tecnicamente verificada. Esta é uma pré-release; os limites dos testes estão em VALIDACAO.json.

## Comece aqui

1. Extraia o pacote de projetos completamente. Não misture as pastas Assets dos três jogos.
2. No Unity Hub, use Add project from disk e escolha 01-QuebraBlocos, 02-Arena ou 03-Plataforma.
3. Abra com a versão indicada e uma licença Unity aplicável. A primeira abertura pode precisar de internet para restaurar pacotes e demora mais que as seguintes.
4. Abra a cena indicada abaixo, aguarde a compilação e pressione Play.
5. Para experimentar sem o Editor, extraia o pacote Windows e execute o jogo dentro de sua pasta completa.

| Projeto | Cena inicial | Comandos principais |
|---|---|---|
| 01-QuebraBlocos | Assets/Scenes/QuebraBlocos.unity | A/D ou setas; Espaço lança; Esc pausa |
| 02-Arena | Assets/Scenes/Arena.unity | WASD ou setas; mouse mira e dispara; Esc pausa |
| 03-Plataforma | Assets/Scenes/Fase1.unity | A/D ou setas; Espaço salta; J ou clique dispara; Esc pausa |

Os menus aceitam mouse ou setas e Enter. O jogo pausa ao perder o foco.
A plataforma salva progresso localmente; Nova partida pede confirmação antes de substituir a campanha.

## Estudar e modificar

Leia [GUIA_MARCOS.md](GUIA_MARCOS.md) e faça experiências em uma cópia.
Os menus Tecnologia na Pratica recriam cenas e dados nos caminhos de referência e podem substituir alterações feitas neles.
O material contém a versão integrada dos projetos e um roteiro de marcos de estudo; não contém um histórico artificial de versões intermediárias.
Os arquivos .meta fazem parte do projeto. Library, Temp, Logs e UserSettings são regeneráveis e foram excluídos.

## Verificações

Os testes do Unity ficam em Assets/Tests. Use Window > General > Test Runner e a aba apropriada.
O argumento --tnp-verificar, seguido de uma pasta de resultados, ativa um roteiro especial nos executáveis. Sem esse argumento, a partida é normal.
Consulte VALIDACAO.json para ambiente, resultados e limites. Transições controladas, comandos simulados e avaliação humana são evidências diferentes.

## Permissões de uso

Código e documentação originais: [MIT](LICENSE), com [escopo definido](LICENCA_ESCOPO.md).
Ilustrações: [uso e redistribuição nos jogos do leitor, inclusive comerciais, com crédito](LICENCA_RECURSOS.md).

## Origem e escopo

Consulte CREDITOS.md. Código e recursos originais do laboratório estão separados do texto comercial do livro e da capa.
O pacote não inclui o Editor Unity. Dependências e arquivos de suporte do motor mantêm as condições de seus titulares.
Este volume é independente, sem patrocínio ou certificação da Unity, Microsoft, Amazon ou itch.io.
