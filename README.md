# 🎵 Let-It-Up - Interactive Concert Lighting System

An AI-powered concert application that synchronizes your audience's smartphones (flash and screen) to the music in real-time, controlled by live audio beat detection.

## 🎯 Project Overview

**Let-It-Up** transforms any concert or party into an immersive light show by:
- 🎤 **Python AI Analyzer** - Listens to live audio and detects beats using RMS volume analysis
- 🌐 **Node.js Server** - Acts as the central hub, broadcasting events via Socket.io
- 📱 **Flutter Mobile App** - Receives triggers and flashes the phone's torch + screen in sync
- 🌐 **Web Demo** - Browser-based client for instant testing (no Flutter required!)

## 🏗️ Architecture

```
Live Audio → Python AI Analyzer → Node.js Server → Flutter Mobile Clients
              (Beat Detection)    (Socket Hub)      (Flash/Screen Effects)
```

## 📂 Project Structure

```
lit_it_up/
├── backend/              # Node.js Socket.io server
│   ├── package.json
│   └── server.js
├── python_dj/            # Python AI audio analyzer
│   ├── requirements.txt
│   ├── dj_listener.py
│   ├── test_trigger.py   # Test script (no audio required)
│   └── config.py
├── flutter_app/          # Flutter mobile application
│   ├── pubspec.yaml
│   └── lib/
│       ├── main.dart
│       ├── services/socket_service.dart
│       └── screens/concert_screen.dart
├── web_demo/             # Web browser client
│   └── index.html        # Instant testing in browser!
├── start.sh              # One-command launcher
└── QUICKSTART.md         # Get started in 30 seconds
```

## 🚀 Quick Start

**See [`QUICKSTART.md`](QUICKSTART.md) for detailed instructions!**

### One-Command Demo (Easiest!)

```bash
./start.sh
```

Then open your browser to `http://localhost:3000/demo` and watch the magic! ✨

---

## 📋 Prerequisites

### Required:
- **Node.js** v16+ and npm
- **Python** 3.8+ with pip

### Optional:
- **Flutter** 3.0+ SDK (for mobile app)
- **Android Studio** or **Xcode** (for mobile development)
- **PyAudio** (for real audio beat detection)

---

## 🎬 Full Setup Instructions

### 1. Start the Node.js Server

```bash
cd backend
npm install
npm start
```

The server will run on `http://localhost:3000`

### 2. Start the Python AI Listener

```bash
cd python_dj
pip install -r requirements.txt

# Edit config.py to set SERVER_URL if needed
python dj_listener.py
```

**Note:** Make sure your microphone/audio input is working and play some music!

### 3. Run the Flutter Mobile App

```bash
cd flutter_app
flutter pub get

# For local testing: Update SERVER_URL in lib/services/socket_service.dart
# Change 'http://localhost:3000' to 'http://YOUR_COMPUTER_IP:3000'

# Run on connected device or emulator
flutter run
```

## 🎛️ Configuration

### Python Audio Analyzer (`python_dj/config.py`)

```python
SERVER_URL = "http://localhost:3000"  # Node.js server address
VOLUME_THRESHOLD_MULTIPLIER = 1.5     # Beat sensitivity (1.5 = 150% of average)
COOLDOWN_MS = 250                      # Min time between flashes (4/sec max)
```

### Flutter App (`flutter_app/lib/services/socket_service.dart`)

```dart
static const String SERVER_URL = 'http://YOUR_COMPUTER_IP:3000';
```

**Important:** When testing on a real device, replace `localhost` with your computer's local IP address.

## 🎨 How It Works

### Beat Detection Algorithm

1. **Audio Capture**: PyAudio captures live audio chunks from microphone
2. **Volume Analysis**: Calculate RMS (Root Mean Square) volume
3. **Dynamic Threshold**: Compare current volume to rolling average
4. **Beat Trigger**: If volume > (average × 1.5), emit flash event
5. **Cooldown**: Prevent rapid-fire triggers (max 4 flashes/second)

### Low-Latency Communication

- **Python → Node.js**: Socket.io direct emission (~5ms)
- **Node.js → Flutter**: WebSocket broadcast (~10ms)
- **Flutter → Hardware**: Native platform channels (~5ms)
- **Total latency**: ~20-30ms (imperceptible to humans)

## 📱 Mobile App Features

- ✅ Real-time WebSocket connection
- ✅ Torch/flashlight control (100ms pulse)
- ✅ Full-screen color flash effects
- ✅ Connection status indicator
- ✅ Auto-reconnection on disconnect
- ✅ Low battery optimization
- ✅ Manual test trigger button (debug mode)

## 🐛 Troubleshooting

### Python Audio Issues

```bash
# Test PyAudio installation
python -m pyaudio

# List available audio devices
python -c "import pyaudio; p=pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"
```

### Connection Issues

1. **Check firewall**: Ensure port 3000 is open
2. **Network**: All devices must be on the same network
3. **IP Address**: Use `ipconfig` (Windows) or `ifconfig` (Mac/Linux) to find your local IP

### Flutter Permissions

- **Android**: Add camera permission in `android/app/src/main/AndroidManifest.xml`
- **iOS**: Add camera usage description in `ios/Runner/Info.plist`

## 🔒 Security Notes

⚠️ **This is an MVP for local testing only.** Before deploying to production:

- Implement authentication
- Use HTTPS/WSS (secure WebSocket)
- Restrict CORS origins
- Add rate limiting
- Validate all inputs

## 📝 License

MIT License - Feel free to use this project for your concerts and events!

## 🎉 Credits

Built as a startup MVP demonstrating real-time audio analysis and synchronized mobile control.

**Tech Stack:** Node.js, Python, Flutter, Socket.io, PyAudio, NumPy

---

**🎵 Let the music light up the crowd! 🎵**
