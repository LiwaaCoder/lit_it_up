/**
 * Socket Service - WebSocket Connection Manager
 *
 * Handles real-time communication with Node.js server:
 * - Connects to Socket.io server
 * - Listens for flash_pulse events
 * - Manages connection state
 * - Auto-reconnection on disconnect
 */

import 'package:socket_io_client/socket_io_client.dart' as IO;

class SocketService {
  // Singleton pattern
  static final SocketService _instance = SocketService._internal();
  factory SocketService() => _instance;
  SocketService._internal();

  IO.Socket? _socket;
  bool _isConnected = false;

  // ⚠️ IMPORTANT: Change this to your Node.js server IP address
  // For local testing on same machine: 'http://localhost:3000'
  // For testing on real device: 'http://YOUR_COMPUTER_IP:3000'
  static const String SERVER_URL = 'http://localhost:3000';

  // Callbacks
  Function(Map<String, dynamic>)? onFlashPulse;
  Function()? onConnected;
  Function()? onDisconnected;

  bool get isConnected => _isConnected;

  /// Initialize and connect to the server
  void connect() {
    if (_socket != null && _socket!.connected) {
      print('✅ Already connected to server');
      return;
    }

    print('🔌 Connecting to server: $SERVER_URL');

    // Configure Socket.io client
    _socket = IO.io(
      SERVER_URL,
      IO.OptionBuilder()
          .setTransports(['websocket']) // Use WebSocket transport
          .enableAutoConnect() // Auto-reconnect on disconnect
          .enableReconnection() // Enable reconnection attempts
          .setReconnectionAttempts(5) // Max reconnection attempts
          .setReconnectionDelay(1000) // 1 second between attempts
          .build(),
    );

    // Connection established
    _socket!.onConnect((_) {
      print('✅ Connected to server');
      _isConnected = true;

      // Identify as mobile client
      _socket!.emit('identify', {'type': 'mobile'});

      if (onConnected != null) {
        onConnected!();
      }
    });

    // Listen for flash_pulse event from server
    _socket!.on('flash_pulse', (data) {
      print('⚡ Flash pulse received: $data');

      if (onFlashPulse != null) {
        onFlashPulse!(data as Map<String, dynamic>);
      }
    });

    // Connection error
    _socket!.onConnectError((error) {
      print('❌ Connection error: $error');
      _isConnected = false;
    });

    // Disconnected from server
    _socket!.onDisconnect((_) {
      print('❌ Disconnected from server');
      _isConnected = false;

      if (onDisconnected != null) {
        onDisconnected!();
      }
    });

    // Reconnection attempt
    _socket!.onReconnectAttempt((attemptNumber) {
      print('🔄 Reconnection attempt #$attemptNumber');
    });

    // Reconnection success
    _socket!.onReconnect((_) {
      print('✅ Reconnected to server');
      _isConnected = true;

      if (onConnected != null) {
        onConnected!();
      }
    });
  }

  /// Disconnect from server
  void disconnect() {
    if (_socket != null) {
      print('🛑 Disconnecting from server');
      _socket!.disconnect();
      _socket!.dispose();
      _socket = null;
      _isConnected = false;
    }
  }

  /// Send manual trigger (for testing)
  void sendManualTrigger() {
    if (_socket != null && _socket!.connected) {
      _socket!.emit('manual_trigger', {});
      print('🔧 Manual trigger sent');
    } else {
      print('⚠️ Cannot send trigger - not connected');
    }
  }
}
