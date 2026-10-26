import 'package:flutter/services.dart';

Future<void> loadFonts() async {
  final sans = FontLoader('VoltioSans');
  for (final f in [
    'roboto-regular.ttf',
    'roboto-medium.ttf',
    'roboto-bold.ttf',
  ]) {
    sans.addFont(rootBundle.load('assets/fonts/$f'));
  }
  await sans.load();
  await (FontLoader(
    'MaterialIcons',
  )..addFont(rootBundle.load('fonts/MaterialIcons-Regular.otf'))).load();
}
