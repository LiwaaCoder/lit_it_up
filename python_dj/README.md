# Python AI Audio Analyzer

Real-time beat detection system that listens to live audio and triggers synchronized lighting effects.

## Installation

### macOS/Linux
```bash
pip install -r requirements.txt
```

### Windows
```bash
# Install PyAudio (requires Microsoft C++ Build Tools)
pip install pipwin
pipwin install pyaudio

# Install other dependencies
pip install -r requirements.txt
```

## Configuration

Edit `config.py`:

```python
SERVER_URL = "http://localhost:3000"  # Node.js server address
VOLUME_THRESHOLD_MULTIPLIER = 1.5     # Beat sensitivity
COOLDOWN_MS = 250                      # Min time between flashes
```

## Usage

```bash
python dj_listener.py
```

**Important:** Make sure:
1. Your microphone is connected and working
2. The Node.js server is running
3. You're playing music (or making noise) for the script to detect

## How It Works

### Beat Detection Algorithm

1. **Capture Audio**: PyAudio streams from microphone (CHUNK_SIZE=1024 frames)
2. **Calculate RMS**: Root Mean Square volume = sqrt(mean(samples²))
3. **Rolling Average**: Track last 10 chunks for dynamic threshold
4. **Beat Detection**: If current_volume > (average × 1.5), it's a beat!
5. **Cooldown**: Wait 250ms before next trigger (prevents flooding)

### Volume Threshold

The threshold adapts to ambient noise:
- Quiet room: ~500 RMS units
- Normal music: ~2000-5000 RMS units
- Loud concert: ~8000+ RMS units

Adjust `VOLUME_THRESHOLD_MULTIPLIER` in `config.py` to change sensitivity.

## Troubleshooting

### No Audio Device Found
```bash
# List available devices
python -c "import pyaudio; p=pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"
```

### PyAudio Installation Failed
- **macOS**: `brew install portaudio && pip install pyaudio`
- **Ubuntu**: `sudo apt-get install portaudio19-dev && pip install pyaudio`
- **Windows**: Use `pipwin` (see installation above)

### Beats Not Detected
- Increase volume or move microphone closer to speakers
- Lower `VOLUME_THRESHOLD_MULTIPLIER` in config.py
- Check `VERBOSE = True` to see real-time RMS values

## Advanced Configuration

### Custom Audio Device

Edit `dj_listener.py` to specify device index:

```python
audio_stream = p.open(
    format=pyaudio.paInt16,
    channels=config.CHANNELS,
    rate=config.SAMPLE_RATE,
    input=True,
    input_device_index=2,  # Add this line with your device index
    frames_per_buffer=config.CHUNK_SIZE,
    stream_callback=audio_callback
)
```

## Performance

- **CPU Usage**: ~5-10%
- **Memory**: ~50MB
- **Latency**: <10ms from audio to socket emission
