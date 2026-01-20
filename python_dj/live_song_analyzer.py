#!/usr/bin/env python3
"""
Live Song Analyzer with Rhythm Detection

This script:
1. Listens to music playing in your environment (microphone/system audio)
2. Identifies the song using Shazam API
3. Detects beats and rhythm in real-time
4. Sends synchronized flash triggers to the server

Usage:
    python3 live_song_analyzer.py

Requirements:
    - Microphone or system audio input
    - Internet connection (for song recognition)
    - Running Node.js server
"""

import asyncio
import time
import wave
import tempfile
import os
import numpy as np
from collections import deque
from datetime import datetime
import socketio
import config

# Audio libraries
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("❌ PyAudio not available. Install with:")
    print("   brew install portaudio")
    print("   pip3 install --break-system-packages pyaudio")

# Song recognition
try:
    from shazamio import Shazam
    SHAZAM_AVAILABLE = True
except ImportError:
    SHAZAM_AVAILABLE = False
    print("❌ ShazamIO not available. Install with:")
    print("   pip3 install --break-system-packages shazamio")

# Initialize Socket.io client
sio = socketio.Client()

# State
current_song = None
current_artist = None
current_bpm = 0
last_recognition_time = 0
recognition_cooldown = 30  # Seconds between song recognition attempts

# Beat detection
volume_history = deque(maxlen=30)
bass_history = deque(maxlen=30)
last_flash_time = 0

# Recording buffer for song recognition
recognition_buffer = []
buffer_duration = 10  # Seconds of audio to capture for recognition


# ============================================================================
# SOCKET.IO HANDLERS
# ============================================================================

@sio.event
def connect():
    print("✅ Connected to server")
    sio.emit('identify', {'type': 'ai_analyzer'})


@sio.event
def disconnect():
    print("❌ Disconnected from server")


@sio.event
def connect_error(data):
    print(f"❌ Connection error: {data}")


# ============================================================================
# AUDIO ANALYSIS
# ============================================================================

def calculate_rms(audio_data):
    """Calculate RMS volume"""
    if isinstance(audio_data, bytes):
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
    else:
        audio_array = audio_data
    rms = np.sqrt(np.mean(audio_array**2))
    return rms


def analyze_bass(audio_data, sample_rate):
    """Extract bass energy (20-250 Hz)"""
    if isinstance(audio_data, bytes):
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
    else:
        audio_array = audio_data.astype(np.float32)

    # Normalize
    audio_array = audio_array / 32768.0

    # FFT
    fft = np.fft.rfft(audio_array)
    freqs = np.fft.rfftfreq(len(audio_array), 1/sample_rate)

    # Bass frequencies
    bass_mask = (freqs >= 20) & (freqs <= 250)
    bass_energy = np.sum(np.abs(fft[bass_mask]))

    return bass_energy


def detect_beat(rms, bass):
    """Detect beat with adaptive thresholding"""
    global volume_history, bass_history, last_flash_time

    volume_history.append(rms)
    bass_history.append(bass)

    if len(volume_history) < 10:
        return False, 0.0

    # Dynamic thresholds
    avg_vol = np.mean(volume_history)
    avg_bass = np.mean(bass_history)

    vol_threshold = avg_vol * 1.6  # Increased sensitivity
    bass_threshold = avg_bass * 1.9

    # Check cooldown
    current_time = time.time() * 1000
    if current_time - last_flash_time < config.COOLDOWN_MS:
        return False, 0.0

    # Detect beat (volume spike OR strong bass)
    is_beat = (rms > vol_threshold and rms > 800) or \
              (bass > bass_threshold and bass > 2000)

    if is_beat:
        last_flash_time = current_time
        # Calculate intensity
        intensity = min(1.0, max(0.4, rms / 4000))
        return True, intensity

    return False, 0.0


def send_flash_event(intensity, event_type='rhythm'):
    """Send flash trigger to server"""
    try:
        sio.emit('audio_analysis', {
            'event_type': event_type,
            'intensity': intensity,
            'bpm': current_bpm,
            'timestamp': time.time()
        })

        # Visual feedback
        bar = '█' * int(intensity * 25)
        print(f"⚡ {bar} {intensity*100:.0f}%", end='\r')

    except Exception as e:
        pass  # Silent fail


def send_song_info(song_data):
    """Send recognized song info to server"""
    try:
        sio.emit('lyrics_update', {
            'text': f"♪ {song_data['title']} - {song_data['artist']}",
            'timestamp': time.time()
        })
    except:
        pass


# ============================================================================
# SONG RECOGNITION
# ============================================================================

async def recognize_song(audio_file_path):
    """Use Shazam to identify the song"""
    try:
        shazam = Shazam()
        result = await shazam.recognize(audio_file_path)

        if result and 'track' in result:
            track = result['track']
            title = track.get('title', 'Unknown')
            artist = track.get('subtitle', 'Unknown Artist')

            return {
                'title': title,
                'artist': artist,
                'shazam_url': track.get('url', ''),
                'genres': track.get('genres', {}).get('primary', 'Unknown'),
                'album': track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', '')
            }

        return None

    except Exception as e:
        print(f"\n⚠️  Recognition error: {e}")
        return None


def save_audio_buffer_to_file(audio_chunks, sample_rate, channels):
    """Save recorded audio chunks to temporary WAV file"""
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_path = temp_file.name
    temp_file.close()

    # Write WAV file
    with wave.open(temp_path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(audio_chunks))

    return temp_path


# ============================================================================
# MAIN AUDIO PROCESSING
# ============================================================================

def process_audio_chunk(audio_data, sample_rate):
    """Process each audio chunk for beat detection and recognition"""
    global recognition_buffer, last_recognition_time, current_song

    # Add to recognition buffer
    recognition_buffer.append(audio_data)

    # Calculate audio metrics
    rms = calculate_rms(audio_data)
    bass = analyze_bass(audio_data, sample_rate)

    # Detect beat
    is_beat, intensity = detect_beat(rms, bass)

    if is_beat:
        event_type = 'bass_drop' if bass > np.mean(bass_history) * 2 else 'rhythm'
        send_flash_event(intensity, event_type)

    # Try song recognition periodically
    current_time = time.time()
    buffer_length = len(recognition_buffer) * config.CHUNK_SIZE / sample_rate

    if buffer_length >= buffer_duration and \
       (current_time - last_recognition_time) >= recognition_cooldown:

        print("\n🔍 Attempting song recognition...")
        last_recognition_time = current_time

        # Save buffer to file
        temp_file = save_audio_buffer_to_file(
            recognition_buffer,
            sample_rate,
            config.CHANNELS
        )

        # Recognize song asynchronously
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            song_data = loop.run_until_complete(recognize_song(temp_file))
            loop.close()

            if song_data:
                current_song = song_data['title']
                current_artist = song_data['artist']

                print(f"\n🎵 SONG IDENTIFIED!")
                print(f"   Title: {song_data['title']}")
                print(f"   Artist: {song_data['artist']}")
                print(f"   Genre: {song_data.get('genres', 'Unknown')}")
                print(f"   Album: {song_data.get('album', 'Unknown')}\n")

                # Send to clients
                send_song_info(song_data)
            else:
                print("❓ Could not identify song\n")

        except Exception as e:
            print(f"⚠️  Recognition failed: {e}\n")
        finally:
            # Cleanup
            try:
                os.unlink(temp_file)
            except:
                pass

        # Clear buffer
        recognition_buffer = []


def audio_callback(in_data, frame_count, time_info, status):
    """PyAudio callback - called for each audio chunk"""
    if status:
        print(f"⚠️  {status}")

    # Process the chunk
    process_audio_chunk(in_data, config.SAMPLE_RATE)

    return (in_data, pyaudio.paContinue)


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║     🎵 Live Song Analyzer + Rhythm Detection 🎵          ║")
    print("║     Shazam-powered Beat-Synced Lighting System            ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

    # Check dependencies
    if not PYAUDIO_AVAILABLE:
        print("❌ PyAudio is required but not installed")
        return

    if not SHAZAM_AVAILABLE:
        print("❌ ShazamIO is required but not installed")
        return

    # Connect to server
    print(f"🔌 Connecting to server: {config.SERVER_URL}")
    try:
        sio.connect(config.SERVER_URL)
        print("✅ Connected!\n")
    except Exception as e:
        print(f"❌ Could not connect: {e}")
        print("   Make sure server is running: bash start.sh")
        return

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    print("📡 Available Audio Input Devices:")
    default_device = None
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            marker = ""
            if info.get('index') == p.get_default_input_device_info().get('index'):
                marker = " [DEFAULT]"
                default_device = i
            print(f"  [{i}] {info['name']}{marker}")

    print(f"\n🎤 Using device: {default_device}")
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("  1. Open http://localhost:3000/demo in your browser")
    print("  2. Play music from Spotify, YouTube, etc.")
    print("  3. System will identify the song and sync lights to beats")
    print("  4. Press Ctrl+C to stop")
    print("="*60 + "\n")

    try:
        # Open audio stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=config.CHANNELS,
            rate=config.SAMPLE_RATE,
            input=True,
            input_device_index=default_device,
            frames_per_buffer=config.CHUNK_SIZE,
            stream_callback=audio_callback
        )

        print("🎧 Listening for music...\n")
        stream.start_stream()

        # Keep running
        while stream.is_active():
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()

        if sio.connected:
            sio.disconnect()

        print("\n✅ Cleanup complete!")


if __name__ == "__main__":
    main()
