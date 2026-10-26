# Delivery Foodie em Flutter

Demonstração criada para Rodrigo Sillos / Tecnologia na Prática. Interface em português, verde com degradê suave, ilustrações 3D e fluxo completo de pedido local.

## Executar

Validado com Flutter 3.41.4 / Dart 3.11.1.

```sh
flutter pub get
flutter run -d chrome
```

Entre com um e-mail fictício, por exemplo `demo@example.com`, e uma senha de pelo menos quatro caracteres. Nenhuma autenticação externa é realizada. Escolha um produto, adicione ao carrinho, ajuste a quantidade, avance e selecione um pagamento antes de confirmar. O pedido aparece como Recebido com um resumo imutável. Para voltar ao catálogo e limpar o carrinho, toque em Voltar ao início.

Categorias, favoritos, quantidade, remoção de itens, endereço demonstrativo, pagamento e confirmação funcionam localmente. Os botões Google, Apple, cadastro e recuperação de senha explicam o caráter demonstrativo; não conectam contas. Nenhuma cobrança, envio a restaurante ou entrega real é feita. Os dados ficam apenas na memória da sessão. O prazo exibido é ilustrativo.

## Verificar

```sh
flutter analyze
flutter test
flutter build web
```

Os testes verificam cálculos em centavos, remoção de itens, pagamento obrigatório, prevenção de confirmação duplicada, recibo imutável e um pedido completo por toques e arrastos nos controles reais.

Para repetir a sequência de 30 segundos: `flutter run --dart-define=AUTO_DEMO=true`.

## Estrutura

- `lib/delivery_controller.dart`: estado, validação local, carrinho e roteiro.
- `lib/delivery_view.dart`: telas e controles.
- `lib/ui_kit.dart`: componentes, ilustrações e cursor da demonstração.
- `lib/catalog.dart`: catálogo fictício.
- `lib/order.dart`: modelos e cálculos exibidos no vídeo.
- `assets/art/`: entregador e atlas de alimentos gerados com image_gen, mais os prompts de origem.

Projeto aprovado para publicação em `flutter/delivery-foodie`, com plataformas web e Android. Web compilada; Android não compilado nem testado em aparelho. A moldura do desktop, os ícones do Dock e os vídeos não fazem parte deste pacote. A composição do vídeo não é uma captura de Mac nem execução em um simulador iOS.

## Licença e recursos

Código, documentação e recursos originais sob [MIT](LICENSE), Copyright (c) 2026 Rodrigo Sillos, somente em `flutter/delivery-foodie`, na medida dos direitos detidos pelo licenciante. Veja [LICENCA_ESCOPO.md](LICENCA_ESCOPO.md). Os recursos de terceiros preservam suas próprias licenças.

Consulte [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt). Os ícones de app do modelo Flutter são provisórios de desenvolvimento, não representam o logo aprovado do canal.
