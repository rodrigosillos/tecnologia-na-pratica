import 'package:flutter/material.dart';
import 'home_view.dart';
import 'light_controller.dart';

class CasaApp extends StatelessWidget {
  const CasaApp({super.key, required this.controller});
  final LightController controller;
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Casa inteligente | Tecnologia na Prática',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(fontFamily: 'VoltioSans', brightness: Brightness.dark,
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(seedColor: gold, brightness: Brightness.dark)),
    home: Scaffold(backgroundColor: const Color(0xFF141923),
      body: Center(child: FittedBox(fit: BoxFit.contain,
        child: SizedBox(width: 390, height: 844,
          child: HomeView(controller: controller))))),
  );
}
