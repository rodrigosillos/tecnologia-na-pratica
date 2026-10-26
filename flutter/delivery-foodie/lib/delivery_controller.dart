import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'catalog.dart';
import 'order.dart';

enum DeliveryStage {
  splash,
  login,
  home,
  detail,
  cart,
  checkout,
  processing,
  confirmation,
}

enum PaymentMethod { cardOnDelivery, cash }

double smooth(double value) {
  final t = value.clamp(0.0, 1.0);
  return t * t * t * (10 + t * (-15 + 6 * t));
}

class DeliveryController extends ChangeNotifier {
  DeliveryStage stage = DeliveryStage.splash, previous = DeliveryStage.splash;
  double clock = 0, elapsed = 0, homeOffset = 0, categoryOffset = 0;
  bool demo = false,
      remember = true,
      loginBusy = false,
      detailsExpanded = false;
  bool showSaved = false;
  int selectedCategory = 0, selectedAddress = 0, navTab = 0;
  Product selected = products.first;
  final Map<String, int> cart = {};
  final Set<String> favorites = {};
  final email = TextEditingController();
  final password = TextEditingController();
  String? emailError;
  String? loginError;
  PaymentMethod? payment;
  DeliveryOrder? order;
  int submittedOrders = 0;
  double addFeedback = 0, quantityFeedback = 0, detailsProgress = 0;
  double _loginRemaining = 0, _submitRemaining = 0;

  static const addresses = ['Rua Exemplo, 123', 'Avenida Modelo, 456'];
  String get address => addresses[selectedAddress];
  String get paymentLabel => payment == PaymentMethod.cardOnDelivery
      ? 'Cartão na entrega'
      : 'Dinheiro';
  int get cartCount => cart.values.fold(0, (a, b) => a + b);
  int get subtotal =>
      products.fold(0, (sum, p) => sum + p.price * (cart[p.id] ?? 0));
  int get deliveryFee => cartCount == 0 ? 0 : 490;
  int get total => subtotal + deliveryFee;
  bool get canConfirm =>
      cartCount > 0 && payment != null && stage == DeliveryStage.checkout;
  List<Product> get shownProducts => products
      .where(
        (p) =>
            (selectedCategory == 0 ||
                p.category == categories[selectedCategory]) &&
            (!showSaved || favorites.contains(p.id)),
      )
      .toList();

  void go(DeliveryStage next) {
    if (stage == next) return;
    previous = stage;
    stage = next;
    elapsed = 0;
    notifyListeners();
  }

  void tick(double dt) {
    if (demo) return;
    clock += dt;
    elapsed += dt;
    addFeedback = math.max(0, addFeedback - dt);
    quantityFeedback = math.max(0, quantityFeedback - dt);
    detailsProgress +=
        ((detailsExpanded ? 1.0 : 0.0) - detailsProgress) *
        (1 - math.exp(-dt * 14));
    if (stage == DeliveryStage.splash && elapsed >= 1.7)
      go(DeliveryStage.login);
    if (loginBusy) {
      _loginRemaining -= dt;
      if (_loginRemaining <= 0) {
        loginBusy = false;
        go(DeliveryStage.home);
      }
    }
    if (stage == DeliveryStage.processing) {
      _submitRemaining -= dt;
      if (_submitRemaining <= 0) _finishOrder();
    }
    notifyListeners();
  }

  void validateEmail(String value) {
    emailError =
        value.isEmpty || RegExp(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').hasMatch(value)
        ? null
        : 'Confira o e-mail digitado';
    loginError = null;
    notifyListeners();
  }

  void login() {
    if (loginBusy) return;
    validateEmail(email.text);
    if (email.text.isEmpty || emailError != null || password.text.length < 4) {
      loginError = 'Preencha e-mail e senha para continuar';
      notifyListeners();
      return;
    }
    loginBusy = true;
    _loginRemaining = .55;
    notifyListeners();
  }

  void toggleRemember() {
    remember = !remember;
    notifyListeners();
  }

  void chooseCategory(int index) {
    selectedCategory = index;
    showSaved = false;
    notifyListeners();
  }

  void showFavorites() {
    selectedCategory = 0;
    showSaved = true;
    navTab = 1;
    notifyListeners();
  }

  void openProduct(Product product) {
    selected = product;
    go(DeliveryStage.detail);
  }

  void toggleFavorite(Product product) {
    if (!favorites.add(product.id)) favorites.remove(product.id);
    notifyListeners();
  }

  void add(Product product) {
    if (stage == DeliveryStage.processing ||
        stage == DeliveryStage.confirmation)
      return;
    cart[product.id] = ((cart[product.id] ?? 0) + 1).clamp(1, 9);
    addFeedback = 1.2;
    notifyListeners();
  }

  void changeQuantity(Product product, int delta) {
    if (stage == DeliveryStage.processing ||
        stage == DeliveryStage.confirmation)
      return;
    final value = ((cart[product.id] ?? 0) + delta).clamp(0, 9);
    if (value == 0) {
      cart.remove(product.id);
    } else {
      cart[product.id] = value;
    }
    quantityFeedback = .35;
    notifyListeners();
  }

  void openCart() {
    navTab = 2;
    go(DeliveryStage.cart);
  }

  void checkout() {
    if (cartCount > 0) go(DeliveryStage.checkout);
  }

  void chooseAddress(int index) {
    if (stage == DeliveryStage.processing) return;
    selectedAddress = index.clamp(0, addresses.length - 1);
    notifyListeners();
  }

  void choosePayment(PaymentMethod method) {
    if (stage == DeliveryStage.processing) return;
    payment = method;
    notifyListeners();
  }

  void confirm() {
    if (!canConfirm) return;
    _submitRemaining = .85;
    go(DeliveryStage.processing);
  }

  DeliveryOrder _snapshot() => DeliveryOrder(
    number: 'FD-${1048 + submittedOrders}',
    items: [
      for (final p in products)
        if (cart.containsKey(p.id))
          OrderLine(
            name: p.name,
            unitPrice: p.price,
            quantity: cart[p.id]!,
            art: p.art,
          ),
    ],
    address: address,
    payment: paymentLabel,
    deliveryFee: deliveryFee,
  );
  void _finishOrder() {
    if (stage != DeliveryStage.processing) return;
    order = _snapshot();
    submittedOrders++;
    detailsExpanded = false;
    detailsProgress = 0;
    go(DeliveryStage.confirmation);
  }

  void toggleDetails() {
    detailsExpanded = !detailsExpanded;
    notifyListeners();
  }

  void home({bool newOrder = false}) {
    if (newOrder) {
      cart.clear();
      order = null;
      payment = null;
      detailsExpanded = false;
      detailsProgress = 0;
    }
    navTab = 0;
    showSaved = false;
    selectedCategory = 0;
    go(DeliveryStage.home);
  }

  /// Reproduz a mesma interface em uma linha do tempo determinística.
  void demoAt(double t) {
    demo = true;
    clock = t;
    remember = true;
    const timeline = <(double, DeliveryStage)>[
      (0, DeliveryStage.splash),
      (1.7, DeliveryStage.login),
      (5.05, DeliveryStage.home),
      (9.5, DeliveryStage.detail),
      (13.35, DeliveryStage.cart),
      (17.75, DeliveryStage.checkout),
      (23.45, DeliveryStage.processing),
      (24.3, DeliveryStage.confirmation),
    ];
    var index = 0;
    for (var i = 0; i < timeline.length; i++) {
      if (t >= timeline[i].$1) index = i;
    }
    stage = timeline[index].$2;
    previous = index == 0 ? stage : timeline[index - 1].$2;
    elapsed = t - timeline[index].$1;
    final emailCount = ((t - 2.1) / 1.0 * 16).floor().clamp(0, 16);
    final emailText = 'demo@example.com'.substring(0, emailCount);
    if (email.text != emailText)
      email.value = TextEditingValue(
        text: emailText,
        selection: TextSelection.collapsed(offset: emailText.length),
      );
    final passCount = ((t - 3.4) / .5 * 8).floor().clamp(0, 8);
    final passText = 'demo1234'.substring(0, passCount);
    if (password.text != passText)
      password.value = TextEditingValue(
        text: passText,
        selection: TextSelection.collapsed(offset: passText.length),
      );
    emailError = null;
    loginError = null;
    loginBusy = t >= 4.5 && t < 5.05;
    selected = products.first;
    selectedCategory = 0;
    showSaved = false;
    categoryOffset =
        180 * smooth((t - 5.9) / .6) * (1 - smooth((t - 6.7) / .5));
    homeOffset = 486 * smooth((t - 7.35) / 1.35);
    cart.clear();
    if (t >= 12.1) cart['burger'] = t >= 14.85 ? 2 : 1;
    navTab = stage == DeliveryStage.cart ? 2 : 0;
    addFeedback = t >= 12.1 && t < 13.3 ? 13.3 - t : 0;
    quantityFeedback = t >= 14.85 && t < 15.2 ? 15.2 - t : 0;
    selectedAddress = 0;
    payment = t >= 20.15 ? PaymentMethod.cardOnDelivery : null;
    submittedOrders = t >= 24.3 ? 1 : 0;
    order = t >= 24.3
        ? DeliveryOrder(
            number: 'FD-1048',
            items: [
              const OrderLine(
                name: 'Hambúrguer da casa',
                unitPrice: 2990,
                quantity: 2,
                art: 0,
              ),
            ],
            address: addresses.first,
            payment: 'Cartão na entrega',
          )
        : null;
    detailsExpanded = t >= 26.85;
    detailsProgress = smooth((t - 26.85) / .3);
    notifyListeners();
  }

  @override
  void dispose() {
    email.dispose();
    password.dispose();
    super.dispose();
  }
}
