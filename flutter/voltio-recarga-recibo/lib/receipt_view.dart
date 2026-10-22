import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'charge_flow.dart';
import 'design.dart';

class ReceiptView extends StatelessWidget {
  const ReceiptView({super.key, required this.flow, required this.elapsed});
  final ChargeFlow flow;
  final double elapsed;
  @override
  Widget build(BuildContext context) {
    // A borda inferior sai primeiro, como na impressora térmica.
    final feed = Curves.easeInOutSine.transform(unit((elapsed - .40) / 3.2));
    final stampTime = unit((elapsed - 3.95) / .60);
    final stampScale = stampTime == 0
        ? 0.0
        : Curves.elasticOut.transform(stampTime);
    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFF14223D), Color(0xFF080F1A), Color(0xFF070C12)],
        ),
      ),
      child: Stack(
        children: [
          at(
            24,
            83,
            342,
            label(
              'Seu recibo',
              size: 21,
              weight: FontWeight.w700,
              color: Colors.white,
              align: TextAlign.center,
            ),
          ),
          at(
            24,
            115,
            342,
            label(
              'Estação Beira-Rio',
              size: 11,
              color: const Color(0xFFA6B2C7),
              align: TextAlign.center,
            ),
          ),
          // O papel desliza pela abertura, mantendo seu tamanho.
          Positioned(
            left: 37,
            top: 181,
            width: 316,
            height: 523,
            child: ClipRect(
              child: Align(
                alignment: Alignment.topCenter,
                child: Transform.translate(
                  offset: Offset(0, -505 * (1 - feed)),
                  child: SizedBox(
                    width: 316,
                    height: 505,
                    child: Stack(
                      children: [
                        const ReceiptPaper(),
                        if (stampTime > 0)
                          Positioned(
                            left: 33,
                            top: 305,
                            child: Transform.rotate(
                              angle: -.18 + (1 - stampTime) * .16,
                              child: Transform.scale(
                                scale: stampScale,
                                child: Opacity(
                                  opacity: unit(stampTime * 3),
                                  child: CustomPaint(
                                    size: const Size(90, 90),
                                    painter: PaidStamp(),
                                  ),
                                ),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
          Positioned(
            left: 23,
            top: 163,
            child: Container(
              width: 344,
              height: 25,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(13),
                gradient: const LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Color(0xFFF6F8FF),
                    Color(0xFFBAC5D8),
                    Color(0xFFE8EDF5),
                  ],
                ),
                border: Border.all(color: Colors.white.withValues(alpha: .65)),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x80000000),
                    blurRadius: 12,
                    offset: Offset(0, 6),
                  ),
                ],
              ),
              child: Center(
                child: Container(
                  width: 319,
                  height: 4,
                  decoration: BoxDecoration(
                    color: const Color(0xFF596577),
                    borderRadius: BorderRadius.circular(3),
                  ),
                ),
              ),
            ),
          ),
          at(
            28,
            749,
            160,
            TextButton.icon(
              key: const ValueKey('reprint'),
              onPressed: feed >= 1 ? flow.printReceipt : null,
              icon: const Icon(
                Icons.refresh_rounded,
                color: Color(0xFF9DAAC1),
                size: 16,
              ),
              label: label(
                'Reimprimir',
                size: 12,
                color: const Color(0xFF9DAAC1),
              ),
            ),
          ),
          at(
            206,
            749,
            155,
            action(
              'Concluir',
              feed >= 1 ? flow.finish : null,
              id: 'done',
              press: flow.buttonPress('done'),
              light: true,
              height: 42,
            ),
          ),
        ],
      ),
    );
  }
}

class ReceiptPaper extends StatelessWidget {
  const ReceiptPaper({super.key});
  Widget mono(
    String s, {
    double size = 9,
    FontWeight weight = FontWeight.w400,
    TextAlign align = TextAlign.left,
  }) => label(
    s,
    size: size,
    family: 'ReceiptMono',
    color: const Color(0xFF34363C),
    weight: weight,
    align: align,
  );
  Widget pair(double y, String a, String b, {double size = 9}) => at(
    22,
    y,
    272,
    Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        mono(a, size: size),
        mono(b, size: size),
      ],
    ),
  );
  @override
  Widget build(BuildContext context) => ClipPath(
    clipper: ReceiptEdge(),
    child: ColoredBox(
      color: const Color(0xFFFFFEF9),
      child: Stack(
        children: [
          Positioned.fill(child: CustomPaint(painter: PaperGrain())),
          at(
            20,
            25,
            276,
            label(
              'V O L T I O',
              size: 20,
              weight: FontWeight.w700,
              align: TextAlign.center,
            ),
          ),
          at(
            20,
            55,
            276,
            mono(
              'RECARGA DE VEÍCULO ELÉTRICO',
              size: 8,
              align: TextAlign.center,
            ),
          ),
          at(
            20,
            72,
            276,
            mono(
              'Estação Beira-Rio · Vaga 04',
              size: 8,
              align: TextAlign.center,
            ),
          ),
          at(
            22,
            97,
            272,
            mono('--------------------------------------', size: 11),
          ),
          pair(120, 'RECIBO', ChargingSession.receiptId, size: 8.5),
          pair(141, 'DATA', '22/10/2026  14:30'),
          pair(162, 'SESSÃO', '45 min · CCS2 · 150 kW'),
          at(
            22,
            187,
            272,
            mono('--------------------------------------', size: 11),
          ),
          pair(212, 'Energia fornecida', '50,40 kWh'),
          pair(
            234,
            'Tarifa / kWh',
            ChargingSession.money(ChargingSession.rateCents),
          ),
          pair(
            256,
            'Valor da energia',
            ChargingSession.money(ChargingSession.energyCents),
          ),
          pair(
            278,
            'Taxa de serviço',
            ChargingSession.money(ChargingSession.serviceCents),
          ),
          at(
            22,
            304,
            272,
            mono('--------------------------------------', size: 11),
          ),
          at(
            171,
            326,
            124,
            label(
              ChargingSession.money(ChargingSession.totalCents),
              size: 25,
              weight: FontWeight.w700,
              align: TextAlign.right,
            ),
          ),
          at(
            193,
            359,
            101,
            mono('TOTAL PAGO', size: 9, align: TextAlign.right),
          ),
          at(
            22,
            398,
            272,
            CustomPaint(size: const Size(272, 43), painter: ReceiptBarcode()),
          ),
          at(
            20,
            448,
            276,
            mono(ChargingSession.receiptId, size: 8, align: TextAlign.center),
          ),
          at(
            20,
            474,
            276,
            mono(
              'Obrigado por recarregar com a Voltio.',
              size: 8,
              align: TextAlign.center,
            ),
          ),
        ],
      ),
    ),
  );
}

class ReceiptEdge extends CustomClipper<Path> {
  @override
  Path getClip(Size s) {
    final p = Path()
      ..moveTo(0, 0)
      ..lineTo(s.width, 0)
      ..lineTo(s.width, s.height - 5);
    const teeth = 40;
    for (int i = teeth; i > 0; i--) {
      p.lineTo((i - .5) * s.width / teeth, s.height);
      p.lineTo((i - 1) * s.width / teeth, s.height - 5);
    }
    return p..close();
  }

  @override
  bool shouldReclip(ReceiptEdge old) => false;
}

class PaperGrain extends CustomPainter {
  @override
  void paint(Canvas c, Size s) {
    final rng = math.Random(41);
    for (int i = 0; i < 2900; i++) {
      c.drawCircle(
        Offset(rng.nextDouble() * s.width, rng.nextDouble() * s.height),
        rng.nextDouble() * .34,
        Paint()..color = const Color(0x0B554A34),
      );
    }
    c.drawRect(
      Rect.fromLTWH(0, 0, s.width, 15),
      Paint()
        ..shader = const LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0x17000000), Color(0x00000000)],
        ).createShader(Rect.fromLTWH(0, 0, s.width, 15)),
    );
  }

  @override
  bool shouldRepaint(PaperGrain old) => false;
}

class PaidStamp extends CustomPainter {
  @override
  void paint(Canvas c, Size s) {
    const col = Color(0xB33973B8);
    final p = Paint()
      ..color = col
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.7;
    c.drawCircle(s.center(Offset.zero), 40, p);
    c.drawCircle(s.center(Offset.zero), 35, p..strokeWidth = .7);
    final tp = TextPainter(
      text: const TextSpan(
        text: 'PAGO',
        style: TextStyle(
          fontFamily: 'ReceiptMono',
          fontWeight: FontWeight.w700,
          fontSize: 22,
          color: col,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    tp.paint(c, Offset((s.width - tp.width) / 2, 29));
    final date = TextPainter(
      text: const TextSpan(
        text: '22 OUT 2026',
        style: TextStyle(fontFamily: 'ReceiptMono', fontSize: 6.5, color: col),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    date.paint(c, Offset((s.width - date.width) / 2, 57));
    c.drawLine(const Offset(20, 26), const Offset(70, 26), p);
  }

  @override
  bool shouldRepaint(PaidStamp old) => false;
}

class ReceiptBarcode extends CustomPainter {
  // Code 128 B, including start, checksum and stop patterns.
  static const patterns = [
    '212222',
    '222122',
    '222221',
    '121223',
    '121322',
    '131222',
    '122213',
    '122312',
    '132212',
    '221213',
    '221312',
    '231212',
    '112232',
    '122132',
    '122231',
    '113222',
    '123122',
    '123221',
    '223211',
    '221132',
    '221231',
    '213212',
    '223112',
    '312131',
    '311222',
    '321122',
    '321221',
    '312212',
    '322112',
    '322211',
    '212123',
    '212321',
    '232121',
    '111323',
    '131123',
    '131321',
    '112313',
    '132113',
    '132311',
    '211313',
    '231113',
    '231311',
    '112133',
    '112331',
    '132131',
    '113123',
    '113321',
    '133121',
    '313121',
    '211331',
    '231131',
    '213113',
    '213311',
    '213131',
    '311123',
    '311321',
    '331121',
    '312113',
    '312311',
    '332111',
    '314111',
    '221411',
    '431111',
    '111224',
    '111422',
    '121124',
    '121421',
    '141122',
    '141221',
    '112214',
    '112412',
    '122114',
    '122411',
    '142112',
    '142211',
    '241211',
    '221114',
    '413111',
    '241112',
    '134111',
    '111242',
    '121142',
    '121241',
    '114212',
    '124112',
    '124211',
    '411212',
    '421112',
    '421211',
    '212141',
    '214121',
    '412121',
    '111143',
    '111341',
    '131141',
    '114113',
    '114311',
    '411113',
    '411311',
    '113141',
    '114131',
    '311141',
    '411131',
    '211412',
    '211214',
    '211232',
    '2331112',
  ];
  @override
  void paint(Canvas c, Size s) {
    final data = ChargingSession.receiptId.codeUnits
        .map((x) => x - 32)
        .toList();
    int sum = 104;
    for (int i = 0; i < data.length; i++) {
      sum += data[i] * (i + 1);
    }
    final symbols = [104, ...data, sum % 103, 106];
    final widths = symbols
        .expand((v) => patterns[v].split('').map(int.parse))
        .toList();
    final module = s.width / (widths.fold<int>(0, (a, b) => a + b) + 20);
    double x = module * 10;
    for (int i = 0; i < widths.length; i++) {
      if (i.isEven) {
        c.drawRect(
          Rect.fromLTWH(x, 0, widths[i] * module, s.height),
          Paint()..color = const Color(0xFF24272D),
        );
      }
      x += widths[i] * module;
    }
  }

  @override
  bool shouldRepaint(ReceiptBarcode old) => false;
}
