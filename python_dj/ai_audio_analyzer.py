"""
Let-It-Up AI Audio Analyzer with Live Lyrics

Advanced audio analysis system that:
1. Detects bass frequencies and drops
2. Analyzes rhythm patterns and BPM
3. Identifies vocal presence
4. Performs real-time speech-to-text for live lyrics
5. Sends intelligent flash triggers based on music analysis

Author: Senior Full Stack Architect
"""

import pyaudio
import numpy as np
import librosa
import socketio
import time
import speech_recognition as sr
from collections import deque
import threading
import queue
import config

# Initialize Socket.io client
sio = socketio.Client()

# Audio stream
audio_stream = None
p = None

# Audio analysis state
volume_history = deque(maxlen=config.HISTORY_SIZE)
last_flash_time = 0
current_bpm = 0
lyrics_queue = queue.Queue()

# Frequency bands (Hz)
BASS_RANGE = (20, 250)      # Bass frequencies
MID_RANGE = (250, 2000)     # Mid frequencies
HIGH_RANGE = (2000, 8000)   # High frequencies
VOCAL_RANGE = (300, 3400)   # Human voice range


def analyze_frequency_bands(audio_data, sample_rate):
    """
    Analyze audio across different frequency bands using FFT.
    Returns: bass_energy, mid_energy, high_energy, vocal_energy
    """
    # Perform FFT
    fft = np.fft.rfft(audio_data)
    frequencies = np.fft.rfftfreq(len(audio_data), 1/sample_rate)
    magnitudes = np.abs(fft)

    # Calculate energy in each band
    bass_mask = (frequencies >= BASS_RANGE[0]) & (frequencies <= BASS_RANGE[1])
    mid_mask = (frequencies >= MID_RANGE[0]) & (frequencies <= MID_RANGE[1])
    high_mask = (frequencies >= HIGH_RANGE[0]) & (frequencies <= HIGH_RANGE[1])
    vocal_mask = (frequencies >= VOCAL_RANGE[0]) & (frequencies <= VOCAL_RANGE[1])

    bass_energy = np.sum(magnitudes[bass_mask])
    mid_energy = np.sum(magnitudes[mid_mask])
    high_energy = np.sum(magnitudes[high_mask])
    vocal_energy = np.sum(magnitudes[vocal_mask])

    return bass_energy, mid_energy, high_energy, vocal_energy


def detect_bass_drop(bass_energy, bass_history):
    """
    Detect sudden bass increases (bass drops).
    Returns: True if bass drop detected
    """
    if len(bass_history) < 5:
        return False

    avg_bass = np.mean(bass_history)
    threshold = avg_bass * 2.0  # 200% increase = bass drop

    return bass_energy > threshold and bass_energy > 5000  # Minimum energy threshold


def estimate_bpm(audio_data, sample_rate):
    """
    Estimate BPM using librosa's beat tracking.
    Returns: estimated BPM
    """
    try:
        # Convert to float32 for librosa
        audio_float = audio_data.astype(np.float32) / np.iinfo(np.int16).max

        # Estimate tempo
        tempo, _ = librosa.beat.beat_track(y=audio_float, sr=sample_rate)
        return tempo
    except:
        return 0


def calculate_rms(audio_data):
    """Calculate RMS volume (overall loudness)"""
    rms = np.sqrt(np.mean(audio_data**2))
    return rms


def detect_rhythm_event(bass_energy, mid_energy, bass_history, mid_history):
    """
    Detect various rhythm events based on frequency analysis.
    Returns: event_type ('bass_drop', 'vocal', 'rhythm', 'build', None)
    """
    global last_flash_time

    # Cooldown check
    current_time = time.time() * 1000
    if current_time - last_flash_time < config.COOLDOWN_MS:
        return None

    if len(bass_history) < 5 or len(mid_history) < 5:
        return None

    avg_bass = np.mean(bass_history)
    avg_mid = np.mean(mid_history)

    # Bass drop detection (strongest event)
    if detect_bass_drop(bass_energy, bass_history):
        return 'bass_drop'

    # Strong bass (rhythmic beat)
    if bass_energy > avg_bass * 1.5 and bass_energy > 3000:
        return 'rhythm'

    # Vocal detection (mid frequencies dominant)
    if mid_energy > avg_mid * 1.3 and mid_energy > bass_energy * 1.2:
        return 'vocal'

    # Build-up detection (gradual increase)
    if len(bass_history) >= 5:
        recent_bass = list(bass_history)[-5:]
        if all(recent_bass[i] < recent_bass[i+1] for i in range(len(recent_bass)-1)):
            return 'build'

    return None


def send_flash_event(event_type='rhythm', intensity=1.0, bpm=0, bass=0, mid=0, high=0):
    """
    Send flash event with music analysis data to Node.js server.
    """
    try:
        sio.emit('audio_analysis', {
            'event_type': event_type,  # bass_drop, vocal, rhythm, build
            'intensity': intensity,
            'bpm': int(bpm),
            'bass_energy': int(bass),
            'mid_energy': int(mid),
            'high_energy': int(high),
            'timestamp': time.time()
        })

        icon = {'bass_drop': '💥', 'vocal': '🎤', 'rhythm': '🎵', 'build': '📈'}.get(event_type, '⚡')
        print(f"{icon} {event_type.upper()} detected! BPM: {int(bpm)}, Intensity: {intensity:.2f}")

        global last_flash_time
        last_flash_time = time.time() * 1000

    except Exception as e:
        print(f"❌ Error sending event: {e}")


def send_lyrics_update(lyrics_text):
    """Send live lyrics to all clients"""
    try:
        sio.emit('lyrics_update', {
            'text': lyrics_text,
            'timestamp': time.time()
        })
        print(f"🎤 Lyrics: {lyrics_text}")
    except Exception as e:
        print(f"❌ Error sending lyrics: {e}")


def lyrics_recognition_thread():
    """
    Background thread for real-time speech recognition.
    Converts live audio to text (lyrics).
    """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Lyrics recognition thread started...")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    while True:
        try:
            with mic as source:
                print("🎧 Listening for lyrics...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

            try:
                # Use Google Speech Recognition (free)
                text = recognizer.recognize_google(audio)
                if text and len(text) > 0:
                    send_lyrics_update(text)
            except sr.UnknownValueError:
                # No speech detected
                pass
            except sr.RequestError as e:
                print(f"⚠️ Speech recognition error: {e}")
                time.sleep(5)

        except Exception as e:
            print(f"⚠️ Lyrics thread error: {e}")
            time.sleep(1)


def audio_callback(in_data, frame_count, time_info, status):
    """
    PyAudio callback - analyzes audio in real-time.
    """
    global current_bpm, volume_history

    if status:
        print(f"⚠️ Audio status: {status}")

    # Convert to numpy array
    audio_data = np.frombuffer(in_data, dtype=np.int16)

    # Calculate overall volume (RMS)
    rms_volume = calculate_rms(audio_data)
    volume_history.append(rms_volume)

    # Analyze frequency bands
    bass, mid, high, vocal = analyze_frequency_bands(audio_data, config.SAMPLE_RATE)

    # Maintain history for bass and mid
    if not hasattr(audio_callback, 'bass_history'):
        audio_callback.bass_history = deque(maxlen=10)
        audio_callback.mid_history = deque(maxlen=10)

    audio_callback.bass_history.append(bass)
    audio_callback.mid_history.append(mid)

    # Estimate BPM (expensive, do less frequently)
    if not hasattr(audio_callback, 'frame_counter'):
        audio_callback.frame_counter = 0

    audio_callback.frame_counter += 1
    if audio_callback.frame_counter % 20 == 0:  # Every ~2 seconds
        current_bpm = estimate_bpm(audio_data, config.SAMPLE_RATE)

    # Detect rhythm events
    event_type = detect_rhythm_event(
        bass, mid,
        audio_callback.bass_history,
        audio_callback.mid_history
    )

    if event_type:
        # Calculate intensity based on event type
        intensity = {
            'bass_drop': 1.0,   # Maximum intensity
            'vocal': 0.7,       # Medium intensity
            'rhythm': 0.8,      # High intensity
            'build': 0.5        # Low intensity (building up)
        }.get(event_type, 0.6)

        send_flash_event(
            event_type=event_type,
            intensity=intensity,
            bpm=current_bpm,
            bass=bass,
            mid=mid,
            high=high
        )

    return (in_data, pyaudio.paContinue)


# Socket.io Event Handlers
@sio.event
def connect():
    print("✅ Connected to Node.js server")
    sio.emit('identify', {'type': 'ai_analyzer'})


@sio.event
def disconnect():
    print("❌ Disconnected from Node.js server")


@sio.event
def connect_error(data):
    print(f"❌ Connection error: {data}")


def start_listening():
    """Initialize PyAudio and start audio analysis"""
    global audio_stream, p

    print("🎵 Initializing AI audio analysis system...")

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Print available devices
    if config.VERBOSE:
        print("\n📡 Available Audio Devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"  [{i}] {info['name']} - Input: {info['maxInputChannels']}")
        print()

    try:
        audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=config.CHANNELS,
            rate=config.SAMPLE_RATE,
            input=True,
            frames_per_buffer=config.CHUNK_SIZE,
            stream_callback=audio_callback
        )

        print("🎤 AI Audio Analysis started!")
        print(f"⚙️  Features: Bass Detection, Rhythm Analysis, BPM Tracking, Live Lyrics")
        print(f"⚙️  Settings: Sample Rate={config.SAMPLE_RATE}Hz, Chunk={config.CHUNK_SIZE}")
        print("🎧 Play music with vocals to see lyrics appear!\n")

        audio_stream.start_stream()

        while audio_stream.is_active():
            time.sleep(0.1)

    except Exception as e:
        print(f"❌ Error opening audio stream: {e}")
        print("\n💡 Troubleshooting:")
        print("  1. Check microphone/audio input is connected")
        print("  2. Try different CHUNK_SIZE in config.py")
        print("  3. Verify PyAudio installation")


def cleanup():
    """Clean up resources"""
    global audio_stream, p

    print("\n🛑 Shutting down AI audio analyzer...")

    if audio_stream:
        audio_stream.stop_stream()
        audio_stream.close()

    if p:
        p.terminate()

    if sio.connected:
        sio.disconnect()

    print("✅ Cleanup complete")


def main():
    """Main entry point"""
    print("╔════════════════════════════════════════════════════╗")
    print("║   🎵 Let-It-Up AI Audio Analyzer 🎵              ║")
    print("║   Advanced Beat Detection + Live Lyrics           ║")
    print("╚════════════════════════════════════════════════════╝\n")

    try:
        # Connect to Node.js server
        print(f"🔌 Connecting to server: {config.SERVER_URL}")
        sio.connect(config.SERVER_URL)

        # Start lyrics recognition in background thread
        print("🎤 Starting lyrics recognition...")
        lyrics_thread = threading.Thread(target=lyrics_recognition_thread, daemon=True)
        lyrics_thread.start()

        # Start audio analysis (main thread)
        time.sleep(1)
        start_listening()

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
