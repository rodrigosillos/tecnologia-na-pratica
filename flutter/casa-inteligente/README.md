# Casa inteligente em Flutter

Uma demonstração do **Tecnologia na Prática**, criada por Rodrigo Sillos com Flutter + Dart. Interface em português, ilustração da sala desenhada em código e iluminação que acompanha os controles.

## Experimente

1. Ligue a luminária da sala.
2. Ajuste a intensidade e a temperatura de cor.
3. Toque em **Salvar cena** e escolha **Cinema**.
4. Apague a luz e toque no cartão **Cinema** para recuperar os ajustes.

A cena é guardada em memória durante a sessão. Ela não persiste após fechar o aplicativo. O controle é simulado, sem conexão com lâmpadas, conta, servidor ou serviço de IA.

## Executar

Validado com Flutter 3.41.4 / Dart 3.11.1.

```sh
flutter pub get
flutter run -d chrome
```

Para Android, conecte um aparelho e execute `flutter run`. Os arquivos Android estão incluídos; compilação e teste em aparelho Android não foram realizados nesta entrega. Não há projeto iOS neste pacote.

Para repetir automaticamente a interação de 24 segundos:

```sh
flutter run -d chrome --dart-define=AUTO_DEMO=true
```

## Verificação

```sh
flutter analyze
flutter test
flutter build web
```

Os testes verificam salvamento independente dos controles, cancelamento, toques e arrastos reais, desligamento e recuperação da cena com os dois ajustes. O projeto foi analisado, testado e compilado para web.

## Código

| Arquivo | Função |
| --- | --- |
| `lib/room_painter.dart` | Sala e iluminação desenhadas no Flutter |
| `lib/home_view.dart` | Interface, controles e cursor da demonstração |
| `lib/light_controller.dart` | Estado local, ações e transições |
| `lib/scene.dart` | Cena salva; código exibido no vídeo |
| `test/interaction_test.dart` | Testes de estado e interação |

O vídeo utiliza uma composição visual de macOS, com o app à esquerda e o código à direita. Essa composição, seus ícones do Dock e os arquivos de mídia não estão incluídos aqui. O vídeo não representa uma captura real de Mac ou execução em simulador iOS. Os ícones de aplicativo gerados pelo modelo Flutter são recursos provisórios de desenvolvimento, não o logo do Tecnologia na Prática.

## Licença

Código e documentação originais sob [MIT](LICENSE), Copyright (c) 2026 Rodrigo Sillos, **somente nesta pasta `flutter/casa-inteligente`**. A licença não se estende ao restante do repositório. Veja [LICENCA_ESCOPO.md](LICENCA_ESCOPO.md) e [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt) para os recursos de terceiros.
