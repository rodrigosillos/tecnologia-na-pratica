import 'dart:math' as math;
import 'package:flutter/material.dart';

const blue = Color(0xFF254BFF);
const ink = Color(0xFF111827);
const muted = Color(0xFF858C9A);
const line = Color(0xFFE9ECF1);
const sheet = Color(0xFFF6F8FB);
double unit(double x) => x.clamp(0.0, 1.0);
double ease(double x) => Curves.easeInOutCubic.transform(unit(x));

Widget label(
  String text, {
  double size = 13,
  Color color = ink,
  FontWeight weight = FontWeight.w400,
  String? family,
  double? spacing,
  TextAlign align = TextAlign.left,
  int? lines,
}) => Text(
  text,
  textAlign: align,
  maxLines: lines,
  style: TextStyle(
    fontFamily: family ?? 'VoltioSans',
    fontSize: size,
    color: color,
    fontWeight: weight,
    letterSpacing: spacing,
    height: 1.25,
    decoration: TextDecoration.none,
  ),
);
Widget at(double x, double y, double w, Widget child, {double? h}) =>
    Positioned(left: x, top: y, width: w, height: h, child: child);
Widget action(
  String text,
  VoidCallback? onTap, {
  String? id,
  bool light = false,
  IconData? icon,
  double height = 48,
  double press = 0,
}) => Transform.scale(
  scale: 1 - .035 * press,
  child: SizedBox(
    height: height,
    child: Material(
      color: light ? Colors.white : blue,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        key: id == null ? null : ValueKey(id),
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (icon != null) ...[
              Icon(icon, size: 16, color: light ? ink : Colors.white),
              const SizedBox(width: 7),
            ],
            label(
              text,
              size: 13,
              color: light ? ink : Colors.white,
              weight: FontWeight.w700,
            ),
          ],
        ),
      ),
    ),
  ),
);
Widget rule() => const SizedBox(height: 1, child: ColoredBox(color: line));

class StatusBar extends StatelessWidget {
  const StatusBar({super.key, this.dark = false});
  final bool dark;
  @override
  Widget build(BuildContext context) {
    final color = dark ? Colors.white : ink;
    return SizedBox(
      height: 46,
      child: Stack(
        children: [
          at(
            27,
            16,
            50,
            label('9:41', size: 13, color: color, weight: FontWeight.w700),
          ),
          Positioned(
            left: 137,
            top: 9,
            child: Container(
              width: 116,
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

class OrbitPainter extends CustomPainter {
  OrbitPainter(this.progress, this.time);
  final double progress, time;
  @override
  void paint(Canvas canvas, Size size) {
    final c = size.center(Offset.zero), r = size.width * .40;
    for (int i = 0; i < 3; i++) {
      canvas.drawCircle(
        c,
        r + 7 + i * 6 + 1.8 * math.sin(time * 2.8 - i),
        Paint()
          ..color = blue.withValues(alpha: .055 - i * .015)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 3,
      );
    }
    canvas.drawCircle(
      c,
      r,
      Paint()
        ..color = const Color(0xFFE9EEFF)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 10,
    );
    final p = Paint()
      ..shader = const SweepGradient(
        colors: [Color(0xFF93C0FF), blue, Color(0xFF6E95FF)],
      ).createShader(Rect.fromCircle(center: c, radius: r))
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke
      ..strokeWidth = 10;
    canvas.drawArc(
      Rect.fromCircle(center: c, radius: r),
      -math.pi / 2,
      math.pi * 2 * progress,
      false,
      p,
    );
    final angle = -math.pi / 2 + math.pi * 2 * progress;
    canvas.drawCircle(
      c + Offset(math.cos(angle), math.sin(angle)) * r,
      4.5,
      Paint()..color = Colors.white,
    );
  }

  @override
  bool shouldRepaint(OrbitPainter old) =>
      old.progress != progress || old.time != time;
}

class TickPainter extends CustomPainter {
  TickPainter(this.progress, {this.color = Colors.white, this.width = 4});
  final double progress, width;
  final Color color;
  @override
  void paint(Canvas c, Size s) {
    final path = Path()
      ..moveTo(s.width * .2, s.height * .50)
      ..lineTo(s.width * .43, s.height * .71)
      ..lineTo(s.width * .81, s.height * .28);
    final metric = path.computeMetrics().first;
    c.drawPath(
      metric.extractPath(0, metric.length * unit(progress)),
      Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = width
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round,
    );
  }

  @override
  bool shouldRepaint(TickPainter old) => old.progress != progress;
}
