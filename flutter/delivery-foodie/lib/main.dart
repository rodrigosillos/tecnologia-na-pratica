import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'app.dart';
import 'delivery_controller.dart';
import 'ui_kit.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await loadDeliveryArt();
  LicenseRegistry.addLicense(() async* {
    final notice = await rootBundle.loadString('assets/fonts/NOTICE.txt');
    final license = await rootBundle.loadString(
      'assets/fonts/roboto_license.txt',
    );
    yield LicenseEntryWithLineBreaks([
      'Roboto',
    ], '$notice\n$license');
  });
  runApp(const DeliveryRuntime());
}

class DeliveryRuntime extends StatefulWidget {
  const DeliveryRuntime({super.key});
  @override
  State<DeliveryRuntime> createState() => _DeliveryRuntimeState();
}

class _DeliveryRuntimeState extends State<DeliveryRuntime>
    with SingleTickerProviderStateMixin {
  final controller = DeliveryController();
  late final Ticker ticker;
  double last = 0;
  @override
  void initState() {
    super.initState();
    ticker = createTicker((elapsed) {
      final now = elapsed.inMicroseconds / 1000000;
      if (const bool.fromEnvironment('AUTO_DEMO')) {
        controller.demoAt(now % 30);
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
  Widget build(BuildContext context) => DeliveryApp(
    controller: controller,
  );
}
