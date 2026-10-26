// Uma cena guarda os ajustes.
class Scene {
  const Scene({
    required this.name,
    required this.level,
    required this.kelvin,
  });

  final String name;
  final double level;
  final int kelvin;

  int get percent =>
      (level * 100).round();

  String get summary =>
      '$percent% · $kelvin K';

  bool matches({
    required bool isOn,
    required double level,
    required int kelvin,
  }) {
    return isOn &&
        (this.level - level)
                .abs() < .005 &&
        this.kelvin == kelvin;
  }

  Map<String, Object> toMap() {
    return {
      'name': name,
      'level': level,
      'kelvin': kelvin,
    };
  }

  factory Scene.fromMap(
    Map<String, Object> data,
  ) {
    return Scene(
      name: data['name'] as String,
      level: (data['level']
          as num).toDouble(),
      kelvin: data['kelvin'] as int,
    );
  }
}
