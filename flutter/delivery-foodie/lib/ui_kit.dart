import 'dart:math' as math;
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'delivery_controller.dart';

const brandPrimary = Color(0xFF5D8C2B);
const brandDark = Color(0xFF35541D);
const ink = Color(0xFF282E22);
const muted = Color(0xFF838A7A);
const paper = Color(0xFFFBFCF8);
const lineColor = Color(0xFFE7ECE1);
const brandSoft = Color(0xFFF0F6E8);
const brandGradient = LinearGradient(
  begin: Alignment.topLeft, end: Alignment.bottomRight,
  colors: [Color(0xFF304D19), Color(0xFF608C28), Color(0xFF95C83D)],
  stops: [0, .68, 1],
);
const actionGradient = LinearGradient(
  colors: [Color(0xFF35541D), Color(0xFF568428), Color(0xFF80B83D)],
  stops: [0, .6, 1],
);
ui.Image? foodAtlas;

Future<void> loadDeliveryArt() async {
  if (foodAtlas != null) return;
  final bytes = await rootBundle.load('assets/art/food_atlas.png');
  final codec = await ui.instantiateImageCodec(bytes.buffer.asUint8List());
  foodAtlas = (await codec.getNextFrame()).image;
  codec.dispose();
}

Widget at(double x, double y, double width, Widget child, {double? height}) =>
    Positioned(left: x, top: y, width: width, height: height, child: child);

Text txt(
  String value, {
  double size = 16,
  Color color = ink,
  FontWeight weight = FontWeight.w400,
  TextAlign? align,
  int? maxLines,
  double height = 1.22,
}) => Text(
  value,
  textAlign: align,
  maxLines: maxLines,
  overflow: maxLines == null ? null : TextOverflow.ellipsis,
  style: TextStyle(
    fontFamily: 'VoltioSans',
    fontSize: size,
    color: color,
    fontWeight: weight,
    height: height,
  ),
);

BoxDecoration card({
  Color color = Colors.white,
  double radius = 19,
  Color border = lineColor,
}) => BoxDecoration(
  color: color,
  borderRadius: BorderRadius.circular(radius),
  border: Border.all(color: border, width: 1),
);

class FoodArt extends StatelessWidget {
  const FoodArt(this.index, {super.key, this.size = 88});
  final int index;
  final double size;
  @override
  Widget build(BuildContext context) => SizedBox.square(
    dimension: size,
    child: CustomPaint(painter: FoodPainter(index)),
  );
}

class FoodPainter extends CustomPainter {
  FoodPainter(this.index);
  final int index;
  @override
  void paint(Canvas c, Size size) {
    final img = foodAtlas;
    if (img == null) return;
    final cw = img.width / 3, ch = img.height / 2;
    final src = index == 4
        ? Rect.fromLTWH(cw, ch - 30, cw, ch + 30)
        : Rect.fromLTWH(
            index % 3 * cw,
            index ~/ 3 * ch,
            cw,
            index == 1 ? ch - 28 : ch,
          );
    final dest = index == 1
        ? Rect.fromLTWH(0, 0, size.width, size.height * (ch - 28) / ch)
        : Rect.fromCenter(
            center: size.center(Offset.zero),
            width: size.width,
            height: size.height,
          );
    c.drawImageRect(
      img,
      src,
      dest,
      Paint()..filterQuality = FilterQuality.high,
    );
  }

  @override
  bool shouldRepaint(FoodPainter old) => old.index != index;
}

class Courier extends StatelessWidget {
  const Courier({super.key, this.size = 200});
  final double size;
  @override
  Widget build(BuildContext context) => Image.asset(
    'assets/art/courier.png',
    width: size,
    height: size,
    fit: BoxFit.contain,
    filterQuality: FilterQuality.high,
  );
}

class RoundButton extends StatelessWidget {
  const RoundButton({
    super.key,
    required this.icon,
    required this.onTap,
    this.color = ink,
    this.fill = Colors.white,
    this.count = 0,
    this.size = 40,
  });
  final IconData icon;
  final VoidCallback onTap;
  final Color color, fill;
  final int count;
  final double size;
  @override
  Widget build(BuildContext context) => GestureDetector(
    onTap: onTap,
    behavior: HitTestBehavior.opaque,
    child: SizedBox.square(
      dimension: size,
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(color: fill, shape: BoxShape.circle),
              child: Icon(icon, color: color, size: 21),
            ),
          ),
          if (count > 0)
            Positioned(
              right: -3,
              top: -4,
              child: Container(
                width: 19,
                height: 19,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: brandPrimary,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 2),
                ),
                child: txt(
                  '$count',
                  size: 10,
                  color: Colors.white,
                  weight: FontWeight.w700,
                ),
              ),
            ),
        ],
      ),
    ),
  );
}

class ActionButton extends StatelessWidget {
  const ActionButton({
    super.key,
    required this.label,
    required this.onTap,
    this.busy = false,
    this.enabled = true,
    this.clock = 0,
    this.icon,
  });
  final String label;
  final VoidCallback onTap;
  final bool busy, enabled;
  final double clock;
  final IconData? icon;
  @override
  Widget build(BuildContext context) => Semantics(
    button: true,
    enabled: enabled,
    label: label,
    child: GestureDetector(
      onTap: enabled && !busy ? onTap : null,
      behavior: HitTestBehavior.opaque,
      child: Container(
        height: 54,
        decoration: BoxDecoration(
          color: enabled ? null : const Color(0xFFBECAB1),
          gradient: enabled ? actionGradient : null,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Center(
          child: busy
              ? SizedBox.square(
                  dimension: 23,
                  child: CustomPaint(painter: SpinnerPainter(clock)),
                )
              : Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (icon != null) ...[
                      Icon(icon, color: Colors.white, size: 21),
                      const SizedBox(width: 8),
                    ],
                    txt(
                      label,
                      size: 16,
                      color: Colors.white,
                      weight: FontWeight.w700,
                    ),
                  ],
                ),
        ),
      ),
    ),
  );
}

class SpinnerPainter extends CustomPainter {
  SpinnerPainter(this.time);
  final double time;
  @override
  void paint(Canvas c, Size s) {
    c.drawCircle(
      s.center(Offset.zero),
      s.width / 2 - 2,
      Paint()
        ..color = const Color(0x55FFFFFF)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.5,
    );
    c.drawArc(
      Rect.fromLTWH(2, 2, s.width - 4, s.height - 4),
      time * math.pi * 3,
      math.pi * 1.25,
      false,
      Paint()
        ..color = Colors.white
        ..strokeWidth = 2.5
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round,
    );
  }

  @override
  bool shouldRepaint(SpinnerPainter old) => old.time != time;
}

class PhoneStatus extends StatelessWidget {
  const PhoneStatus({super.key, this.light = false});
  final bool light;
  @override
  Widget build(BuildContext context) {
    final color = light ? Colors.white : ink;
    return SizedBox(
      height: 46,
      child: Stack(
        children: [
          at(
            27,
            16,
            50,
            txt('11:11', size: 12, color: color, weight: FontWeight.w700),
          ),
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
                Icon(Icons.signal_cellular_alt_rounded, color: color, size: 15),
                const SizedBox(width: 3),
                Icon(Icons.wifi_rounded, color: color, size: 15),
                const SizedBox(width: 5),
                Icon(Icons.battery_full_rounded, color: color, size: 19),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class CheckPainter extends CustomPainter {
  CheckPainter(this.progress, {this.color = Colors.white, this.width = 5});
  final double progress, width;
  final Color color;
  @override
  void paint(Canvas c, Size s) {
    final path = Path()
      ..moveTo(s.width * .19, s.height * .5)
      ..lineTo(s.width * .42, s.height * .72)
      ..lineTo(s.width * .82, s.height * .27);
    final m = path.computeMetrics().first;
    c.drawPath(
      m.extractPath(0, m.length * progress.clamp(0, 1)),
      Paint()
        ..color = color
        ..strokeWidth = width
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round,
    );
  }

  @override
  bool shouldRepaint(CheckPainter old) => old.progress != progress;
}

class DemoPointer extends CustomPainter {
  DemoPointer(this.time);
  final double time;
  static const trajectory = <(double, Offset)>[
    (0, Offset(354, 670)),
    (1.45, Offset(354, 670)),
    (2.03, Offset(224, 426)),
    (3.02, Offset(224, 426)),
    (3.38, Offset(235, 493)),
    (3.96, Offset(235, 493)),
    (4.43, Offset(282, 610)),
    (5.18, Offset(282, 610)),
    (5.86, Offset(299, 365)),
    (6.5, Offset(119, 365)),
    (6.65, Offset(119, 365)),
    (7.2, Offset(299, 365)),
    (7.8, Offset(322, 620)),
    (8.7, Offset(322, 620)),
    (9.46, Offset(116, 329)),
    (10.15, Offset(116, 329)),
    (11.28, Offset(314, 695)),
    (12.06, Offset(285, 756)),
    (12.6, Offset(285, 756)),
    (13.3, Offset(297, 83)),
    (14.12, Offset(297, 83)),
    (14.81, Offset(334, 252)),
    (16.95, Offset(334, 252)),
    (17.71, Offset(289, 769)),
    (18.45, Offset(289, 769)),
    (19.2, Offset(312, 190)),
    (19.55, Offset(312, 190)),
    (20.11, Offset(325, 331)),
    (21.15, Offset(325, 331)),
    (22.2, Offset(334, 640)),
    (23.41, Offset(280, 769)),
    (24.1, Offset(280, 769)),
    (24.8, Offset(350, 718)),
    (26.05, Offset(350, 718)),
    (26.81, Offset(326, 525)),
    (27.25, Offset(326, 525)),
    (27.9, Offset(355, 727)),
    (30, Offset(355, 727)),
  ];
  Offset get position {
    for (var i = 1; i < trajectory.length; i++) {
      final a = trajectory[i - 1], b = trajectory[i];
      if (time > b.$1) continue;
      final t = smooth((time - a.$1) / (b.$1 - a.$1));
      final delta = b.$2 - a.$2;
      if (delta.distance < .01) return a.$2;
      if (a.$1 == 5.86 || a.$1 == 6.65) return Offset.lerp(a.$2, b.$2, t)!;
      final normal = Offset(-delta.dy, delta.dx) / delta.distance;
      final bend =
          math.min(8.0, delta.distance * .045) * (delta.dy > 0 ? -1 : 1);
      final c1 = a.$2 + delta * .34 + normal * bend,
          c2 = b.$2 - delta * .30 + normal * bend * .5,
          v = 1 - t;
      return a.$2 * (v * v * v) +
          c1 * (3 * v * v * t) +
          c2 * (3 * v * t * t) +
          b.$2 * (t * t * t);
    }
    return trajectory.last.$2;
  }

  @override
  void paint(Canvas c, Size size) {
    final opacity = smooth((time - 1.4) / .3);
    if (opacity == 0) return;
    final clicks = <double, Offset>{
      2.1: const Offset(224, 426),
      3.4: const Offset(235, 493),
      4.5: const Offset(282, 610),
      5.9: const Offset(299, 365),
      6.7: const Offset(119, 365),
      9.5: const Offset(116, 329),
      12.1: const Offset(285, 756),
      13.35: const Offset(297, 83),
      14.85: const Offset(334, 252),
      17.75: const Offset(289, 769),
      20.15: const Offset(325, 331),
      23.45: const Offset(280, 769),
      26.85: const Offset(326, 525),
    };
    for (final e in clicks.entries) {
      final dt = time - e.key;
      if (dt < 0 || dt > .24) continue;
      final p = dt / .24, alpha = math.sin(p * math.pi);
      c.drawCircle(
        e.value,
        3 + p * 9,
        Paint()
          ..color = brandPrimary.withValues(alpha: .44 * alpha)
          ..strokeWidth = 1.7
          ..style = PaintingStyle.stroke,
      );
      c.drawCircle(
        e.value,
        3 + p * 9,
        Paint()
          ..color = Colors.white.withValues(alpha: .6 * alpha)
          ..strokeWidth = .7
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
    c.drawPath(
      arrow,
      Paint()..color = const Color(0xFF080808).withValues(alpha: opacity),
    );
    c.drawPath(
      arrow,
      Paint()
        ..color = Colors.white.withValues(alpha: opacity)
        ..style = PaintingStyle.stroke
        ..strokeJoin = StrokeJoin.round
        ..strokeWidth = 1,
    );
    c.restore();
  }

  @override
  bool shouldRepaint(DemoPointer old) => old.time != time;
}
