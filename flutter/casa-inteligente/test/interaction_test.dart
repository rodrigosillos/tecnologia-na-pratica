import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:casa_inteligente/app.dart';
import 'package:casa_inteligente/light_controller.dart';
import 'package:casa_inteligente/scene.dart';

void main() {
  test('A cena salva é independente dos controles e restaura os dois valores', () {
    final c=LightController();
    c.changeLevel(.3);c.changeKelvin(2700);c.saveCinema();
    final copy=Scene.fromMap(c.saved!.toMap());
    expect(copy.summary,'30% · 2700 K');
    expect(c.active,false);
    c.changeLevel(.9);c.changeKelvin(6300);
    expect(c.saved!.level,.3);expect(c.saved!.kelvin,2700);
    c.applyScene();
    expect(c.isOn,true);expect(c.level,.3);expect(c.kelvin,2700);expect(c.active,true);
    c.toggle();expect(c.active,false);expect(c.saved, isNotNull);
    c.dispose();
  });

  testWidgets('Toques e arrastos reais: ajustar, cancelar, salvar e reaplicar', (tester) async {
    tester.view.physicalSize=const Size(390,844);
    tester.view.devicePixelRatio=1;
    addTearDown(tester.view.resetPhysicalSize);addTearDown(tester.view.resetDevicePixelRatio);
    final c=LightController();
    Future<void> animate() async {
      for(var i=0;i<20;i++){c.tick(.05);await tester.pump(const Duration(milliseconds:50));}
    }
    await tester.pumpWidget(CasaApp(controller:c));
    await tester.tap(find.byKey(const ValueKey('power')));await animate();
    expect(c.isOn,true);expect(c.power,greaterThan(.99));
    final gesture=await tester.startGesture(const Offset(276.0526,507));
    await gesture.moveTo(const Offset(128.6842,507));await gesture.up();await tester.pump();
    expect(c.level,closeTo(.3,.01));
    await tester.tapAt(const Offset(55,588));await tester.pump();
    expect(c.kelvin,2700);
    await tester.tap(find.byKey(const ValueKey('save-scene')));await animate();
    await tester.tap(find.byKey(const ValueKey('close-editor')));await animate();
    expect(c.saved,isNull);
    await tester.tap(find.byKey(const ValueKey('save-scene')));await animate();
    await tester.tap(find.byKey(const ValueKey('name-cinema')));await animate();
    expect(c.saved,isNotNull);expect(c.saved!.summary,'30% · 2700 K');
    await tester.tapAt(const Offset(320,507));await tester.pump();
    await tester.tapAt(const Offset(320,588));await tester.pump();
    expect(c.active,false);
    await tester.tap(find.byKey(const ValueKey('power')));await animate();
    expect(c.isOn,false);
    await tester.tap(find.byKey(const ValueKey('apply-scene')));await animate();
    expect(c.isOn,true);expect(c.level,closeTo(.3,.01));expect(c.kelvin,2700);expect(c.active,true);
    expect(find.text('Cena Cinema aplicada'),findsOneWidget);
    expect(tester.takeException(),isNull);
    await tester.pumpWidget(const SizedBox.shrink());c.dispose();
  });
}
