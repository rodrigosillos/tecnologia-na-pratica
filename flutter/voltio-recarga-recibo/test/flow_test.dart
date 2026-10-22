import 'package:flutter_test/flutter_test.dart';
import 'package:voltio/charge_flow.dart';

void main() {
  test('Receipt total matches the charging session in integer cents', () {
    expect(
      (ChargingSession.energyKwh * ChargingSession.rateCents).round(),
      ChargingSession.energyCents,
    );
    expect(ChargingSession.totalCents, 1890);
  });
  test(
    'No receipt before payment; cancellation does not charge; repeat confirmation is ignored',
    () {
      final c = ChargeFlow();
      c.printReceipt();
      expect(c.stage, ChargeStage.charging);
      c.stopCharging();
      c.viewSummary();
      c.requestPayment();
      c.cancelPayment();
      expect(c.completedPayments, 0);
      expect(c.stage, ChargeStage.summary);
      c.requestPayment();
      c.confirmPayment();
      c.confirmPayment();
      c.tick(1.5);
      expect(c.stage, ChargeStage.success);
      expect(c.completedPayments, 1);
      c.printReceipt();
      c.tick(6);
      c.printReceipt();
      expect(c.stage, ChargeStage.receipt);
      expect(c.completedPayments, 1);
      c.finish();
      expect(c.stage, ChargeStage.charging);
    },
  );
  test('The 24 second demonstration performs one payment and returns home', () {
    final c = ChargeFlow();
    c.demoAt(5.1);
    expect(c.stage, ChargeStage.completed);
    c.demoAt(8.8);
    expect(c.stage, ChargeStage.summary);
    c.demoAt(11.3);
    expect(c.paymentMethod, 1);
    c.demoAt(12.4);
    expect(c.paymentMethod, 2);
    expect(c.paymentLabel, contains('7310'));
    c.demoAt(13.6);
    expect(c.stage, ChargeStage.confirm);
    c.demoAt(14.5);
    expect(c.stage, ChargeStage.processing);
    c.demoAt(16.0);
    expect(c.stage, ChargeStage.success);
    c.demoAt(21.5);
    expect(c.stage, ChargeStage.receipt);
    expect(c.paid, true);
    c.demoAt(24);
    expect(c.stage, ChargeStage.charging);
    expect(c.completedPayments, 1);
  });
}
