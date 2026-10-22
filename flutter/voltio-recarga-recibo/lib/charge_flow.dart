import 'package:flutter/foundation.dart';

enum ChargeStage {
  charging,
  completed,
  summary,
  confirm,
  processing,
  success,
  receipt,
}

/// Demo data only. No payment API or personal information is used.
class ChargingSession {
  static const energyKwh = 50.4;
  static const rateCents = 35;
  static const energyCents = 1764;
  static const serviceCents = 126;
  static const totalCents = energyCents + serviceCents;
  static const receiptId = 'VLT-221026-0418';
  static String money(int cents) =>
      'R\$ ${(cents / 100).toStringAsFixed(2).replaceAll('.', ',')}';
}

class ChargeFlow extends ChangeNotifier {
  ChargeStage stage = ChargeStage.charging;
  ChargeStage previous = ChargeStage.charging;
  double clock = 0, enteredAt = -1;
  int paymentMethod = 0;
  int completedPayments = 0;
  bool paid = false;
  bool _demo = false;
  int _demoEvent = 0;
  bool get isDemo => _demo;
  double get elapsed => clock - enteredAt;
  double get progress => ((clock % 24) / 4.65).clamp(0.0, 1.0);
  String get paymentLabel => const [
    'Apple Pay · Face ID',
    'Visa Crédito · •••• 4821',
    'Mastercard Débito · •••• 7310',
  ][paymentMethod];

  double buttonPress(String id) {
    if (!_demo) return 0;
    const clicks = {
      'finish-charging': 5.0,
      'summary': 8.7,
      'pay': 13.5,
      'confirm-pay': 14.3,
      'print-receipt': 17.3,
      'done': 23.05,
    };
    final time = clicks[id];
    if (time == null) return 0;
    return (1 - (clock - time + .035).abs() / .12).clamp(0.0, 1.0);
  }

  void _enter(ChargeStage next) {
    previous = stage;
    stage = next;
    enteredAt = clock;
  }

  void stopCharging() {
    if (stage != ChargeStage.charging) return;
    _enter(ChargeStage.completed);
    notifyListeners();
  }

  void viewSummary() {
    if (stage != ChargeStage.completed) return;
    _enter(ChargeStage.summary);
    notifyListeners();
  }

  void requestPayment() {
    if (stage != ChargeStage.summary || paid) return;
    _enter(ChargeStage.confirm);
    notifyListeners();
  }

  void cancelPayment() {
    if (stage != ChargeStage.confirm) return;
    _enter(ChargeStage.summary);
    notifyListeners();
  }

  void confirmPayment() {
    if (stage != ChargeStage.confirm || paid) return;
    _enter(ChargeStage.processing);
    notifyListeners();
  }

  void _finishPayment() {
    if (stage != ChargeStage.processing || paid) return;
    paid = true;
    completedPayments++;
    _enter(ChargeStage.success);
  }

  void printReceipt() {
    if (!paid ||
        (stage != ChargeStage.success && stage != ChargeStage.receipt)) {
      return;
    }
    _enter(ChargeStage.receipt);
    notifyListeners();
  }

  void finish() {
    if (stage != ChargeStage.receipt) return;
    _enter(ChargeStage.charging);
    paid = false;
    notifyListeners();
  }

  void selectMethod(int value) {
    if (stage != ChargeStage.summary || value < 0 || value > 2) return;
    paymentMethod = value;
    notifyListeners();
  }

  void tick(double dt) {
    if (_demo) {
      demoAt(clock + dt);
      return;
    }
    clock += dt;
    if (stage == ChargeStage.processing && elapsed >= 1.4) _finishPayment();
    notifyListeners();
  }

  /// Calls the same actions as the interactive buttons, on a repeatable timeline.
  void demoAt(double seconds) {
    _demo = true;
    final target = seconds.clamp(0.0, 24.0);
    const eventTimes = [5.0, 8.7, 11.2, 12.3, 13.5, 14.3, 15.8, 17.3, 23.05];
    while (_demoEvent < eventTimes.length && eventTimes[_demoEvent] <= target) {
      clock = eventTimes[_demoEvent];
      switch (_demoEvent) {
        case 0:
          stopCharging();
        case 1:
          viewSummary();
        case 2:
          selectMethod(1);
        case 3:
          selectMethod(2);
        case 4:
          requestPayment();
        case 5:
          confirmPayment();
        case 6:
          _finishPayment();
        case 7:
          printReceipt();
        case 8:
          finish();
      }
      _demoEvent++;
    }
    clock = target;
    notifyListeners();
  }
}
