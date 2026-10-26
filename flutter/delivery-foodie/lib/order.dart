// Valores em centavos.
class OrderLine {
  const OrderLine({
    required this.name,
    required this.unitPrice,
    required this.quantity,
    required this.art,
  });
  final String name;
  final int unitPrice;
  final int quantity;
  final int art;
  int get subtotal =>
      unitPrice * quantity;
}

class DeliveryOrder {
  DeliveryOrder({
    required this.number,
    required List<OrderLine>
        items,
    required this.address,
    required this.payment,
    this.deliveryFee = 490,
  }) : items =
           List.unmodifiable(
             items,
           );
  final String number;
  final List<OrderLine>
      items;
  final String address;
  final String payment;
  final int deliveryFee;
  int get subtotal =>
      items.fold<int>(
        0,
        (sum, item) =>
            sum +
            item.subtotal,
      );

  int get total =>
      subtotal + deliveryFee;
}

String money(int cents) =>
    'R\$ ${cents ~/ 100},'
    '${(cents % 100).toString().padLeft(2, '0')}';
