#!/usr/bin/env python3
"""
Music Rhythm Detection Test Script

This script can:
1. Listen to live microphone input and detect beats in real-time
2. Analyze music files (MP3, WAV, etc.) and detect rhythm patterns
3. Display visual feedback and send triggers to the server

Usage:
    python3 music_rhythm_test.py --live              # Listen to microphone
    python3 music_rhythm_test.py --file song.mp3     # Analyze a music file
    python3 music_rhythm_test.py --help              # Show help
"""

import argparse
import sys
import time
import numpy as np
import socketio
import config

# Try to import optional libraries
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️  PyAudio not available - live microphone mode disabled")

try:
    import librosa
    import soundfile as sf
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️  Librosa not available - file analysis features limited")

from collections import deque

# Initialize Socket.io client
sio = socketio.Client()

# Beat detection state
volume_history = deque(maxlen=20)
bass_history = deque(maxlen=20)
last_flash_time = 0


# ============================================================================
# AUDIO ANALYSIS FUNCTIONS
# ============================================================================

def calculate_rms(audio_data):
    """Calculate Root Mean Square (RMS) volume"""
    if isinstance(audio_data, bytes):
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
    else:
        audio_array = audio_data
    rms = np.sqrt(np.mean(audio_array**2))
    return rms


def analyze_frequency_bands(audio_data, sample_rate):
    """Analyze audio across different frequency bands using FFT"""
    if isinstance(audio_data, bytes):
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
    else:
        audio_array = audio_data.astype(np.float32)

    # Normalize
    if audio_array.dtype == np.int16:
        audio_array = audio_array / 32768.0

    # Perform FFT
    fft = np.fft.rfft(audio_array)
    frequencies = np.fft.rfftfreq(len(audio_array), 1/sample_rate)
    magnitudes = np.abs(fft)

    # Define frequency ranges
    bass_mask = (frequencies >= 20) & (frequencies <= 250)
    mid_mask = (frequencies >= 250) & (frequencies <= 2000)
    high_mask = (frequencies >= 2000) & (frequencies <= 8000)

    bass_energy = np.sum(magnitudes[bass_mask])
    mid_energy = np.sum(magnitudes[mid_mask])
    high_energy = np.sum(magnitudes[high_mask])

    return bass_energy, mid_energy, high_energy


def detect_beat(rms_volume, bass_energy):
    """
    Detect if current volume/bass represents a beat.
    Returns: (is_beat, intensity)
    """
    global last_flash_time, volume_history, bass_history

    volume_history.append(rms_volume)
    bass_history.append(bass_energy)

    if len(volume_history) < 5:
        return False, 0.0

    # Calculate thresholds
    avg_volume = np.mean(volume_history)
    avg_bass = np.mean(bass_history)

    volume_threshold = avg_volume * 1.5
    bass_threshold = avg_bass * 1.8

    # Check cooldown
    current_time = time.time() * 1000
    if current_time - last_flash_time < config.COOLDOWN_MS:
        return False, 0.0

    # Detect beat (strong bass or overall volume spike)
    is_beat = (rms_volume > volume_threshold and rms_volume > 500) or \
              (bass_energy > bass_threshold and bass_energy > 1000)

    if is_beat:
        last_flash_time = current_time
        # Calculate intensity (0.0 to 1.0)
        intensity = min(1.0, max(0.3, rms_volume / 5000))
        return True, intensity

    return False, 0.0


def send_flash_trigger(intensity=1.0, event_type='beat'):
    """Send flash trigger to server"""
    try:
        if sio.connected:
            sio.emit('trigger_flash', {
                'intensity': intensity,
                'timestamp': time.time(),
                'event_type': event_type
            })
            print(f"⚡ BEAT! Intensity: {intensity:.2f}")
    except Exception as e:
        print(f"❌ Error sending trigger: {e}")


# ============================================================================
# SOCKET.IO HANDLERS
# ============================================================================

@sio.event
def connect():
    print("✅ Connected to server")
    sio.emit('identify', {'type': 'python'})


@sio.event
def disconnect():
    print("❌ Disconnected from server")


@sio.event
def connect_error(data):
    print(f"❌ Connection error: {data}")


# ============================================================================
# LIVE MICROPHONE MODE
# ============================================================================

def audio_callback(in_data, frame_count, time_info, status):
    """PyAudio callback for live audio processing"""
    if status:
        print(f"⚠️  {status}")

    # Calculate metrics
    rms = calculate_rms(in_data)
    bass, mid, high = analyze_frequency_bands(in_data, config.SAMPLE_RATE)

    # Detect beat
    is_beat, intensity = detect_beat(rms, bass)

    if is_beat:
        send_flash_trigger(intensity)
        # Visual feedback
        bar = '█' * int(intensity * 20)
        print(f"🎵 {bar} {intensity*100:.0f}%")

    return (in_data, pyaudio.paContinue)


def run_live_mode():
    """Listen to live microphone input"""
    if not PYAUDIO_AVAILABLE:
        print("❌ PyAudio is not installed. Cannot use live mode.")
        print("   Install with: pip3 install --break-system-packages pyaudio")
        return

    print("\n🎤 LIVE MICROPHONE MODE")
    print("=" * 50)
    print("Starting live audio analysis...")
    print("Play some music near your microphone!\n")

    p = pyaudio.PyAudio()

    # List audio devices
    print("📡 Available audio input devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"  [{i}] {info['name']}")
    print()

    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=config.CHANNELS,
            rate=config.SAMPLE_RATE,
            input=True,
            frames_per_buffer=config.CHUNK_SIZE,
            stream_callback=audio_callback
        )

        print("🎧 Listening for beats... (Press Ctrl+C to stop)\n")
        stream.start_stream()

        while stream.is_active():
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n⚠️  Stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()


# ============================================================================
# FILE ANALYSIS MODE
# ============================================================================

def analyze_music_file(file_path):
    """Analyze a music file and detect rhythm patterns"""
    if not LIBROSA_AVAILABLE:
        print("❌ Librosa is not installed. Cannot analyze files.")
        print("   Install with: pip3 install --break-system-packages librosa soundfile")
        return

    print(f"\n🎵 MUSIC FILE ANALYSIS MODE")
    print("=" * 50)
    print(f"Loading: {file_path}\n")

    try:
        # Load audio file
        audio_data, sample_rate = librosa.load(file_path, sr=config.SAMPLE_RATE, mono=True)
        duration = len(audio_data) / sample_rate

        print(f"✅ Loaded: {duration:.1f} seconds")
        print(f"   Sample rate: {sample_rate} Hz")
        print(f"   Total samples: {len(audio_data)}")

        # Estimate BPM
        tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
        print(f"   Estimated BPM: {tempo:.0f}")
        print(f"   Detected beats: {len(beats)}")

        # Analyze in chunks
        print("\n🎧 Playing and analyzing...\n")

        chunk_size = config.CHUNK_SIZE
        total_chunks = len(audio_data) // chunk_size
        beat_count = 0

        for i in range(0, len(audio_data) - chunk_size, chunk_size):
            chunk = audio_data[i:i+chunk_size]

            # Convert to int16 for consistency
            chunk_int16 = (chunk * 32767).astype(np.int16)

            # Analyze
            rms = calculate_rms(chunk_int16)
            bass, mid, high = analyze_frequency_bands(chunk_int16, sample_rate)

            # Detect beat
            is_beat, intensity = detect_beat(rms, bass)

            if is_beat:
                beat_count += 1
                send_flash_trigger(intensity)

                # Show progress with visual beat indicator
                progress = (i / len(audio_data)) * 100
                timestamp = i / sample_rate
                bar = '█' * int(intensity * 20)
                print(f"⚡ [{timestamp:6.2f}s] {bar} {intensity*100:.0f}%")

            # Simulate real-time playback
            time.sleep(chunk_size / sample_rate * 0.5)  # 2x speed for demo

            # Show periodic progress
            if i % (chunk_size * 100) == 0:
                progress = (i / len(audio_data)) * 100
                print(f"   Progress: {progress:.1f}%")

        print(f"\n✅ Analysis complete!")
        print(f"   Total beats detected: {beat_count}")
        print(f"   Average: {beat_count / duration:.1f} beats/second")

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Music Rhythm Detection Test',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Listen to live microphone
  python3 music_rhythm_test.py --live

  # Analyze a music file
  python3 music_rhythm_test.py --file song.mp3

  # Analyze without server connection
  python3 music_rhythm_test.py --file song.mp3 --no-server
        """
    )

    parser.add_argument('--live', action='store_true',
                       help='Listen to live microphone input')
    parser.add_argument('--file', type=str,
                       help='Path to music file (MP3, WAV, etc.)')
    parser.add_argument('--no-server', action='store_true',
                       help='Run without connecting to server')

    args = parser.parse_args()

    # Show header
    print("\n╔════════════════════════════════════════════════════╗")
    print("║   🎵 Music Rhythm Detection Test 🎵              ║")
    print("║   Let-It-Up Audio Analysis System                 ║")
    print("╚════════════════════════════════════════════════════╝")

    # Check if any mode is selected
    if not args.live and not args.file:
        parser.print_help()
        return

    # Connect to server unless disabled
    if not args.no_server:
        try:
            print(f"\n🔌 Connecting to server: {config.SERVER_URL}")
            sio.connect(config.SERVER_URL)
        except Exception as e:
            print(f"⚠️  Could not connect to server: {e}")
            print("   Continuing without server connection...")

    try:
        # Run selected mode
        if args.live:
            run_live_mode()
        elif args.file:
            analyze_music_file(args.file)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    finally:
        if sio.connected:
            sio.disconnect()
        print("\n✅ Done!")


if __name__ == "__main__":
    main()
