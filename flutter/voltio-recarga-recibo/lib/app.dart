import 'package:flutter/material.dart';
import 'charge_flow.dart';
import 'charging_view.dart';
import 'mac_showcase.dart';

class VoltioApp extends StatelessWidget {
  const VoltioApp({
    super.key,
    required this.flow,
    this.showcase = false,
    this.code = '',
    this.captureKey,
  });
  final ChargeFlow flow;
  final bool showcase;
  final String code;
  final GlobalKey? captureKey;
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Voltio',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      fontFamily: 'VoltioSans',
      brightness: Brightness.light,
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF254BFF)),
      useMaterial3: true,
    ),
    home: Scaffold(
      backgroundColor: const Color(0xFF11131A),
      body: Center(
        child: RepaintBoundary(
          key: captureKey,
          child: FittedBox(
            fit: BoxFit.contain,
            child: showcase
                ? Showcase(flow: flow, code: code)
                : SizedBox(
                    width: 390,
                    height: 844,
                    child: ChargingView(flow: flow),
                  ),
          ),
        ),
      ),
    ),
  );
}
