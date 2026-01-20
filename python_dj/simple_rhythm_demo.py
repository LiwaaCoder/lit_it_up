#!/usr/bin/env python3
"""
Simple Rhythm Detection Demo

This demonstrates how the rhythm detection works by analyzing
a music file or generating simulated beats.

No PyAudio required - works with just numpy and librosa!

Usage:
    python3 simple_rhythm_demo.py                    # Simulated beats demo
    python3 simple_rhythm_demo.py song.mp3           # Analyze a music file
"""

import sys
import time
import numpy as np
import socketio
import config

# Check for optional librosa
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️  Librosa not installed - file analysis disabled")
    print("   Install with: pip3 install --break-system-packages librosa soundfile")

from collections import deque

# Socket.io client
sio = socketio.Client()

# Beat detection state
volume_history = deque(maxlen=20)
bass_history = deque(maxlen=20)
last_flash_time = 0


@sio.event
def connect():
    print("✅ Connected to server")
    sio.emit('identify', {'type': 'python'})


@sio.event
def disconnect():
    print("❌ Disconnected from server")


def calculate_rms(audio_data):
    """Calculate RMS volume"""
    return np.sqrt(np.mean(audio_data**2))


def analyze_bass(audio_data, sample_rate):
    """Extract bass energy from audio"""
    # Simple low-pass filter for bass frequencies (20-250 Hz)
    fft = np.fft.rfft(audio_data)
    freqs = np.fft.rfftfreq(len(audio_data), 1/sample_rate)
    bass_mask = (freqs >= 20) & (freqs <= 250)
    bass_energy = np.sum(np.abs(fft[bass_mask]))
    return bass_energy


def detect_beat(rms, bass):
    """Simple beat detection algorithm"""
    global volume_history, bass_history, last_flash_time

    volume_history.append(rms)
    bass_history.append(bass)

    if len(volume_history) < 5:
        return False, 0.0

    # Dynamic thresholds
    avg_vol = np.mean(volume_history)
    avg_bass = np.mean(bass_history)

    # Beat conditions
    is_beat = (rms > avg_vol * 1.5 or bass > avg_bass * 1.8)

    # Cooldown
    current_time = time.time() * 1000
    if is_beat and (current_time - last_flash_time) >= config.COOLDOWN_MS:
        last_flash_time = current_time
        intensity = min(1.0, max(0.3, rms / 5000))
        return True, intensity

    return False, 0.0


def send_trigger(intensity, event_type='beat'):
    """Send trigger to server"""
    try:
        sio.emit('trigger_flash', {
            'intensity': intensity,
            'timestamp': time.time(),
            'event_type': event_type
        })
    except:
        pass


def simulate_beats():
    """Generate simulated beat patterns for demo"""
    print("\n🎵 SIMULATED RHYTHM DEMO")
    print("=" * 60)
    print("Generating realistic beat patterns...")
    print("Watch your web demo to see the flashes!\n")

    bpm = 120  # Beats per minute
    beat_interval = 60.0 / bpm  # Seconds per beat

    patterns = [
        {"name": "Steady 4/4", "beats": [1.0, 0.5, 0.7, 0.5]},
        {"name": "Build-up", "beats": [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]},
        {"name": "Drop", "beats": [1.0, 1.0, 0.8, 0.8, 1.0, 0.6, 0.9, 0.7]},
        {"name": "Breakdown", "beats": [0.8, 0.3, 0.8, 0.3, 0.8, 0.3]},
    ]

    try:
        for pattern in patterns:
            print(f"\n🎼 Pattern: {pattern['name']}")
            print(f"   BPM: {bpm}")

            for i, intensity in enumerate(pattern['beats']):
                # Visual feedback
                bar = '█' * int(intensity * 30)
                print(f"   Beat {i+1}: {bar} {intensity*100:.0f}%")

                # Send trigger
                send_trigger(intensity, event_type='simulated')

                # Wait for next beat
                time.sleep(beat_interval)

            print()

        print("✅ Simulation complete!")

    except KeyboardInterrupt:
        print("\n⚠️  Stopped by user")


def analyze_music_file(file_path):
    """Analyze a real music file"""
    if not LIBROSA_AVAILABLE:
        print("❌ Librosa not installed. Cannot analyze music files.")
        return

    print(f"\n🎵 MUSIC FILE ANALYSIS")
    print("=" * 60)
    print(f"Loading: {file_path}")

    try:
        # Load audio
        print("📂 Loading audio file...")
        audio, sr = librosa.load(file_path, sr=22050, mono=True)
        duration = len(audio) / sr

        print(f"✅ Loaded successfully!")
        print(f"   Duration: {duration:.1f} seconds")
        print(f"   Sample rate: {sr} Hz\n")

        # Estimate tempo
        print("🎼 Analyzing rhythm...")
        tempo, beat_frames = librosa.beat.beat_track(y=audio, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        print(f"✅ Analysis complete!")
        print(f"   Estimated BPM: {tempo:.1f}")
        print(f"   Detected beats: {len(beat_times)}\n")

        # Process in chunks and detect beats
        print("🎧 Processing and sending triggers...\n")

        chunk_size = 2048
        beat_count = 0
        beat_idx = 0

        for i in range(0, len(audio) - chunk_size, chunk_size):
            chunk = audio[i:i+chunk_size]
            current_time = i / sr

            # Calculate metrics
            rms = calculate_rms(chunk)
            bass = analyze_bass(chunk, sr)

            # Check if we're near a detected beat
            if beat_idx < len(beat_times) and abs(current_time - beat_times[beat_idx]) < 0.1:
                beat_count += 1
                intensity = min(1.0, rms * 10)

                # Visual feedback
                bar = '█' * int(intensity * 30)
                print(f"⚡ [{current_time:6.2f}s] {bar} {intensity*100:.0f}%")

                # Send trigger
                send_trigger(intensity, event_type='music_beat')

                beat_idx += 1

            # Simulate playback speed
            time.sleep(chunk_size / sr * 0.3)  # 3x speed

        print(f"\n✅ Analysis complete!")
        print(f"   Total beats sent: {beat_count}")
        print(f"   Average: {beat_count/duration:.1f} beats/second")

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         🎵 Simple Rhythm Detection Demo 🎵                ║")
    print("║         Let-It-Up Beat Analysis System                     ║")
    print("╚════════════════════════════════════════════════════════════╝")

    # Connect to server
    print(f"\n🔌 Connecting to server: {config.SERVER_URL}")
    try:
        sio.connect(config.SERVER_URL)
        print("✅ Connected to server!")
    except Exception as e:
        print(f"⚠️  Could not connect: {e}")
        print("   Make sure the server is running!")
        print("   Run: bash start.sh")
        return

    # Check for file argument
    if len(sys.argv) > 1:
        music_file = sys.argv[1]
        analyze_music_file(music_file)
    else:
        simulate_beats()

    # Disconnect
    sio.disconnect()
    print("\n✅ Demo complete!")
    print("   Check your browser at http://localhost:3000/demo")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
