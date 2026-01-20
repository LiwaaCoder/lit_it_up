# 🎵 How to Use the Live Song Analyzer

## What It Does

This system listens to music playing in your environment and:
1. **Identifies songs** using Shazam API (like the Shazam app)
2. **Detects beats** in real-time
3. **Syncs flash lights** to the rhythm
4. **Displays song info** in the web demo

## Quick Start

### Step 1: Start the Server
```bash
cd /Users/liwaa/IdeaProjects/lit_it_up
bash start.sh
```

This starts:
- Node.js server on port 3000
- Web demo at http://localhost:3000/demo

### Step 2: Open the Web Demo
Open your browser to: **http://localhost:3000/demo**

### Step 3: Run the Live Song Analyzer
In a new terminal:
```bash
cd python_dj
python3 live_song_analyzer.py
```

### Step 4: Play Music!
1. Play music from:
   - Spotify
   - YouTube
   - Apple Music
   - Any other source near your microphone

2. The system will:
   - Listen to the audio
   - Identify the song name and artist
   - Detect beats and bass drops
   - Flash your browser in sync with the music

## Troubleshooting

### PyAudio Issues
If you get PyAudio errors:
```bash
brew install portaudio
pip3 install --break-system-packages pyaudio
```

### No Microphone Detected
Check your system audio settings and grant microphone permissions to Terminal.

### Song Recognition Not Working
- Ensure you have internet connection (Shazam API requires it)
- Make sure music is loud enough for microphone to pick up
- Wait 10 seconds for first recognition attempt

### Connection Refused
Make sure the server is running:
```bash
ps aux | grep "node server.js"
```

If not running, restart with:
```bash
bash start.sh
```

## Alternative Test Modes

### 1. Simulated Beats (No Microphone)
```bash
python3 simple_rhythm_demo.py
```

### 2. Analyze a Music File
```bash
python3 simple_rhythm_demo.py /path/to/song.mp3
```

### 3. Advanced Test Script
```bash
python3 music_rhythm_test.py --help
```

## How It Works

### Beat Detection Algorithm
1. Captures audio in small chunks (1024 samples)
2. Calculates RMS volume (overall loudness)
3. Analyzes bass frequencies (20-250 Hz) using FFT
4. Uses adaptive thresholds to detect beats
5. Applies cooldown (250ms) to prevent multiple triggers

### Song Recognition
1. Records 10 seconds of audio in a buffer
2. Saves to temporary WAV file
3. Sends to Shazam API for identification
4. Displays song info and artist
5. Waits 30 seconds before next recognition attempt

### Event Types
- **rhythm**: Regular beat detected
- **bass_drop**: Strong bass frequency spike
- **vocal**: Mid-frequency dominance (singing)
- **build**: Gradual intensity increase

## Configuration

Edit `config.py` to adjust:

```python
# Beat detection sensitivity
VOLUME_THRESHOLD_MULTIPLIER = 1.5  # Lower = more sensitive
COOLDOWN_MS = 250                   # Time between flashes

# Audio settings
CHUNK_SIZE = 1024                   # Buffer size
SAMPLE_RATE = 44100                 # Audio quality
```

## Web Demo Features

- **Basic Demo**: http://localhost:3000/demo
  - Simple white flashes synchronized to beats

- **Enhanced Demo**: http://localhost:3000/demo/enhanced_demo.html
  - Live song info display
  - Audio spectrum visualization
  - Color-coded event types

## System Status

Check what's running:
```bash
# Check server
curl http://localhost:3000/health

# Check processes
ps aux | grep -E "(node|python3)"
```

## Stopping Services

Press `Ctrl+C` in each terminal window, or:

```bash
# Kill all services
pkill -f "node server.js"
pkill -f "python3 live_song_analyzer"
pkill -f "python3 test_trigger"
```

## Need Help?

- Server not starting? Check if port 3000 is in use: `lsof -i :3000`
- Audio issues? List audio devices: `python3 -c "import pyaudio; p=pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"`
- Connection issues? Check firewall settings

Enjoy your beat-synchronized concert lighting! 🎉
