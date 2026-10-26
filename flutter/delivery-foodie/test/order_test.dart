import 'package:flutter_test/flutter_test.dart';
import 'package:delivery_flutter/catalog.dart';
import 'package:delivery_flutter/order.dart';
import 'package:delivery_flutter/delivery_controller.dart';

void main() {
  test('Carrinho calcula quantidades, frete único e remoção em centavos', () {
    final c = DeliveryController();
    addTearDown(c.dispose);
    expect(c.total, 0);
    c.add(products.first);
    expect(c.total, 3480);
    c.changeQuantity(products.first, 1);
    expect(c.subtotal, 5980);
    expect(c.total, 6470);
    c.add(products[2]);
    expect(c.total, 7960);
    expect(c.deliveryFee, 490);
    c.changeQuantity(products.first, -2);
    c.changeQuantity(products[2], -1);
    expect(c.cartCount, 0);
    expect(c.total, 0);
    expect(money(6470), 'R\$ 64,70');
  });
  test('Pedido exige pagamento e só confirma uma vez; recibo é imutável', () {
    final c = DeliveryController();
    addTearDown(c.dispose);
    c.checkout();
    expect(c.stage, DeliveryStage.splash);
    c.add(products.first);
    c.changeQuantity(products.first, 1);
    c.checkout();
    c.confirm();
    expect(c.stage, DeliveryStage.checkout);
    expect(c.submittedOrders, 0);
    c.choosePayment(PaymentMethod.cardOnDelivery);
    c.confirm();
    c.confirm();
    c.changeQuantity(products.first, 1);
    expect(c.cartCount, 2);
    c.tick(1);
    c.confirm();
    c.tick(1);
    expect(c.stage, DeliveryStage.confirmation);
    expect(c.submittedOrders, 1);
    final receipt = c.order!;
    expect(receipt.total, 6470);
    expect(receipt.items.single.quantity, 2);
    expect(() => receipt.items.clear(), throwsUnsupportedError);
    c.home(newOrder: true);
    expect(c.total, 0);
    expect(receipt.total, 6470);
  });
  test('Login local valida dados e categoria filtra o catálogo', () {
    final c = DeliveryController();
    addTearDown(c.dispose);
    c.tick(2);
    c.login();
    expect(c.loginBusy, false);
    expect(c.loginError, isNotNull);
    c.email.text = 'demo@example.com';
    c.password.text = 'demo1234';
    c.login();
    c.tick(.6);
    expect(c.stage, DeliveryStage.home);
    c.chooseCategory(4);
    expect(c.shownProducts.single.id, 'sushi');
  });
}
