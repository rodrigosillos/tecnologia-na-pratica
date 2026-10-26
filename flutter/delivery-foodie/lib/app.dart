import 'package:flutter/material.dart';
import 'delivery_view.dart';
import 'delivery_controller.dart';
import 'ui_kit.dart';

class DeliveryApp extends StatelessWidget {
  const DeliveryApp({
    super.key,
    required this.controller,
    this.captureKey,
  });
  final DeliveryController controller;
  final GlobalKey? captureKey;
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Foodie | Tecnologia na Prática',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(
      fontFamily: 'VoltioSans',
      brightness: Brightness.light,
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: brandPrimary,
        brightness: Brightness.light,
      ),
    ),
    home: Scaffold(
      backgroundColor: paper,
      resizeToAvoidBottomInset: false,
      body: Center(
        child: RepaintBoundary(
          key: captureKey,
          child: FittedBox(
            fit: BoxFit.contain,
            child: SizedBox(
                    width: 390,
                    height: 844,
                    child: DeliveryView(controller: controller),
                  ),
          ),
        ),
      ),
    ),
  );
}
