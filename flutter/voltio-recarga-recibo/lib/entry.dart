import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter/services.dart';
import 'app.dart';
import 'charge_flow.dart';

Future<void> startVoltio() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  await SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
  final code = await rootBundle.loadString('assets/showcase_code.txt');
  LicenseRegistry.addLicense(() async* {
    final notice = await rootBundle.loadString('assets/fonts/NOTICE.txt');
    final license = await rootBundle.loadString(
      'assets/fonts/roboto_license.txt',
    );
    yield LicenseEntryWithLineBreaks([
      'Roboto',
      'Roboto Mono',
    ], '$notice\n\n$license');
  });
  runApp(VoltioRuntime(code: code));
}

class VoltioRuntime extends StatefulWidget {
  const VoltioRuntime({super.key, required this.code});
  final String code;
  @override
  State<VoltioRuntime> createState() => _VoltioRuntimeState();
}

class _VoltioRuntimeState extends State<VoltioRuntime>
    with SingleTickerProviderStateMixin {
  late final ChargeFlow flow;
  late final Ticker ticker;
  double last = 0;
  @override
  void initState() {
    super.initState();
    flow = ChargeFlow();
    if (const bool.fromEnvironment('AUTO_DEMO')) flow.demoAt(0);
    ticker = createTicker((duration) {
      final now = duration.inMicroseconds / 1000000;
      flow.tick((now - last).clamp(0, .1));
      last = now;
    })..start();
  }

  @override
  void dispose() {
    ticker.dispose();
    flow.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => VoltioApp(
    flow: flow,
    code: widget.code,
    showcase: const bool.fromEnvironment('SHOWCASE'),
  );
}
