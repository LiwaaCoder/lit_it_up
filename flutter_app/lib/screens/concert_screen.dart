/**
 * Concert Screen - Main UI for Let-It-Up
 *
 * Features:
 * - Dark fullscreen display
 * - Connection status indicator
 * - Flash effect (torch + screen color)
 * - Low-latency response to beat events
 */

import 'package:flutter/material.dart';
import 'package:torch_light/torch_light.dart';
import 'package:screen_brightness/screen_brightness.dart';
import '../services/socket_service.dart';
import 'dart:math';

class ConcertScreen extends StatefulWidget {
  const ConcertScreen({Key? key}) : super(key: key);

  @override
  State<ConcertScreen> createState() => _ConcertScreenState();
}

class _ConcertScreenState extends State<ConcertScreen>
    with SingleTickerProviderStateMixin {
  final SocketService _socketService = SocketService();
  bool _isConnected = false;
  bool _isFlashing = false;
  Color _flashColor = Colors.white;

  // Animation controller for smooth flash effect
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  // Torch availability
  bool _torchAvailable = false;

  @override
  void initState() {
    super.initState();

    // Initialize animation controller
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 150), // Fast fade out
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOut),
    );

    // Check torch availability
    _checkTorchAvailability();

    // Setup socket service callbacks
    _setupSocketCallbacks();

    // Connect to server
    _socketService.connect();
  }

  /// Check if device has flashlight/torch
  Future<void> _checkTorchAvailability() async {
    try {
      _torchAvailable = await TorchLight.isTorchAvailable();
      print('🔦 Torch available: $_torchAvailable');
    } catch (e) {
      print('⚠️ Error checking torch availability: $e');
      _torchAvailable = false;
    }
  }

  /// Setup socket service event callbacks
  void _setupSocketCallbacks() {
    // Connected to server
    _socketService.onConnected = () {
      if (mounted) {
        setState(() {
          _isConnected = true;
        });
      }
    };

    // Disconnected from server
    _socketService.onDisconnected = () {
      if (mounted) {
        setState(() {
          _isConnected = false;
        });
      }
    };

    // Flash pulse received - THE MAIN EVENT!
    _socketService.onFlashPulse = (data) {
      if (mounted) {
        _triggerFlashEffect();
      }
    };
  }

  /// Trigger the flash effect (torch + screen)
  Future<void> _triggerFlashEffect() async {
    if (_isFlashing) return; // Prevent overlapping flashes

    setState(() {
      _isFlashing = true;
      // Random color for variety (or use white for classic effect)
      _flashColor = _getRandomColor();
    });

    // Start fade-in animation
    _animationController.forward(from: 0.0);

    // Turn on torch
    if (_torchAvailable) {
      try {
        await TorchLight.enableTorch();
      } catch (e) {
        print('⚠️ Error enabling torch: $e');
      }
    }

    // Flash duration: 100ms
    await Future.delayed(const Duration(milliseconds: 100));

    // Turn off torch
    if (_torchAvailable) {
      try {
        await TorchLight.disableTorch();
      } catch (e) {
        print('⚠️ Error disabling torch: $e');
      }
    }

    // Fade out animation
    _animationController.reverse();

    // Wait for fade out to complete
    await Future.delayed(const Duration(milliseconds: 150));

    if (mounted) {
      setState(() {
        _isFlashing = false;
      });
    }
  }

  /// Get random color for flash effect
  Color _getRandomColor() {
    final random = Random();
    final colors = [
      Colors.white,
      Colors.red,
      Colors.blue,
      Colors.green,
      Colors.yellow,
      Colors.purple,
      Colors.orange,
      Colors.pink,
    ];
    return colors[random.nextInt(colors.length)];
  }

  @override
  void dispose() {
    _animationController.dispose();
    _socketService.disconnect();

    // Ensure torch is off
    if (_torchAvailable) {
      TorchLight.disableTorch().catchError((e) {
        print('⚠️ Error disabling torch on dispose: $e');
      });
    }

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF121212), // Dark background
      body: Stack(
        children: [
          // Main content
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Status indicator
                _buildStatusIndicator(),
                const SizedBox(height: 40),

                // Main message
                Text(
                  _isConnected
                      ? 'Waiting for the beat...'
                      : 'Connecting to server...',
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 24,
                    fontWeight: FontWeight.w300,
                    letterSpacing: 1.2,
                  ),
                  textAlign: TextAlign.center,
                ),

                const SizedBox(height: 20),

                // Connection status text
                Text(
                  _isConnected ? 'Connected ✅' : 'Disconnected ❌',
                  style: TextStyle(
                    color: _isConnected ? Colors.green : Colors.red,
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),

                // Debug: Manual trigger button (optional - remove in production)
                if (_isConnected) ...[
                  const SizedBox(height: 60),
                  ElevatedButton(
                    onPressed: () {
                      _socketService.sendManualTrigger();
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white24,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 30,
                        vertical: 15,
                      ),
                    ),
                    child: const Text(
                      'Manual Test Flash',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ],
              ],
            ),
          ),

          // Flash overlay effect
          if (_isFlashing)
            FadeTransition(
              opacity: _fadeAnimation,
              child: Container(
                color: _flashColor,
              ),
            ),
        ],
      ),
    );
  }

  /// Build connection status indicator
  Widget _buildStatusIndicator() {
    return Container(
      width: 20,
      height: 20,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: _isConnected ? Colors.green : Colors.red,
        boxShadow: _isConnected
            ? [
                BoxShadow(
                  color: Colors.green.withOpacity(0.5),
                  blurRadius: 10,
                  spreadRadius: 2,
                ),
              ]
            : null,
      ),
    );
  }
}
