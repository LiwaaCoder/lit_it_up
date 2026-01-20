# Flutter Mobile App

Interactive concert lighting application that synchronizes your phone's flash and screen to the music beat.

## Prerequisites

- Flutter SDK 3.0+
- Android Studio / Xcode
- Physical device (emulator has limited torch support)

## Installation

```bash
flutter pub get
```

## Configuration

### 1. Update Server URL

Edit `lib/services/socket_service.dart`:

```dart
static const String SERVER_URL = 'http://YOUR_COMPUTER_IP:3000';
```

**Important:** Replace `YOUR_COMPUTER_IP` with your computer's local IP address.

To find your IP:
- **macOS/Linux**: `ifconfig | grep inet`
- **Windows**: `ipconfig`

### 2. Platform-Specific Setup

#### Android

Add permissions to `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.FLASHLIGHT" />
```

#### iOS

Add camera usage description to `ios/Runner/Info.plist`:

```xml
<key>NSCameraUsageDescription</key>
<string>This app needs camera access to control the flashlight</string>
```

## Running the App

```bash
# Run on connected device
flutter run

# Build release APK (Android)
flutter build apk --release

# Build iOS app
flutter build ios --release
```

## Features

- ✅ **Real-time WebSocket Connection** - Connects to Node.js server
- ✅ **Torch Control** - Pulses flashlight for 100ms
- ✅ **Screen Flash** - Full-screen color animation
- ✅ **Connection Status** - Visual indicator (green/red dot)
- ✅ **Auto-Reconnection** - Handles network interruptions
- ✅ **Low Latency** - <50ms response time
- ✅ **Manual Test** - Debug button for testing without music

## Architecture

### File Structure

```
lib/
├── main.dart                    # App entry point
├── services/
│   └── socket_service.dart      # WebSocket connection manager
└── screens/
    └── concert_screen.dart      # Main UI and flash logic
```

### Socket Service

Manages WebSocket connection:
- Auto-reconnection on disconnect
- Event emission and listening
- Connection state management

### Concert Screen

Main UI with:
- Dark fullscreen display
- Flash effect (torch + screen)
- Connection status indicator
- Smooth fade animations

## Performance Optimization

### Low Latency
- WebSocket transport (no HTTP polling)
- Native platform channels for torch control
- AnimationController for smooth transitions

### Battery Optimization
- Torch auto-off after 100ms
- Minimal background processing
- Screen brightness restoration

## Troubleshooting

### Torch Not Working
- Check camera permissions
- Test on physical device (emulators don't have torch)
- Some devices don't support torch control

### Cannot Connect to Server
1. Ensure Node.js server is running
2. Check you're on the same Wi-Fi network
3. Verify SERVER_URL is correct (use IP, not localhost)
4. Disable firewall or allow port 3000

### App Crashes
- Check Flutter version: `flutter doctor`
- Clear build cache: `flutter clean && flutter pub get`
- Rebuild: `flutter run`

## Testing

### Manual Test Mode
The app includes a "Manual Test Flash" button for debugging without live music.

### Network Debugging
Enable verbose logging in `socket_service.dart` to see connection events.

## Production Deployment

Before releasing:
1. Remove debug button from `concert_screen.dart`
2. Update SERVER_URL to production endpoint
3. Add error reporting (e.g., Sentry)
4. Implement analytics
5. Test on multiple devices

## Known Limitations

- **iOS Background**: App must be in foreground for torch control
- **Battery Drain**: Continuous use can drain battery quickly
- **Torch Availability**: Not all Android devices support torch control
- **Latency**: Network quality affects response time

## Dependencies

- `socket_io_client` - WebSocket communication
- `torch_light` - Flashlight control
- `screen_brightness` - Screen brightness management

## License

MIT License
