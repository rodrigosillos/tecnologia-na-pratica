import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:delivery_flutter/app.dart';
import 'package:delivery_flutter/delivery_controller.dart';
import 'package:delivery_flutter/ui_kit.dart';
import 'font_support.dart';

void main() {
  testWidgets('Pedido completo pelos controles reais da interface', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final c = DeliveryController();
    await loadFonts();
    await tester.runAsync(loadDeliveryArt);
    await tester.pumpWidget(DeliveryApp(controller: c));
    await tester.runAsync(
      () => precacheImage(
        const AssetImage('assets/art/courier.png'),
        tester.element(find.byType(DeliveryApp)),
      ),
    );
    Future<void> step([double dt = .4]) async {
      c.tick(dt);
      await tester.pump(Duration(milliseconds: (dt * 1000).round()));
      await tester.pump();
    }

    Future<void> tap(String key) async {
      await tester.tap(find.byKey(ValueKey(key)));
      await step();
    }

    await step(2);
    await step();
    await tester.enterText(
      find.byKey(const ValueKey('email-field')),
      'demo@example.com',
    );
    await tester.enterText(
      find.byKey(const ValueKey('password-field')),
      'demo1234',
    );
    await tap('login');
    await step(.3);
    await step();
    expect(c.stage, DeliveryStage.home);
    await tester.drag(
      find.byKey(const ValueKey('category-scroll')),
      const Offset(-145, 0),
    );
    await step();
    await tester.drag(
      find.byKey(const ValueKey('home-scroll')),
      const Offset(0, -490),
    );
    await step();
    await tester.ensureVisible(find.byKey(const ValueKey('product-burger')));
    await tester.pumpAndSettle();
    await tap('product-burger');
    expect(c.stage, DeliveryStage.detail);
    await tap('add-to-cart');
    expect(c.cartCount, 1);
    await tap('detail-cart');
    expect(c.stage, DeliveryStage.cart);
    await tap('plus-burger');
    expect(c.total, 6470);
    expect(find.text('R\$ 64,70'), findsOneWidget);
    await tap('checkout');
    expect(c.stage, DeliveryStage.checkout);
    await tap('confirm-order');
    expect(c.stage, DeliveryStage.checkout);
    await tap('pay-card');
    await tap('confirm-order');
    await step(.6);
    await step();
    expect(c.stage, DeliveryStage.confirmation);
    expect(c.order!.total, 6470);
    expect(c.submittedOrders, 1);
    await tap('order-details');
    await step();
    expect(c.detailsExpanded, true);
    expect(find.text('Cartão na entrega'), findsOneWidget);
    expect(tester.takeException(), isNull);
    await tap('new-order');
    expect(c.stage, DeliveryStage.home);
    expect(c.cartCount, 0);
    await tester.pumpWidget(const SizedBox.shrink());
    c.dispose();
  });
}
