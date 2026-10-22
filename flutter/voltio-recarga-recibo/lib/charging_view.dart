import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'charge_flow.dart';
import 'design.dart';
import 'receipt_view.dart';

class ChargingView extends StatelessWidget {
  const ChargingView({super.key, required this.flow});
  final ChargeFlow flow;
  bool modal(ChargeStage s) => [
    ChargeStage.confirm,
    ChargeStage.processing,
    ChargeStage.success,
  ].contains(s);
  Widget page(ChargeStage s, double elapsed) => switch (s) {
    ChargeStage.charging => HomeView(flow: flow),
    ChargeStage.completed => CompletedView(flow: flow, elapsed: elapsed),
    ChargeStage.summary => SummaryView(flow: flow),
    ChargeStage.receipt => ReceiptView(flow: flow, elapsed: elapsed),
    _ => SummaryView(flow: flow),
  };
  @override
  Widget build(BuildContext context) => AnimatedBuilder(
    animation: flow,
    builder: (context, _) {
      final dark = flow.stage == ChargeStage.receipt;
      final transition = ease(flow.elapsed / .44);
      final hasTransition =
          transition < 1 &&
          !modal(flow.stage) &&
          (!modal(flow.previous) || flow.stage == ChargeStage.receipt) &&
          flow.previous != flow.stage;
      return ColoredBox(
        color: dark ? const Color(0xFF14223D) : Colors.white,
        child: Stack(
          children: [
            if (hasTransition) Positioned.fill(child: page(flow.previous, 7)),
            Positioned.fill(
              child: Transform.translate(
                offset: Offset(0, hasTransition ? (1 - transition) * 844 : 0),
                child: page(flow.stage, flow.elapsed),
              ),
            ),
            if (modal(flow.stage))
              Positioned.fill(child: PaymentDialog(flow: flow)),
            Positioned(
              left: 0,
              right: 0,
              top: 0,
              child: StatusBar(
                dark: dark && (!hasTransition || transition > .97),
              ),
            ),
            Positioned(
              left: 128,
              bottom: 9,
              child: Container(
                width: 134,
                height: 4,
                decoration: BoxDecoration(
                  color: dark ? Colors.white : ink,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ),
            if (flow.isDemo)
              Positioned.fill(
                child: IgnorePointer(
                  child: CustomPaint(painter: DemoTouch(flow.clock)),
                ),
              ),
          ],
        ),
      );
    },
  );
}

class HomeView extends StatelessWidget {
  const HomeView({super.key, required this.flow});
  final ChargeFlow flow;
  @override
  Widget build(BuildContext context) {
    final p = flow.clock >= 23.05 ? 0.0 : flow.progress;
    final percent = (62 + 18 * p).round();
    return ColoredBox(
      color: Colors.white,
      child: Stack(
        children: [
          at(
            22,
            66,
            346,
            Row(
              children: [
                Container(
                  width: 31,
                  height: 31,
                  decoration: BoxDecoration(
                    color: blue,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(
                    Icons.bolt_rounded,
                    color: Colors.white,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 9),
                label(
                  'VOLTIO',
                  size: 17,
                  weight: FontWeight.w700,
                  spacing: 1.5,
                ),
                const Spacer(),
                Container(
                  width: 30,
                  height: 30,
                  decoration: const BoxDecoration(
                    color: sheet,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.more_horiz_rounded,
                    color: ink,
                    size: 19,
                  ),
                ),
              ],
            ),
          ),
          at(
            22,
            119,
            346,
            Row(
              children: [
                const Icon(Icons.location_on_outlined, size: 15, color: muted),
                const SizedBox(width: 5),
                label('Estação Beira-Rio', size: 13, weight: FontWeight.w500),
                const Spacer(),
                const Icon(
                  Icons.keyboard_arrow_down_rounded,
                  size: 17,
                  color: muted,
                ),
              ],
            ),
          ),
          at(
            22,
            155,
            346,
            Row(
              children: [
                _chip('CCS2 · Vaga 04', false),
                const SizedBox(width: 8),
                _chip('Recarga rápida', true),
              ],
            ),
          ),
          Positioned(
            left: 20,
            top: 202,
            width: 350,
            height: 265,
            child: Container(
              decoration: BoxDecoration(
                color: const Color(0xFFF5F7FC),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(color: const Color(0xFFEEF1F7)),
              ),
              child: Stack(
                children: [
                  at(
                    18,
                    18,
                    314,
                    Row(
                      children: [
                        label(
                          'Recarga ao vivo',
                          size: 15,
                          weight: FontWeight.w700,
                        ),
                        const Spacer(),
                        Container(
                          width: 6,
                          height: 6,
                          decoration: BoxDecoration(
                            color: const Color(0xFF29B183).withValues(
                              alpha: .55 + .45 * math.sin(flow.clock * 3).abs(),
                            ),
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 5),
                        label('Conectado', size: 10, color: muted),
                      ],
                    ),
                  ),
                  Positioned(
                    left: 17,
                    top: 63,
                    width: 316,
                    height: 150,
                    child: CustomPaint(painter: EnergyPulsePainter(flow.clock)),
                  ),
                  Positioned(
                    left: 18,
                    top: 61,
                    width: 314,
                    height: 150,
                    child: DecoratedBox(
                      decoration: const BoxDecoration(
                        gradient: RadialGradient(
                          colors: [Color(0x19254BFF), Color(0x00254BFF)],
                        ),
                      ),
                      child: Transform.translate(
                        offset: Offset(0, 1.4 * math.sin(flow.clock * 1.8)),
                        child: Image.asset(
                          'assets/car_blue.png',
                          fit: BoxFit.contain,
                        ),
                      ),
                    ),
                  ),
                  at(
                    118,
                    114,
                    114,
                    label(
                      '$percent%',
                      size: 25,
                      color: Colors.white,
                      weight: FontWeight.w500,
                      align: TextAlign.center,
                    ),
                  ),
                  at(
                    25,
                    216,
                    300,
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        label(
                          '$percent% de carga',
                          size: 12,
                          weight: FontWeight.w500,
                        ),
                        label(
                          'Autonomia: ${(234 + p * 67).round()} km',
                          size: 12,
                          weight: FontWeight.w500,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          at(
            22,
            493,
            346,
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                label('Limite de recarga', color: muted, size: 12),
                label('80%', weight: FontWeight.w700),
              ],
            ),
          ),
          at(
            22,
            519,
            346,
            ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: LinearProgressIndicator(
                value: (62 + 18 * p) / 100,
                minHeight: 5,
                color: blue,
                backgroundColor: const Color(0xFFEDF0F6),
              ),
            ),
          ),
          at(
            22,
            557,
            346,
            _detail(
              Icons.bolt_outlined,
              'Energia fornecida',
              '${(38.7 + 11.7 * p).toStringAsFixed(1).replaceAll('.', ',')} kWh',
            ),
          ),
          at(
            22,
            594,
            346,
            _detail(
              Icons.schedule_rounded,
              'Tempo de recarga',
              '${(37 + 8 * p).round()} min',
            ),
          ),
          at(
            22,
            631,
            346,
            _detail(
              Icons.receipt_long_outlined,
              'Custo da recarga',
              ChargingSession.money(
                ((38.7 + 11.7 * p) * 35).round() + ChargingSession.serviceCents,
              ),
            ),
          ),
          at(
            22,
            690,
            346,
            action(
              'Encerrar recarga',
              flow.stopCharging,
              id: 'finish-charging',
              press: flow.buttonPress('finish-charging'),
              icon: Icons.power_settings_new_rounded,
            ),
          ),
          Positioned(
            left: 80,
            top: 768,
            width: 230,
            height: 43,
            child: Container(
              decoration: BoxDecoration(
                color: const Color(0xFF121724),
                borderRadius: BorderRadius.circular(24),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _nav(Icons.home_rounded, true),
                  _nav(Icons.bolt_rounded, false),
                  _nav(Icons.receipt_long_outlined, false),
                  _nav(Icons.person_outline_rounded, false),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _nav(IconData icon, bool active) => Container(
    width: 31,
    height: 31,
    decoration: BoxDecoration(
      color: active ? Colors.white : Colors.transparent,
      shape: BoxShape.circle,
    ),
    child: Icon(icon, size: 16, color: active ? ink : const Color(0xFFA5ACB9)),
  );
  Widget _chip(String text, bool active) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 7),
    decoration: BoxDecoration(
      color: active ? blue : sheet,
      borderRadius: BorderRadius.circular(9),
    ),
    child: Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (active) ...[
          const Icon(Icons.bolt_rounded, size: 12, color: Colors.white),
          const SizedBox(width: 3),
        ],
        label(
          text,
          size: 10,
          color: active ? Colors.white : muted,
          weight: FontWeight.w500,
        ),
      ],
    ),
  );
  Widget _detail(IconData icon, String a, String b) => Row(
    children: [
      Icon(icon, size: 17, color: muted),
      const SizedBox(width: 9),
      label(a, size: 12, color: muted),
      const Spacer(),
      label(b, size: 12, weight: FontWeight.w500),
    ],
  );
}

class CompletedView extends StatelessWidget {
  const CompletedView({super.key, required this.flow, required this.elapsed});
  final ChargeFlow flow;
  final double elapsed;
  @override
  Widget build(BuildContext context) => ColoredBox(
    color: Colors.white,
    child: Stack(
      children: [
        at(
          22,
          84,
          346,
          label(
            'Recarga concluída',
            size: 20,
            weight: FontWeight.w700,
            align: TextAlign.center,
          ),
        ),
        at(
          22,
          117,
          346,
          label(
            'Tudo pronto para a próxima viagem.',
            size: 12,
            color: muted,
            align: TextAlign.center,
          ),
        ),
        Positioned(
          left: 80,
          top: 208,
          width: 230,
          height: 230,
          child: CustomPaint(
            painter: OrbitPainter(.8 * ease(elapsed / 1.2), elapsed),
          ),
        ),
        at(
          95,
          280,
          200,
          label(
            '${(80 * ease(elapsed / 1.1)).round()}%',
            size: 48,
            weight: FontWeight.w700,
            align: TextAlign.center,
          ),
        ),
        at(
          95,
          341,
          200,
          label(
            'Carga da bateria',
            size: 12,
            color: muted,
            align: TextAlign.center,
          ),
        ),
        at(
          109,
          475,
          172,
          Container(
            padding: const EdgeInsets.symmetric(vertical: 8),
            decoration: BoxDecoration(
              color: const Color(0xFFEEF2FF),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.bolt_rounded, color: blue, size: 15),
                const SizedBox(width: 4),
                label(
                  'Desconecte e siga',
                  size: 11,
                  color: blue,
                  weight: FontWeight.w500,
                ),
              ],
            ),
          ),
        ),
        at(
          30,
          588,
          330,
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _stat('45', 'minutos'),
              _stat('301', 'km de autonomia'),
              _stat(
                ChargingSession.money(ChargingSession.totalCents),
                'custo total',
              ),
            ],
          ),
        ),
        at(
          22,
          718,
          346,
          action(
            'Ver resumo da recarga',
            flow.viewSummary,
            id: 'summary',
            press: flow.buttonPress('summary'),
            icon: Icons.arrow_forward_rounded,
          ),
        ),
      ],
    ),
  );
  Widget _stat(String a, String b) => Column(
    children: [
      label(a, size: 23, weight: FontWeight.w700),
      const SizedBox(height: 5),
      label(b, size: 11, color: muted),
    ],
  );
}

class SummaryView extends StatefulWidget {
  const SummaryView({super.key, required this.flow});
  final ChargeFlow flow;
  @override
  State<SummaryView> createState() => _SummaryViewState();
}

class _SummaryViewState extends State<SummaryView> {
  late final ScrollController scroll;
  ChargeFlow get flow => widget.flow;

  double get demoOffset => 122 * ease((flow.clock - 9.3) / 1.15);

  @override
  void initState() {
    super.initState();
    scroll = ScrollController(
      initialScrollOffset: flow.isDemo ? demoOffset : 0,
    );
    flow.addListener(syncDemoScroll);
  }

  void syncDemoScroll() {
    if (!flow.isDemo || !scroll.hasClients) return;
    final target = demoOffset.clamp(0.0, scroll.position.maxScrollExtent);
    if ((scroll.offset - target).abs() > .01) scroll.jumpTo(target);
  }

  @override
  void didUpdateWidget(covariant SummaryView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.flow != flow) {
      oldWidget.flow.removeListener(syncDemoScroll);
      flow.addListener(syncDemoScroll);
    }
  }

  @override
  void dispose() {
    flow.removeListener(syncDemoScroll);
    scroll.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => ColoredBox(
    color: Colors.white,
    child: Stack(
      children: [
        at(
          22,
          70,
          346,
          Row(
            children: [
              const Icon(Icons.chevron_left_rounded, size: 22),
              const SizedBox(width: 8),
              label('Resumo da recarga', size: 18, weight: FontWeight.w700),
            ],
          ),
        ),
        Positioned(
          left: 0,
          right: 0,
          top: 112,
          height: 694,
          child: RawScrollbar(
            controller: scroll,
            thumbVisibility:
                flow.isDemo && flow.clock >= 9.3 && flow.clock <= 10.9,
            thickness: 3,
            radius: const Radius.circular(3),
            thumbColor: const Color(0x806E7787),
            child: SingleChildScrollView(
              key: const ValueKey('summary-scroll'),
              controller: scroll,
              physics: const BouncingScrollPhysics(),
              child: SizedBox(
                width: 390,
                height: 816,
                child: Stack(
                  children: [
                    _scrollAt(
                      22,
                      116,
                      346,
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF3F6FF),
                          borderRadius: BorderRadius.circular(17),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(
                                  Icons.check_circle_rounded,
                                  color: blue,
                                  size: 18,
                                ),
                                const SizedBox(width: 6),
                                label(
                                  'Recarga concluída',
                                  size: 12,
                                  weight: FontWeight.w700,
                                ),
                                const Spacer(),
                                label(
                                  '80%',
                                  size: 13,
                                  color: blue,
                                  weight: FontWeight.w700,
                                ),
                              ],
                            ),
                            const SizedBox(height: 13),
                            ClipRRect(
                              borderRadius: BorderRadius.circular(3),
                              child: const LinearProgressIndicator(
                                value: .8,
                                color: blue,
                                backgroundColor: Color(0xFFDFE6FF),
                                minHeight: 5,
                              ),
                            ),
                            const SizedBox(height: 16),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                _metric('45 min', 'Duração'),
                                _metric('50,4 kWh', 'Fornecidos'),
                                _metric('+301 km', 'Autonomia'),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                    _scrollAt(
                      22,
                      272,
                      346,
                      label(
                        'Estação Beira-Rio',
                        size: 14,
                        weight: FontWeight.w700,
                      ),
                    ),
                    _scrollAt(
                      22,
                      298,
                      346,
                      label('Vaga 04 · CCS2 · 150 kW', size: 11, color: muted),
                    ),
                    _scrollAt(22, 329, 346, rule()),
                    _scrollAt(
                      22,
                      351,
                      346,
                      _pair(
                        'Energia · 50,4 kWh × R\$ 0,35',
                        ChargingSession.money(ChargingSession.energyCents),
                      ),
                    ),
                    _scrollAt(
                      22,
                      383,
                      346,
                      _pair(
                        'Taxa de serviço',
                        ChargingSession.money(ChargingSession.serviceCents),
                      ),
                    ),
                    _scrollAt(22, 417, 346, rule()),
                    _scrollAt(
                      22,
                      439,
                      346,
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          label('Total', size: 16, weight: FontWeight.w700),
                          label(
                            ChargingSession.money(ChargingSession.totalCents),
                            size: 21,
                            weight: FontWeight.w700,
                          ),
                        ],
                      ),
                    ),
                    _scrollAt(
                      22,
                      495,
                      346,
                      label(
                        'Forma de pagamento',
                        size: 13,
                        weight: FontWeight.w700,
                      ),
                    ),
                    _scrollAt(
                      22,
                      524,
                      346,
                      Column(
                        children: [
                          _method(0, 'Apple Pay', 'Pague com Face ID'),
                          const SizedBox(height: 1),
                          _method(1, 'Visa Crédito', 'Visa •••• 4821'),
                          const SizedBox(height: 1),
                          _method(
                            2,
                            'Cartão de débito',
                            'Mastercard •••• 7310',
                          ),
                        ],
                      ),
                    ),
                    _scrollAt(
                      22,
                      691,
                      346,
                      Row(
                        children: [
                          const Icon(
                            Icons.lock_outline_rounded,
                            size: 12,
                            color: muted,
                          ),
                          const SizedBox(width: 5),
                          label(
                            'Demonstração · sem cobrança real',
                            size: 10,
                            color: muted,
                          ),
                        ],
                      ),
                    ),
                    _scrollAt(
                      22,
                      725,
                      346,
                      action(
                        'Pagar ${ChargingSession.money(ChargingSession.totalCents)}',
                        flow.requestPayment,
                        id: 'pay',
                        press: flow.buttonPress('pay'),
                        icon: Icons.arrow_forward_rounded,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    ),
  );
  Widget _scrollAt(double x, double y, double w, Widget child) =>
      at(x, 4 + (y - 116) * 1.2, w, child);
  Widget _metric(String a, String b) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      label(a, size: 14, weight: FontWeight.w700),
      const SizedBox(height: 4),
      label(b, size: 10, color: muted),
    ],
  );
  Widget _pair(String a, String b) => Row(
    mainAxisAlignment: MainAxisAlignment.spaceBetween,
    children: [
      label(a, size: 12, color: muted),
      label(b, size: 12, weight: FontWeight.w500),
    ],
  );
  Widget _method(int value, String a, String b) {
    final selected = flow.paymentMethod == value;
    return AnimatedContainer(
      duration: const Duration(milliseconds: 240),
      curve: Curves.easeOutCubic,
      height: 52,
      decoration: BoxDecoration(
        color: selected ? const Color(0xFFF0F4FF) : sheet,
        borderRadius: BorderRadius.circular(11),
        border: Border.all(
          color: selected ? const Color(0xFFCDD7FF) : const Color(0xFFF0F2F6),
        ),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          key: ValueKey('method-$value'),
          onTap: () => flow.selectMethod(value),
          borderRadius: BorderRadius.circular(11),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            child: Row(
              children: [
                PaymentMark(method: value),
                const SizedBox(width: 10),
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    label(a, size: 12, weight: FontWeight.w500),
                    const SizedBox(height: 3),
                    label(b, size: 10, color: muted),
                  ],
                ),
                const Spacer(),
                AnimatedScale(
                  scale: selected ? 1.10 : 1.0,
                  duration: const Duration(milliseconds: 220),
                  curve: Curves.easeOutBack,
                  child: Icon(
                    selected
                        ? Icons.radio_button_checked_rounded
                        : Icons.radio_button_off_rounded,
                    size: 18,
                    color: selected ? blue : const Color(0xFFC5CBD6),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class PaymentMark extends StatelessWidget {
  const PaymentMark({super.key, required this.method});
  final int method;
  @override
  Widget build(BuildContext context) => SizedBox(
    width: 38,
    height: 25,
    child: Center(
      child: switch (method) {
        0 => const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.apple, size: 17, color: Colors.black),
            Text(
              'Pay',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: Colors.black,
              ),
            ),
          ],
        ),
        1 => const Text(
          'VISA',
          style: TextStyle(
            fontSize: 15,
            fontStyle: FontStyle.italic,
            fontWeight: FontWeight.w900,
            color: Color(0xFF16357A),
            letterSpacing: -.7,
          ),
        ),
        _ => const CustomPaint(size: Size(34, 22), painter: MastercardMark()),
      },
    ),
  );
}

class MastercardMark extends CustomPainter {
  const MastercardMark();
  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawCircle(
      const Offset(12, 11),
      9,
      Paint()..color = const Color(0xFFEB001B),
    );
    canvas.drawCircle(
      const Offset(23, 11),
      9,
      Paint()..color = const Color(0xF5F79E1B),
    );
  }

  @override
  bool shouldRepaint(MastercardMark old) => false;
}

class EnergyPulsePainter extends CustomPainter {
  EnergyPulsePainter(this.time);
  final double time;
  @override
  void paint(Canvas canvas, Size size) {
    final center = size.center(Offset.zero);
    for (var i = 0; i < 2; i++) {
      final phase = (time * .48 + i * .5) % 1;
      canvas.drawOval(
        Rect.fromCenter(
          center: center,
          width: 284 + phase * 25,
          height: 119 + phase * 18,
        ),
        Paint()
          ..color = blue.withValues(alpha: .15 * (1 - phase))
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2.2,
      );
    }
    final a = time * 1.2;
    for (var i = 0; i < 2; i++) {
      final angle = a + i * math.pi;
      final p = center + Offset(149 * math.cos(angle), 66 * math.sin(angle));
      canvas.drawCircle(p, 3.0, Paint()..color = const Color(0xFF89B8FF));
    }
  }

  @override
  bool shouldRepaint(EnergyPulsePainter old) => old.time != time;
}

class PaymentDialog extends StatelessWidget {
  const PaymentDialog({super.key, required this.flow});
  final ChargeFlow flow;
  @override
  Widget build(BuildContext context) {
    final confirm = flow.stage == ChargeStage.confirm;
    final processing = flow.stage == ChargeStage.processing;
    final t = ease(flow.elapsed / .25);
    return ColoredBox(
      color: Colors.black.withValues(alpha: .40 * (confirm ? t : 1)),
      child: Center(
        child: Transform.scale(
          scale: confirm ? .92 + .08 * t : 1,
          child: Container(
            width: 316,
            height: confirm ? 246 : 233,
            padding: const EdgeInsets.all(23),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(23),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x20000000),
                  blurRadius: 32,
                  offset: Offset(0, 12),
                ),
              ],
            ),
            child: confirm
                ? Column(
                    children: [
                      label(
                        'Confirmar pagamento',
                        size: 16,
                        weight: FontWeight.w700,
                      ),
                      const SizedBox(height: 9),
                      label('Estação Beira-Rio', size: 10, color: muted),
                      const SizedBox(height: 15),
                      label(
                        ChargingSession.money(ChargingSession.totalCents),
                        size: 35,
                        weight: FontWeight.w700,
                      ),
                      const SizedBox(height: 8),
                      label(flow.paymentLabel, size: 11, color: muted),
                      const Spacer(),
                      Row(
                        children: [
                          Expanded(
                            child: action(
                              'Cancelar',
                              flow.cancelPayment,
                              id: 'cancel',
                              press: flow.buttonPress('cancel'),
                              light: true,
                              height: 40,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: action(
                              'Sim, pagar',
                              flow.confirmPayment,
                              id: 'confirm-pay',
                              press: flow.buttonPress('confirm-pay'),
                              height: 40,
                            ),
                          ),
                        ],
                      ),
                    ],
                  )
                : Column(
                    children: [
                      const SizedBox(height: 4),
                      SizedBox(
                        width: 53,
                        height: 53,
                        child: processing
                            ? CustomPaint(painter: LoaderPainter(flow.elapsed))
                            : DecoratedBox(
                                decoration: const BoxDecoration(
                                  color: blue,
                                  shape: BoxShape.circle,
                                ),
                                child: Padding(
                                  padding: const EdgeInsets.all(10),
                                  child: CustomPaint(
                                    painter: TickPainter(flow.elapsed / .38),
                                  ),
                                ),
                              ),
                      ),
                      const SizedBox(height: 18),
                      label(
                        processing
                            ? 'Processando pagamento'
                            : 'Pagamento aprovado',
                        size: 16,
                        weight: FontWeight.w700,
                      ),
                      const SizedBox(height: 8),
                      label(
                        processing
                            ? 'Só um instante…'
                            : 'Sua recarga está paga.',
                        size: 11,
                        color: muted,
                      ),
                      const Spacer(),
                      if (!processing)
                        action(
                          'Imprimir recibo',
                          flow.printReceipt,
                          id: 'print-receipt',
                          press: flow.buttonPress('print-receipt'),
                          height: 40,
                        ),
                      if (processing)
                        label(
                          'Pagamento demonstrativo',
                          size: 10,
                          color: muted,
                        ),
                    ],
                  ),
          ),
        ),
      ),
    );
  }
}

class LoaderPainter extends CustomPainter {
  LoaderPainter(this.time);
  final double time;
  @override
  void paint(Canvas c, Size s) {
    c.drawCircle(
      s.center(Offset.zero),
      s.width / 2 - 5,
      Paint()
        ..color = const Color(0xFFE9EEFF)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3.5,
    );
    c.drawArc(
      Rect.fromLTWH(5, 5, s.width - 10, s.height - 10),
      time * 6 - math.pi / 2,
      math.pi * 1.1,
      false,
      Paint()
        ..color = blue
        ..strokeCap = StrokeCap.round
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3.5,
    );
  }

  @override
  bool shouldRepaint(LoaderPainter old) => old.time != time;
}

class DemoTouch extends CustomPainter {
  DemoTouch(this.time);
  final double time;

  // Ponteiro no estilo macOS: trajeto contínuo, aceleração e chegada suaves.
  static const trajectory = <(double, Offset)>[
    (0, Offset(343, 665)),
    (4.15, Offset(343, 665)),
    (4.86, Offset(322, 714)),
    (7.84, Offset(322, 714)),
    (8.56, Offset(322, 742)),
    (9.0, Offset(322, 742)),
    (9.55, Offset(344, 689)),
    (10.5, Offset(344, 689)),
    (11.06, Offset(346, 563)),
    (11.55, Offset(346, 563)),
    (12.16, Offset(346, 616)),
    (12.72, Offset(346, 616)),
    (13.36, Offset(322, 749)),
    (13.62, Offset(322, 749)),
    (14.17, Offset(302, 502)),
    (16.58, Offset(302, 502)),
    (17.16, Offset(302, 496)),
    (17.5, Offset(302, 496)),
    (18.12, Offset(350, 720)),
    (22.40, Offset(350, 720)),
    (22.91, Offset(337, 770)),
    (23.19, Offset(337, 770)),
    (23.88, Offset(343, 665)),
    (24, Offset(343, 665)),
  ];

  Offset get position {
    for (int i = 1; i < trajectory.length; i++) {
      final a = trajectory[i - 1], b = trajectory[i];
      if (time <= b.$1) {
        final u = unit((time - a.$1) / (b.$1 - a.$1));
        // Velocidade e aceleração nulas nas pontas, sem arrancadas bruscas.
        final t = u * u * u * (10 + u * (-15 + 6 * u));
        final delta = b.$2 - a.$2;
        final distance = delta.distance;
        if (distance < .01) return a.$2;
        final normal = Offset(-delta.dy, delta.dx) / distance;
        final bend = math.min(12.0, distance * .08) * (delta.dy > 0 ? -1 : 1);
        final c1 = a.$2 + delta * .32 + normal * bend;
        final c2 = b.$2 - delta * .28 + normal * (bend * .65);
        final v = 1 - t;
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
    final points = <double, Offset>{
      5.0: Offset(322, 714),
      8.7: Offset(322, 742),
      11.2: Offset(346, 563),
      12.3: Offset(346, 616),
      13.5: Offset(322, 749),
      14.3: Offset(302, 502),
      17.3: Offset(302, 496),
      23.05: Offset(337, 770),
    };
    for (final e in points.entries) {
      final dt = time - e.key;
      if (dt < -.04 || dt > .26) continue;
      final p = unit((dt + .04) / .30);
      final a = math.sin(p * math.pi);
      // Feedback discreto de gravação; a seta conserva cor e tamanho ao clicar.
      c.drawCircle(
        e.value,
        3 + p * 9,
        Paint()
          ..color = Colors.white.withValues(alpha: .55 * a)
          ..strokeWidth = 1.6
          ..style = PaintingStyle.stroke,
      );
      c.drawCircle(
        e.value,
        3 + p * 9,
        Paint()
          ..color = const Color(0xFF657080).withValues(alpha: .3 * a)
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
      ..lineTo(11.7, 21.0)
      ..lineTo(8.0, 13.0)
      ..lineTo(14.2, 13.0)
      ..close();
    c.drawShadow(arrow, const Color(0x55000000), 1.2, true);
    c.drawPath(arrow, Paint()..color = const Color(0xFF080808));
    c.drawPath(
      arrow,
      Paint()
        ..color = Colors.white
        ..style = PaintingStyle.stroke
        ..strokeJoin = StrokeJoin.round
        ..strokeWidth = 1.0,
    );
    c.restore();
  }

  @override
  bool shouldRepaint(DemoTouch old) => old.time != time;
}
