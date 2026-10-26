import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'app.dart';
import 'light_controller.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  LicenseRegistry.addLicense(() async* {
    final notice = await rootBundle.loadString('assets/fonts/NOTICE.txt');
    final license = await rootBundle.loadString(
      'assets/fonts/roboto_license.txt',
    );
    yield LicenseEntryWithLineBreaks([
      'Roboto',
      'Roboto Mono',
    ], '$notice\n$license');
  });
  runApp(const CasaRuntime());
}

class CasaRuntime extends StatefulWidget {
  const CasaRuntime({super.key});
  @override
  State<CasaRuntime> createState() => _CasaRuntimeState();
}

class _CasaRuntimeState extends State<CasaRuntime>
    with SingleTickerProviderStateMixin {
  final controller = LightController();
  late final Ticker ticker;
  double last = 0;
  @override
  void initState() {
    super.initState();
    ticker = createTicker((elapsed) {
      final now = elapsed.inMicroseconds / 1000000;
      if (const bool.fromEnvironment('AUTO_DEMO')) {
        controller.demoAt(now % 24);
      } else {
        controller.tick((now - last).clamp(0, .1));
      }
      last = now;
    })..start();
  }

  @override
  void dispose() {
    ticker.dispose();
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => CasaApp(
    controller: controller,
  );
}
