import 'package:flutter/material.dart';

/// Ilustração vetorial própria, redesenhada pelo Flutter a cada ajuste.
class RoomPainter extends CustomPainter {
  RoomPainter({required this.power, required this.level, required this.kelvin});
  final double power, level;
  final int kelvin;

  @override
  void paint(Canvas canvas, Size size) {
    final c = canvas;
    c.save();
    c.scale(size.width / 342, size.height / 248);
    final temp = ((kelvin - 2700) / 3800).clamp(0.0, 1.0);
    final light = Color.lerp(
      const Color(0xFFFFBC6A),
      const Color(0xFFC3DEFF),
      temp,
    )!;
    final strength = power * (.22 + level * .78);
    Color lit(int dark, int bright) =>
        Color.lerp(Color(dark), Color(bright), strength)!;
    void rect(Rect r, Color color, [double radius = 0]) => c.drawRRect(
      RRect.fromRectAndRadius(r, Radius.circular(radius)),
      Paint()..color = color,
    );
    void poly(List<Offset> points, Color color) {
      c.drawPath(Path()..addPolygon(points, true), Paint()..color = color);
    }

    void line(Offset a, Offset b, Color color, [double width = 1]) =>
        c.drawLine(
          a,
          b,
          Paint()
            ..color = color
            ..strokeWidth = width,
        );
    // Parede principal, lateral e piso em perspectiva.
    rect(const Rect.fromLTWH(0, 0, 342, 248), const Color(0xFF171D2B));
    c.drawRect(
      const Rect.fromLTWH(0, 0, 342, 180),
      Paint()
        ..shader = LinearGradient(
          colors: [lit(0xFF252C3C, 0xFF8C8985), lit(0xFF151D2D, 0xFF625B53)],
        ).createShader(const Rect.fromLTWH(0, 0, 342, 180)),
    );
    poly([
      const Offset(0, 0),
      const Offset(61, 20),
      const Offset(61, 173),
      const Offset(0, 219),
    ], lit(0xFF1D2433, 0xFF77716B));
    poly([
      const Offset(0, 219),
      const Offset(61, 173),
      const Offset(342, 173),
      const Offset(342, 248),
      const Offset(0, 248),
    ], lit(0xFF1A1F2A, 0xFF5F4F40));
    line(
      const Offset(61, 20),
      const Offset(61, 173),
      const Color(0xFF929390).withValues(alpha: .12),
    );
    line(
      const Offset(61, 174),
      const Offset(342, 174),
      lit(0xFF303645, 0xFFABA08F),
      2,
    );
    for (var i = 0; i < 8; i++) {
      line(
        Offset(61 + i * 45, 176),
        Offset(-30 + i * 58, 248),
        Colors.black.withValues(alpha: .12),
      );
    }
    // Janela noturna e pequenos prédios, sem animação decorativa.
    rect(const Rect.fromLTWH(84, 28, 77, 89), lit(0xFF101521, 0xFFB5A38E), 4);
    rect(const Rect.fromLTWH(89, 33, 67, 79), const Color(0xFF162744), 2);
    c.drawCircle(
      const Offset(141, 48),
      6,
      Paint()..color = const Color(0xFFD4E0EE),
    );
    for (var i = 0; i < 5; i++) {
      final x = 91.0 + i * 13;
      final y = 79.0 + (i % 3) * 7;
      rect(Rect.fromLTWH(x, y, 11, 112 - y), const Color(0xFF0C172D));
      for (var j = 0; j < 3; j++) {
        rect(
          Rect.fromLTWH(x + 3, y + 6 + j * 9, 2, 3),
          const Color(0xFFBBA976).withValues(alpha: .6),
        );
      }
    }
    line(
      const Offset(122, 33),
      const Offset(122, 113),
      lit(0xFF111827, 0xFFC4B7A4),
      3,
    );
    // Quadros abstratos de autoria própria.
    rect(const Rect.fromLTWH(193, 39, 48, 60), lit(0xFF141922, 0xFFCBBDA5), 3);
    rect(const Rect.fromLTWH(197, 43, 40, 52), lit(0xFF2F3440, 0xFFE6D7BC), 1);
    c.drawCircle(
      const Offset(217, 62),
      12,
      Paint()..color = lit(0xFF414151, 0xFFB0774A),
    );
    poly([
      const Offset(198, 91),
      const Offset(211, 70),
      const Offset(228, 92),
    ], lit(0xFF252D37, 0xFF6D7863));
    rect(const Rect.fromLTWH(249, 52, 23, 32), lit(0xFF343A45, 0xFFBCAF97), 2);
    rect(const Rect.fromLTWH(252, 55, 17, 26), lit(0xFF232A37, 0xFFDFCFB3));
    // Tapete, sombra e sofá.
    c.drawOval(
      const Rect.fromLTWH(67, 181, 211, 52),
      Paint()..color = Colors.black.withValues(alpha: .24),
    );
    c.drawOval(
      const Rect.fromLTWH(65, 178, 218, 51),
      Paint()..color = lit(0xFF2B303B, 0xFFABA18E),
    );
    c.drawOval(
      const Rect.fromLTWH(75, 184, 196, 37),
      Paint()..color = lit(0xFF333742, 0xFFC2B6A1),
    );
    rect(const Rect.fromLTWH(93, 181, 8, 17), const Color(0xFF161C26), 2);
    rect(const Rect.fromLTWH(238, 181, 8, 17), const Color(0xFF161C26), 2);
    rect(
      const Rect.fromLTWH(91, 123, 160, 66),
      lit(0xFF343E50, 0xFF788E9B),
      17,
    );
    rect(const Rect.fromLTWH(99, 127, 70, 47), lit(0xFF424E60, 0xFF98ACB4), 10);
    rect(
      const Rect.fromLTWH(173, 127, 70, 47),
      lit(0xFF3F4B5C, 0xFF8DA2AD),
      10,
    );
    rect(const Rect.fromLTWH(95, 164, 151, 23), lit(0xFF303C4C, 0xFF78909E), 8);
    line(
      const Offset(171, 165),
      const Offset(171, 181),
      Colors.black.withValues(alpha: .15),
    );
    rect(const Rect.fromLTWH(83, 146, 22, 42), lit(0xFF475365, 0xFFA3B4B8), 9);
    rect(const Rect.fromLTWH(237, 146, 22, 42), lit(0xFF3B485A, 0xFF869FA8), 9);
    c.save();
    c.translate(120, 151);
    c.rotate(-.15);
    rect(const Rect.fromLTWH(-12, -15, 26, 28), lit(0xFF59524D, 0xFFE0B47F), 5);
    c.restore();
    c.save();
    c.translate(218, 152);
    c.rotate(.14);
    rect(const Rect.fromLTWH(-13, -15, 27, 28), lit(0xFF3D4B4C, 0xFFA8B5A1), 5);
    c.restore();
    // Mesa baixa com bandeja e objetos decorativos.
    // Apenas uma bandeja com duas peças decorativas na mesa.
    line(
      const Offset(151, 214),
      const Offset(150, 233),
      lit(0xFF25252B, 0xFF625345),
      4,
    );
    line(
      const Offset(202, 214),
      const Offset(205, 230),
      lit(0xFF25252B, 0xFF625345),
      4,
    );
    c.drawOval(
      const Rect.fromLTWH(133, 201, 89, 25),
      Paint()..color = lit(0xFF363334, 0xFFA98C68),
    );
    c.drawOval(
      const Rect.fromLTWH(133, 198, 89, 25),
      Paint()..color = lit(0xFF4A4440, 0xFFC4A57D),
    );
    c.drawOval(
      const Rect.fromLTWH(160, 204, 32, 10),
      Paint()..color = lit(0xFF252B31, 0xFF685E50),
    );
    rect(const Rect.fromLTWH(168, 197, 8, 11), lit(0xFF79736B, 0xFFEBD9B9), 3);
    c.drawCircle(
      const Offset(183, 205),
      4,
      Paint()..color = lit(0xFF40565A, 0xFF9BAD9D),
    );
    // Planta à esquerda.
    poly([
      const Offset(27, 183),
      const Offset(47, 183),
      const Offset(44, 205),
      const Offset(31, 205),
    ], lit(0xFF4E403C, 0xFFBB8C6A));
    line(
      const Offset(37, 187),
      const Offset(37, 142),
      lit(0xFF243D39, 0xFF749179),
      2,
    );
    for (final (x, y, angle) in [
      (30.0, 164.0, -.6),
      (44.0, 155.0, .6),
      (29.0, 147.0, -.4),
      (43.0, 139.0, .5),
    ]) {
      c.save();
      c.translate(x, y);
      c.rotate(angle);
      c.drawOval(
        const Rect.fromLTWH(-5, -10, 10, 21),
        Paint()..color = lit(0xFF2C4340, 0xFF7E9A7B),
      );
      c.restore();
    }
    // Luminária: feixe, halo e reflexos seguem os mesmos valores dos sliders.
    final source = const Offset(291, 101);
    if (power > .001) {
      c.drawOval(
        const Rect.fromLTWH(234, 41, 108, 134),
        Paint()
          ..shader = RadialGradient(
            colors: [
              light.withValues(alpha: strength * .65),
              light.withValues(alpha: 0),
            ],
          ).createShader(const Rect.fromLTWH(228, 35, 120, 145)),
      );
      final beam = Path()
        ..moveTo(276, 101)
        ..lineTo(245, 195)
        ..quadraticBezierTo(289, 216, 332, 194)
        ..lineTo(306, 101)
        ..close();
      c.drawPath(
        beam,
        Paint()
          ..shader = LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              light.withValues(alpha: strength * .36),
              light.withValues(alpha: strength * .03),
            ],
          ).createShader(const Rect.fromLTWH(245, 101, 87, 107)),
      );
      c.drawOval(
        const Rect.fromLTWH(244, 181, 94, 25),
        Paint()
          ..shader = RadialGradient(
            colors: [
              light.withValues(alpha: strength * .32),
              light.withValues(alpha: 0),
            ],
          ).createShader(const Rect.fromLTWH(242, 166, 100, 55)),
      );
    }
    line(
      const Offset(291, 95),
      const Offset(291, 198),
      lit(0xFF72716E, 0xFFD9C7A9),
      3,
    );
    c.drawOval(
      const Rect.fromLTWH(276, 194, 30, 7),
      Paint()..color = lit(0xFF454951, 0xFFAA9C86),
    );
    poly([
      const Offset(280, 75),
      const Offset(302, 75),
      const Offset(310, 103),
      const Offset(272, 103),
    ], Color.lerp(const Color(0xFF5D6067), light, .85 * power)!);
    c.drawOval(
      const Rect.fromLTWH(272, 99, 38, 7),
      Paint()
        ..color = Color.lerp(
          const Color(0xFF74757A),
          const Color(0xFFFFF1D7),
          power,
        )!,
    );
    c.drawCircle(source, 3, Paint()..color = light.withValues(alpha: power));
    // Banho de cor muito suave sobre a parede.
    if (strength > .001) {
      c.drawRect(
        const Rect.fromLTWH(61, 0, 281, 175),
        Paint()
          ..blendMode = BlendMode.softLight
          ..shader = RadialGradient(
            colors: [
              light.withValues(alpha: strength * .4),
              light.withValues(alpha: 0),
            ],
          ).createShader(const Rect.fromLTWH(155, 0, 210, 210)),
      );
    }
    c.restore();
  }

  @override
  bool shouldRepaint(RoomPainter old) =>
      old.power != power || old.level != level || old.kelvin != kelvin;
}
