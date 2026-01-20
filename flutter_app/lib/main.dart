/**
 * Let-It-Up Mobile App
 *
 * Interactive concert lighting application that synchronizes
 * your phone's flash and screen to the music beat.
 *
 * Entry point for the Flutter application.
 */

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'screens/concert_screen.dart';

void main() {
  // Ensure Flutter is initialized
  WidgetsFlutterBinding.ensureInitialized();

  // Set fullscreen mode (hide status bar and navigation bar)
  SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);

  // Lock orientation to portrait
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  runApp(const LetItUpApp());
}

class LetItUpApp extends StatelessWidget {
  const LetItUpApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Let-It-Up',
      debugShowCheckedModeBanner: false, // Remove debug banner
      theme: ThemeData(
        // Dark theme for concert environment
        brightness: Brightness.dark,
        primarySwatch: Colors.deepPurple,
        scaffoldBackgroundColor: const Color(0xFF121212),
        fontFamily: 'Roboto',
      ),
      home: const ConcertScreen(),
    );
  }
}
