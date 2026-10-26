import 'dart:math' as math;
import 'package:flutter/foundation.dart';
import 'scene.dart';

double smooth(double value) {
  final x = value.clamp(0.0, 1.0);
  return x * x * x * (10 + x * (-15 + x * 6));
}

/// Estado local: nenhuma conexão com lâmpadas ou serviços externos.
class LightController extends ChangeNotifier {
  bool isOn = false;
  double level = .8;
  int kelvin = 6500;
  Scene? saved;
  bool showEditor = false;
  double power = 0;
  double sheet = 0;
  double toast = 0;
  String message = '';
  double clock = 0;
  bool demo = false;
  double _toastRemaining = 0;

  bool get active =>
      saved?.matches(isOn: isOn, level: level, kelvin: kelvin) ?? false;

  void toggle() {
    isOn = !isOn;
    notifyListeners();
  }

  void changeLevel(double value) {
    level = value.clamp(.05, 1.0);
    notifyListeners();
  }

  void changeKelvin(double value) {
    kelvin = ((value / 100).round() * 100).clamp(2700, 6500);
    notifyListeners();
  }

  void openEditor() {
    showEditor = true;
    notifyListeners();
  }

  void closeEditor() {
    showEditor = false;
    notifyListeners();
  }

  void saveCinema() {
    saved = Scene(name: 'Cinema', level: level, kelvin: kelvin);
    showEditor = false;
    message = 'Cena Cinema salva';
    _toastRemaining = 2;
    notifyListeners();
  }

  void applyScene() {
    final scene = saved;
    if (scene == null) return;
    level = scene.level;
    kelvin = scene.kelvin;
    isOn = true;
    message = 'Cena Cinema aplicada';
    _toastRemaining = 4;
    notifyListeners();
  }

  void tick(double dt) {
    if (demo) return;
    final step = 1 - math.exp(-dt * 9);
    power += ((isOn ? 1.0 : 0.0) - power) * step;
    sheet += ((showEditor ? 1.0 : 0.0) - sheet) * step;
    _toastRemaining = math.max(0, _toastRemaining - dt);
    toast += ((_toastRemaining > 0 ? 1.0 : 0.0) - toast) * step;
    notifyListeners();
  }

  /// Linha do tempo determinística para exportar os widgets a 60 fps.
  void demoAt(double t) {
    demo = true;
    clock = t;
    isOn = t >= .8 && (t < 15.65 || t >= 18.65);
    level = .8 - .5 * smooth((t - 3.5) / 2.9);
    kelvin = (6500 - 3800 * smooth((t - 7.5) / 2.9)).round();
    power =
        smooth((t - .8) / .75) * (1 - smooth((t - 15.65) / .7)) +
        smooth((t - 18.65) / 2.25);
    showEditor = t >= 11.65 && t < 13.35;
    sheet = smooth((t - 11.65) / .38) * (1 - smooth((t - 13.35) / .35));
    saved = t >= 13.35
        ? const Scene(name: 'Cinema', level: .3, kelvin: 2700)
        : null;
    if (t >= 18.65) {
      message = 'Cena Cinema aplicada';
      toast = smooth((t - 21.1) / .35);
    } else {
      message = 'Cena Cinema salva';
      toast = smooth((t - 13.6) / .3) * (1 - smooth((t - 15.05) / .3));
    }
    notifyListeners();
  }
}
