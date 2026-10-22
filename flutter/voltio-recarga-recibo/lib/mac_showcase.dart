import 'dart:convert';
import 'package:flutter/material.dart';
import 'charge_flow.dart';
import 'charging_view.dart';

/// Composição visual de macOS. O aplicativo é desenhado pelo motor Flutter.
class Showcase extends StatelessWidget {
  const Showcase({super.key, required this.flow, required this.code});
  final ChargeFlow flow;
  final String code;

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 540,
    height: 960,
    child: Stack(
      children: [
        Positioned.fill(
          child: RepaintBoundary(child: CustomPaint(painter: MacDesktop(code))),
        ),
        // O simulador termina antes da coluna do código.
        Positioned(
          left: 44,
          top: 176,
          width: 286,
          height: 604.46,
          child: FittedBox(
            fit: BoxFit.fill,
            child: SizedBox(
              width: 370,
              height: 782,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: const Color(0xFF101115),
                  borderRadius: BorderRadius.circular(52),
                  border: Border.all(
                    color: const Color(0xFF656972),
                    width: 1.1,
                  ),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x99000000),
                      blurRadius: 10,
                      offset: Offset(0, 8),
                    ),
                    BoxShadow(
                      color: Color(0xFF030409),
                      blurRadius: 3,
                      spreadRadius: 2,
                    ),
                  ],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(8),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(44),
                    child: FittedBox(
                      fit: BoxFit.fill,
                      child: SizedBox(
                        width: 390,
                        height: 844,
                        child: ChargingView(flow: flow),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    ),
  );
}

/// Recriação gráfica, sem representar uma captura ou compilação real no macOS.
class MacDesktop extends CustomPainter {
  MacDesktop(this.code)
    : sources = (jsonDecode(code) as Map<String, dynamic>)
          .cast<String, String>();
  final String code;
  final Map<String, String> sources;
  static const white = Color(0xFFE9EDF5);
  static const gray = Color(0xFFA5ADBC);

  double text(
    Canvas c,
    Offset at,
    String value,
    Color color,
    double size, {
    bool mono = false,
    double? width,
    FontWeight weight = FontWeight.w400,
  }) {
    final painter = TextPainter(
      text: TextSpan(
        text: value,
        style: TextStyle(
          fontFamily: mono ? 'ReceiptMono' : 'VoltioSans',
          fontSize: size,
          color: color,
          height: 1.45,
          fontWeight: weight,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout(maxWidth: width ?? double.infinity);
    painter.paint(c, at);
    return painter.height;
  }

  void icon(Canvas c, Offset at, IconData item, double size, Color color) {
    final p = TextPainter(
      text: TextSpan(
        text: String.fromCharCode(item.codePoint),
        style: TextStyle(
          fontFamily: item.fontFamily,
          fontSize: size,
          color: color,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    p.paint(c, at);
  }

  void round(Canvas c, Rect rect, Color color, double radius) => c.drawRRect(
    RRect.fromRectAndRadius(rect, Radius.circular(radius)),
    Paint()..color = color,
  );

  void lights(Canvas c, Offset at, {double radius = 3.5}) {
    for (int i = 0; i < 3; i++) {
      c.drawCircle(
        at + Offset(i * 11, 0),
        radius,
        Paint()
          ..color = const [
            Color(0xFFFF6058),
            Color(0xFFFFBD2E),
            Color(0xFF28C840),
          ][i],
      );
    }
  }

  @override
  void paint(Canvas c, Size s) {
    c.drawRect(
      Offset.zero & s,
      Paint()
        ..shader = const LinearGradient(
          begin: Alignment.topRight,
          end: Alignment.bottomLeft,
          colors: [
            Color(0xFF174E4C),
            Color(0xFF101A29),
            Color(0xFF292445),
            Color(0xFF11161E),
          ],
        ).createShader(Offset.zero & s),
    );

    round(c, const Rect.fromLTWH(10, 52, 520, 24), const Color(0xE8171C24), 5);
    icon(c, const Offset(19, 57), Icons.apple, 13, white);
    text(
      c,
      const Offset(39, 56),
      'Simulator',
      white,
      8.2,
      weight: FontWeight.w700,
    );
    text(
      c,
      const Offset(90, 56),
      'Arquivo   Editar   Dispositivo   Janela   Ajuda',
      white,
      8,
    );
    icon(c, const Offset(428, 57), Icons.wifi, 12, white);
    icon(c, const Offset(447, 57), Icons.battery_full, 12, white);
    text(c, const Offset(466, 56), 'Qui 22  9:41', white, 7.5);

    round(
      c,
      const Rect.fromLTWH(10, 83, 520, 718),
      const Color(0xFF1D1E24),
      10,
    );
    round(c, const Rect.fromLTWH(10, 83, 520, 28), const Color(0xFF292B32), 10);
    lights(c, const Offset(23, 97));
    text(c, const Offset(184, 89), 'Voltio — Visual Studio Code', gray, 8.5);
    icon(c, const Offset(497, 90), Icons.splitscreen_rounded, 13, gray);
    for (final (i, item) in <IconData>[
      Icons.file_copy_outlined,
      Icons.search,
      Icons.account_tree_outlined,
      Icons.play_circle_outline,
      Icons.extension_outlined,
    ].indexed) {
      icon(
        c,
        Offset(15, 127 + i * 33),
        item,
        13,
        i == 0 ? white : const Color(0xFF858C9C),
      );
    }
    icon(c, const Offset(15, 751), Icons.settings_outlined, 13, gray);

    // A janela do Simulator não encobre nenhuma linha do editor.
    round(
      c,
      const Rect.fromLTWH(39, 132, 293, 36),
      const Color(0xFF34353D),
      10,
    );
    lights(c, const Offset(51, 145), radius: 3.4);
    text(
      c,
      const Offset(91, 137),
      'iPhone · Voltio',
      white,
      9,
      weight: FontWeight.w500,
    );
    text(c, const Offset(91, 151), 'Simulator', gray, 6.5);
    icon(c, const Offset(263, 143), Icons.home_outlined, 13, gray);
    icon(c, const Offset(285, 143), Icons.screenshot, 13, gray);
    icon(c, const Offset(307, 143), Icons.rotate_right, 13, gray);

    // Editor estático: mesmo arquivo, mesmas linhas durante os 24 segundos.
    const filename = 'entry.dart';
    c.drawRect(
      const Rect.fromLTWH(338, 118, 186, 661),
      Paint()..color = const Color(0xFF191B22),
    );
    c.drawRect(
      const Rect.fromLTWH(338, 118, 186, 26),
      Paint()..color = const Color(0xFF252831),
    );
    c.drawRect(
      const Rect.fromLTWH(338, 118, 186, 1.5),
      Paint()..color = const Color(0xFF3E9BD1),
    );
    text(
      c,
      const Offset(346, 124),
      filename,
      const Color(0xFFB7DAF4),
      9.0,
      mono: true,
    );
    text(c, const Offset(346, 150), 'lib › $filename', gray, 7.6);
    c.save();
    c.clipRect(const Rect.fromLTWH(339, 170, 181, 604));
    final lines = sources[filename]!.split('\n');
    for (var i = 0; i < 45 && i < lines.length; i++) {
      final y = 170.0 + i * 13.4;
      text(
        c,
        Offset(341, y + 1),
        '${i + 1}',
        const Color(0xFF929CAF),
        7.0,
        mono: true,
      );
      codeLine(c, Offset(358, y), lines[i]);
    }
    c.restore();
    round(c, const Rect.fromLTWH(522, 170, 2, 112), const Color(0xFF535964), 1);
    c.drawRect(
      const Rect.fromLTWH(10, 780, 520, 21),
      Paint()..color = const Color(0xFF194361),
    );
    text(c, const Offset(22, 784), 'main    ✓ 0 erros', white, 7, mono: true);
    text(c, const Offset(380, 784), 'Dart  •  Flutter', white, 7, mono: true);


  }

  @override
  bool shouldRepaint(MacDesktop old) => old.code != code;

  double codeLine(Canvas canvas, Offset at, String line) {
    final tokens = RegExp(
      r"//.*$|'[^']*'|\b(?:void|if|return|final|const|true|false)\b|\b\d+(?:\.\d+)?\b|\b[A-Za-z_]\w*(?=\()",
    );
    final spans = <TextSpan>[];
    var from = 0;
    for (final match in tokens.allMatches(line)) {
      if (match.start > from) {
        spans.add(TextSpan(text: line.substring(from, match.start)));
      }
      final token = match.group(0)!;
      final color = token.startsWith('//')
          ? const Color(0xFF92B77D)
          : token.startsWith("'")
          ? const Color(0xFFF0C49C)
          : RegExp(r'^\d').hasMatch(token)
          ? const Color(0xFFC5E6AC)
          : RegExp(r'^(void|if|return|final|const|true|false)$').hasMatch(token)
          ? const Color(0xFFBF9DF3)
          : const Color(0xFF89D7EE);
      spans.add(
        TextSpan(
          text: token,
          style: TextStyle(color: color),
        ),
      );
      from = match.end;
    }
    spans.add(TextSpan(text: line.substring(from)));
    final painter = TextPainter(
      text: TextSpan(
        children: spans,
        style: const TextStyle(
          fontFamily: 'ReceiptMono',
          fontSize: 9.0,
          height: 1.45,
          color: Color(0xFFE8ECF5),
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    painter.paint(canvas, at);
    return painter.height;
  }
}
