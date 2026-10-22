# Voltio — recarga com recibo animado

Estudo de interface em Flutter e Dart, em português do Brasil. Acompanhe uma recarga demonstrativa, selecione um método de pagamento e imprima um recibo animado.

## Executar
Ambiente usado: Flutter 3.41.4 / Dart 3.11.1.
```sh
flutter pub get
flutter run
flutter test test/flow_test.dart
```
Use um dispositivo Android ou emulador configurado. Não houve validação de execução em iOS.

## Código
- `lib/charge_flow.dart`: estados, valores em centavos e pagamento simulado.
- `lib/charging_view.dart`: telas e interações.
- `lib/receipt_view.dart`: animação do recibo.
- `lib/mac_showcase.dart`: apresentação visual opcional.

Não há backend, pagamentos reais, credenciais bancárias ou integração com carregadores. Nomes e dados de transação são demonstrativos. O APK de desenvolvimento não é uma publicação em loja.

O vídeo utiliza uma composição visual de desktop, não uma gravação do simulador iOS. O Dock com ícones da Apple foi excluído deste pacote público. O app e suas interações são preservados. O roteiro de captura dependente da máquina de produção também foi excluído.

Consulte THIRD_PARTY_NOTICES.txt antes de reutilizar os recursos. O código original desta pasta está sob licença MIT (Copyright 2026 Rodrigo Sillos); o escopo está em LICENCA_ESCOPO.md. Fontes e demais dependências de terceiros mantêm as próprias licenças.
