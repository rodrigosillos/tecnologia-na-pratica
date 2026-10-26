import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'light_controller.dart';
import 'room_painter.dart';

const ink = Color(0xFFF1F0EC);
const muted = Color(0xFF9FA7B4);
const gold = Color(0xFFF3C988);
const panel = Color(0xFF202632);

Text label(
  String text, {
  double size = 16,
  Color color = ink,
  FontWeight weight = FontWeight.w400,
  double? spacing,
}) => Text(
  text,
  style: TextStyle(
    fontFamily: 'VoltioSans',
    fontSize: size,
    color: color,
    fontWeight: weight,
    letterSpacing: spacing,
    height: 1.2,
  ),
);
Widget at(double x, double y, double w, Widget child, {double? h}) =>
    Positioned(left: x, top: y, width: w, height: h, child: child);

class HomeView extends StatelessWidget {
  const HomeView({super.key, required this.controller});
  final LightController controller;
  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: controller,
    builder: (context, _) {
      final s = controller;
      return ColoredBox(
        color: const Color(0xFF141923),
        child: Stack(
          children: [
            const Positioned(top: 0, left: 0, right: 0, child: PhoneStatus()),
            at(
              24,
              69,
              280,
              label('Minha casa', size: 29, weight: FontWeight.w700),
            ),
            at(25, 106, 280, label('Sala de estar', size: 15, color: muted)),
            at(
              318,
              73,
              48,
              Container(
                height: 44,
                decoration: BoxDecoration(
                  color: panel,
                  borderRadius: BorderRadius.circular(15),
                ),
                child: const Icon(Icons.home_outlined, color: gold, size: 25),
              ),
            ),
            at(
              24,
              138,
              342,
              ClipRRect(
                borderRadius: BorderRadius.circular(22),
                child: SizedBox(
                  height: 248,
                  child: Stack(
                    children: [
                      Positioned.fill(
                        child: CustomPaint(
                          painter: RoomPainter(
                            power: s.power,
                            level: s.level,
                            kelvin: s.kelvin,
                          ),
                        ),
                      ),
                      Positioned(
                        left: 14,
                        top: 12,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 9,
                            vertical: 6,
                          ),
                          decoration: BoxDecoration(
                            color: const Color(0xB8101520),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Container(
                                width: 5,
                                height: 5,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: s.isOn ? gold : muted,
                                ),
                              ),
                              const SizedBox(width: 6),
                              label(
                                s.isOn ? 'Luz ligada' : 'Luz apagada',
                                size: 10,
                                weight: FontWeight.w500,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            at(
              24,
              400,
              342,
              Container(
                height: 220,
                decoration: BoxDecoration(
                  color: panel,
                  borderRadius: BorderRadius.circular(22),
                  border: Border.all(color: const Color(0xFF303744)),
                ),
              ),
            ),
            at(
              42,
              416,
              32,
              Icon(
                Icons.lightbulb_outline_rounded,
                color: s.isOn ? gold : muted,
                size: 26,
              ),
            ),
            at(84, 411, 190, label('Luz', size: 19, weight: FontWeight.w700)),
            at(
              84,
              435,
              180,
              label('Luminária da sala', size: 12, color: muted),
            ),
            at(
              294,
              413,
              56,
              Semantics(
                label: 'Luz',
                button: true,
                toggled: s.isOn,
                child: GestureDetector(
                  key: const ValueKey('power'),
                  onTap: s.toggle,
                  behavior: HitTestBehavior.opaque,
                  child: SizedBox(
                    height: 34,
                    child: CustomPaint(painter: TogglePainter(s.power)),
                  ),
                ),
              ),
            ),
            at(
              43,
              467,
              200,
              label('Intensidade', size: 14, weight: FontWeight.w500),
            ),
            at(
              274,
              465,
              72,
              Align(
                alignment: Alignment.centerRight,
                child: label(
                  '${(s.level * 100).round()}%',
                  size: 19,
                  weight: FontWeight.w700,
                ),
              ),
            ),
            at(
              43,
              486,
              304,
              ControlSlider(
                key: const ValueKey('level'),
                value: (s.level - .05) / .95,
                onChanged: (v) => s.changeLevel(.05 + v * .95),
                colors: const [Color(0xFF6C6255), gold],
                semanticLabel: 'Intensidade',
              ),
            ),
            at(
              43,
              547,
              196,
              label('Temperatura', size: 14, weight: FontWeight.w500),
            ),
            at(
              249,
              545,
              97,
              Align(
                alignment: Alignment.centerRight,
                child: label(
                  '${s.kelvin} K',
                  size: 18,
                  weight: FontWeight.w700,
                ),
              ),
            ),
            at(
              43,
              567,
              304,
              ControlSlider(
                key: const ValueKey('kelvin'),
                value: (s.kelvin - 2700) / 3800,
                onChanged: (v) => s.changeKelvin(2700 + v * 3800),
                colors: const [
                  Color(0xFFFFBD73),
                  Color(0xFFF7EEE2),
                  Color(0xFFB4D7FF),
                ],
                semanticLabel: 'Temperatura',
              ),
            ),
            at(55, 604, 120, label('Quente', size: 10, color: muted)),
            at(
              277,
              604,
              58,
              Align(
                alignment: Alignment.centerRight,
                child: label('Fria', size: 10, color: muted),
              ),
            ),
            at(
              24,
              638,
              342,
              s.saved == null
                  ? GestureDetector(
                      key: const ValueKey('save-scene'),
                      onTap: s.openEditor,
                      child: Container(
                        height: 66,
                        decoration: BoxDecoration(
                          color: gold,
                          borderRadius: BorderRadius.circular(18),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(
                              Icons.add_rounded,
                              color: Color(0xFF242323),
                              size: 23,
                            ),
                            const SizedBox(width: 9),
                            label(
                              'Salvar cena',
                              size: 17,
                              color: const Color(0xFF242323),
                              weight: FontWeight.w700,
                            ),
                          ],
                        ),
                      ),
                    )
                  : GestureDetector(
                      key: const ValueKey('apply-scene'),
                      onTap: s.applyScene,
                      child: Container(
                        height: 66,
                        padding: const EdgeInsets.symmetric(horizontal: 17),
                        decoration: BoxDecoration(
                          color: s.active ? const Color(0xFF343129) : panel,
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(
                            color: s.active
                                ? const Color(0xFF746143)
                                : const Color(0xFF353D4D),
                          ),
                        ),
                        child: Row(
                          children: [
                            const Icon(
                              Icons.movie_outlined,
                              color: gold,
                              size: 27,
                            ),
                            const SizedBox(width: 13),
                            Expanded(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  label(
                                    'Cinema',
                                    size: 17,
                                    weight: FontWeight.w700,
                                  ),
                                  const SizedBox(height: 4),
                                  label(
                                    s.saved!.summary,
                                    size: 12,
                                    color: muted,
                                  ),
                                ],
                              ),
                            ),
                            if (s.active)
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 9,
                                  vertical: 5,
                                ),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF514633),
                                  borderRadius: BorderRadius.circular(9),
                                ),
                                child: label(
                                  'Ativa',
                                  size: 11,
                                  color: gold,
                                  weight: FontWeight.w700,
                                ),
                              )
                            else
                              const Icon(
                                Icons.play_circle_outline_rounded,
                                color: gold,
                                size: 27,
                              ),
                          ],
                        ),
                      ),
                    ),
            ),
            at(
              28,
              722,
              334,
              Opacity(
                opacity: s.toast.clamp(0, 1),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.check_circle_outline_rounded,
                      color: gold,
                      size: 17,
                    ),
                    const SizedBox(width: 7),
                    label(
                      s.message,
                      size: 13,
                      color: gold,
                      weight: FontWeight.w500,
                    ),
                  ],
                ),
              ),
            ),
            at(
              24,
              773,
              342,
              Center(
                child: label(
                  'Tecnologia na Prática',
                  size: 12,
                  color: muted,
                  weight: FontWeight.w500,
                ),
              ),
            ),
            at(
              24,
              792,
              342,
              Center(
                child: label(
                  'Demonstração de interface',
                  size: 10,
                  color: const Color(0xFF778190),
                ),
              ),
            ),
            if (s.sheet > .001)
              Positioned.fill(
                child: GestureDetector(
                  onTap: s.closeEditor,
                  child: ColoredBox(
                    color: Colors.black.withValues(alpha: .48 * s.sheet),
                  ),
                ),
              ),
            if (s.sheet > .001)
              Positioned(
                left: 0,
                right: 0,
                top: 558 + (1 - s.sheet) * 286,
                child: Container(
                  height: 286,
                  decoration: const BoxDecoration(
                    color: Color(0xFF272E3C),
                    borderRadius: BorderRadius.vertical(
                      top: Radius.circular(28),
                    ),
                  ),
                  child: Stack(
                    children: [
                      at(
                        174,
                        11,
                        42,
                        Container(
                          height: 4,
                          decoration: BoxDecoration(
                            color: const Color(0xFF596170),
                            borderRadius: BorderRadius.circular(4),
                          ),
                        ),
                      ),
                      at(
                        25,
                        34,
                        280,
                        label('Salvar cena', size: 24, weight: FontWeight.w700),
                      ),
                      at(
                        325,
                        26,
                        42,
                        IconButton(
                          key: const ValueKey('close-editor'),
                          onPressed: s.closeEditor,
                          icon: const Icon(
                            Icons.close_rounded,
                            color: muted,
                            size: 22,
                          ),
                        ),
                      ),
                      at(
                        25,
                        72,
                        330,
                        label(
                          '${(s.level * 100).round()}% de intensidade · ${s.kelvin} K',
                          size: 14,
                          color: muted,
                        ),
                      ),
                      at(
                        25,
                        104,
                        330,
                        label('Escolha um nome', size: 13, color: muted),
                      ),
                      at(
                        24,
                        137,
                        342,
                        GestureDetector(
                          key: const ValueKey('name-cinema'),
                          onTap: s.saveCinema,
                          child: Container(
                            height: 64,
                            padding: const EdgeInsets.symmetric(horizontal: 18),
                            decoration: BoxDecoration(
                              color: gold,
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Row(
                              children: [
                                const Icon(
                                  Icons.movie_outlined,
                                  color: Color(0xFF272323),
                                  size: 27,
                                ),
                                const SizedBox(width: 14),
                                Expanded(
                                  child: Column(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      label(
                                        'Cinema',
                                        size: 18,
                                        color: const Color(0xFF272323),
                                        weight: FontWeight.w700,
                                      ),
                                      const SizedBox(height: 3),
                                      label(
                                        'Salvar com este nome',
                                        size: 12,
                                        color: const Color(0xFF574832),
                                      ),
                                    ],
                                  ),
                                ),
                                const Icon(
                                  Icons.check_rounded,
                                  color: Color(0xFF272323),
                                  size: 25,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            Positioned(
              left: 128,
              bottom: 9,
              child: Container(
                width: 134,
                height: 4,
                decoration: BoxDecoration(
                  color: ink,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ),
            if (s.demo)
              Positioned.fill(
                child: IgnorePointer(
                  child: CustomPaint(painter: DemoPointer(s.clock)),
                ),
              ),
          ],
        ),
      );
    },
  );
}

class ControlSlider extends StatelessWidget {
  const ControlSlider({
    super.key,
    required this.value,
    required this.onChanged,
    required this.colors,
    required this.semanticLabel,
  });
  final double value;
  final ValueChanged<double> onChanged;
  final List<Color> colors;
  final String semanticLabel;
  @override
  Widget build(BuildContext context) => Semantics(
    label: semanticLabel,
    value: '${(value * 100).round()}%',
    slider: true,
    child: GestureDetector(
      behavior: HitTestBehavior.opaque,
      onTapDown: (d) =>
          onChanged(((d.localPosition.dx - 12) / 280).clamp(0, 1)),
      onHorizontalDragStart: (d) =>
          onChanged(((d.localPosition.dx - 12) / 280).clamp(0, 1)),
      onHorizontalDragUpdate: (d) =>
          onChanged(((d.localPosition.dx - 12) / 280).clamp(0, 1)),
      child: SizedBox(
        height: 42,
        child: CustomPaint(painter: SliderPainter(value, colors)),
      ),
    ),
  );
}

class SliderPainter extends CustomPainter {
  SliderPainter(this.value, this.colors);
  final double value;
  final List<Color> colors;
  @override
  void paint(Canvas c, Size s) {
    final track = RRect.fromRectAndRadius(
      Rect.fromLTWH(12, 17, s.width - 24, 8),
      const Radius.circular(4),
    );
    c.drawRRect(
      track,
      Paint()
        ..shader = LinearGradient(colors: colors).createShader(track.outerRect),
    );
    final center = Offset(12 + value * (s.width - 24), 21);
    c.drawShadow(
      Path()..addOval(Rect.fromCircle(center: center, radius: 11)),
      Colors.black,
      .7,
      true,
    );
    c.drawCircle(center, 11, Paint()..color = const Color(0xFFF6F3EC));
    c.drawCircle(center, 4, Paint()..color = const Color(0xFF7D766A));
  }

  @override
  bool shouldRepaint(SliderPainter old) =>
      old.value != value || old.colors != colors;
}

class TogglePainter extends CustomPainter {
  TogglePainter(this.progress);
  final double progress;
  @override
  void paint(Canvas c, Size s) {
    c.drawRRect(
      RRect.fromRectAndRadius(
        const Rect.fromLTWH(0, 0, 56, 34),
        const Radius.circular(17),
      ),
      Paint()..color = Color.lerp(const Color(0xFF48515F), gold, progress)!,
    );
    c.drawCircle(
      Offset(17 + 22 * progress, 17),
      12,
      Paint()..color = const Color(0xFFF9F6F0),
    );
  }

  @override
  bool shouldRepaint(TogglePainter old) => old.progress != progress;
}

class PhoneStatus extends StatelessWidget {
  const PhoneStatus({super.key});
  @override
  Widget build(BuildContext context) => SizedBox(
    height: 46,
    child: Stack(
      children: [
        at(27, 16, 50, label('9:41', size: 13, weight: FontWeight.w700)),
        at(
          137,
          9,
          116,
          Container(
            height: 31,
            decoration: BoxDecoration(
              color: Colors.black,
              borderRadius: BorderRadius.circular(24),
            ),
          ),
        ),
        Positioned(
          right: 22,
          top: 17,
          child: Row(
            children: [
              const Icon(
                Icons.signal_cellular_alt_rounded,
                color: ink,
                size: 15,
              ),
              const SizedBox(width: 3),
              const Icon(Icons.wifi_rounded, color: ink, size: 15),
              const SizedBox(width: 5),
              const Icon(Icons.battery_full_rounded, color: ink, size: 19),
            ],
          ),
        ),
      ],
    ),
  );
}

/// Cursor reaproveita a forma e a suavização aprovadas, com novos alvos.
class DemoPointer extends CustomPainter {
  DemoPointer(this.time);
  final double time;
  static const trajectory = <(double, Offset)>[
    (0, Offset(296, 458)),
    (.72, Offset(322, 430)),
    (2.6, Offset(322, 430)),
    (3.5, Offset(276.0526, 507)),
    (6.4, Offset(128.6842, 507)),
    (6.7, Offset(128.6842, 507)),
    (7.5, Offset(335, 588)),
    (10.4, Offset(55, 588)),
    (10.65, Offset(55, 588)),
    (11.55, Offset(310, 670)),
    (12.2, Offset(310, 670)),
    (13.25, Offset(210, 725)),
    (14.35, Offset(210, 725)),
    (15.55, Offset(322, 430)),
    (17.3, Offset(322, 430)),
    (18.55, Offset(310, 670)),
    (19.55, Offset(310, 670)),
    (20.6, Offset(355, 750)),
    (24, Offset(355, 750)),
  ];
  Offset get position {
    for (var i = 1; i < trajectory.length; i++) {
      final a = trajectory[i - 1], b = trajectory[i];
      if (time <= b.$1) {
        final t = smooth((time - a.$1) / (b.$1 - a.$1));
        final delta = b.$2 - a.$2;
        if (delta.distance < .01) return a.$2;
        // Arrastos horizontais coincidem exatamente com a posição do controle.
        if ((a.$1 == 3.5) || (a.$1 == 7.5)) return Offset.lerp(a.$2, b.$2, t)!;
        final normal = Offset(-delta.dy, delta.dx) / delta.distance;
        final bend =
            math.min(12.0, delta.distance * .08) * (delta.dy > 0 ? -1 : 1);
        final c1 = a.$2 + delta * .32 + normal * bend,
            c2 = b.$2 - delta * .28 + normal * (bend * .65),
            v = 1 - t;
        return a.$2 * (v * v * v) +
            c1 * (3 * v * v * t) +
            c2 * (3 * v * t * t) +
            b.$2 * (t * t * t);
      }
    }
    return trajectory.last.$2;
  }

  @override
  void paint(Canvas c, Size s) {
    final clicks = <double, Offset>{
      .8: const Offset(322, 430),
      3.5: const Offset(276.0526, 507),
      7.5: const Offset(335, 588),
      11.65: const Offset(310, 670),
      13.35: const Offset(210, 725),
      15.65: const Offset(322, 430),
      18.65: const Offset(310, 670),
    };
    for (final e in clicks.entries) {
      final dt = time - e.key;
      if (dt < -.04 || dt > .26) continue;
      final p = ((dt + .04) / .3).clamp(0.0, 1.0), a = math.sin(p * math.pi);
      c.drawCircle(
        e.value,
        3 + p * 9,
        Paint()
          ..color = Colors.white.withValues(alpha: .55 * a)
          ..strokeWidth = 1.6
          ..style = PaintingStyle.stroke,
      );
    }
    c.save();
    c.translate(position.dx, position.dy);
    final arrow = Path()
      ..moveTo(0, 0)
      ..lineTo(0, 18.8)
      ..lineTo(4.8, 14.6)
      ..lineTo(8.5, 22.5)
      ..lineTo(11.7, 21)
      ..lineTo(8, 13)
      ..lineTo(14.2, 13)
      ..close();
    c.drawShadow(arrow, const Color(0x55000000), 1.2, true);
    c.drawPath(arrow, Paint()..color = const Color(0xFF080808));
    c.drawPath(
      arrow,
      Paint()
        ..color = Colors.white
        ..style = PaintingStyle.stroke
        ..strokeJoin = StrokeJoin.round
        ..strokeWidth = 1,
    );
    c.restore();
  }

  @override
  bool shouldRepaint(DemoPointer old) => old.time != time;
}
