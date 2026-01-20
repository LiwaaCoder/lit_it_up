"""
Let-It-Up Python AI Audio Analyzer

Real-time audio beat detection system that:
1. Captures live audio from microphone/system
2. Analyzes volume (RMS) to detect bass drops/beats
3. Sends flash triggers to Node.js server via Socket.io

Author: Senior Full Stack Architect
"""

import pyaudio
import numpy as np
import socketio
import time
from collections import deque
import config

# Initialize Socket.io client
sio = socketio.Client()

# Audio stream
audio_stream = None
p = None

# Beat detection state
volume_history = deque(maxlen=config.HISTORY_SIZE)
last_flash_time = 0


def calculate_rms(audio_data):
    """
    Calculate Root Mean Square (RMS) volume of audio data.
    RMS gives us the "energy" or "loudness" of the audio.
    """
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    rms = np.sqrt(np.mean(audio_array**2))
    return rms


def detect_beat(rms_volume):
    """
    Detect if current volume represents a beat/bass drop.

    Algorithm:
    - Keep rolling average of last N chunks
    - If current volume > (average * threshold), it's a beat
    - Apply cooldown to prevent rapid-fire triggers
    """
    global last_flash_time, volume_history

    # Add current volume to history
    volume_history.append(rms_volume)

    # Need at least some history for comparison
    if len(volume_history) < 3:
        return False

    # Calculate dynamic threshold based on recent average
    avg_volume = np.mean(volume_history)
    threshold = max(
        config.MIN_VOLUME_THRESHOLD,
        min(avg_volume * config.VOLUME_THRESHOLD_MULTIPLIER, config.MAX_VOLUME_THRESHOLD)
    )

    # Check if current volume exceeds threshold
    is_beat = rms_volume > threshold

    # Apply cooldown mechanism
    current_time = time.time() * 1000  # Convert to milliseconds
    time_since_last_flash = current_time - last_flash_time

    if is_beat and time_since_last_flash >= config.COOLDOWN_MS:
        last_flash_time = current_time

        if config.VERBOSE:
            print(f"🔊 BEAT DETECTED! Volume: {rms_volume:.0f} | Threshold: {threshold:.0f} | "
                  f"Avg: {avg_volume:.0f}")

        return True

    return False


def send_flash_trigger(intensity=1.0):
    """
    Emit flash trigger event to Node.js server.
    """
    try:
        sio.emit('trigger_flash', {
            'intensity': intensity,
            'timestamp': time.time()
        })
        print("⚡ Flash trigger sent to server")
    except Exception as e:
        print(f"❌ Error sending trigger: {e}")


# Socket.io Event Handlers
@sio.event
def connect():
    print("✅ Connected to Node.js server")
    # Identify as Python client
    sio.emit('identify', {'type': 'python'})


@sio.event
def disconnect():
    print("❌ Disconnected from Node.js server")


@sio.event
def connect_error(data):
    print(f"❌ Connection error: {data}")


def audio_callback(in_data, frame_count, time_info, status):
    """
    PyAudio callback function - called for each audio chunk.
    This is where the magic happens!
    """
    if status:
        print(f"⚠️  Audio status: {status}")

    # Calculate volume
    rms_volume = calculate_rms(in_data)

    # Detect beat
    if detect_beat(rms_volume):
        send_flash_trigger(intensity=1.0)

    return (in_data, pyaudio.paContinue)


def start_listening():
    """
    Initialize PyAudio and start listening to microphone.
    """
    global audio_stream, p

    print("🎵 Initializing audio system...")

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Print available audio devices (for debugging)
    if config.VERBOSE:
        print("\n📡 Available Audio Devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"  [{i}] {info['name']} - Input Channels: {info['maxInputChannels']}")
        print()

    # Open audio stream
    try:
        audio_stream = p.open(
            format=pyaudio.paInt16,
            channels=config.CHANNELS,
            rate=config.SAMPLE_RATE,
            input=True,
            frames_per_buffer=config.CHUNK_SIZE,
            stream_callback=audio_callback
        )

        print("🎤 Audio stream started - Listening for beats...")
        print(f"⚙️  Settings: Sample Rate={config.SAMPLE_RATE}Hz, Chunk={config.CHUNK_SIZE}, "
              f"Cooldown={config.COOLDOWN_MS}ms")
        print("🎧 Start playing music to trigger flashes!\n")

        # Start audio stream
        audio_stream.start_stream()

        # Keep the program running
        while audio_stream.is_active():
            time.sleep(0.1)

    except Exception as e:
        print(f"❌ Error opening audio stream: {e}")
        print("\n💡 Troubleshooting:")
        print("  1. Check if microphone is connected and not in use")
        print("  2. Try adjusting CHUNK_SIZE in config.py")
        print("  3. Run 'python -m pyaudio' to test PyAudio installation")


def cleanup():
    """
    Clean up audio resources.
    """
    global audio_stream, p

    print("\n🛑 Shutting down...")

    if audio_stream:
        audio_stream.stop_stream()
        audio_stream.close()

    if p:
        p.terminate()

    if sio.connected:
        sio.disconnect()

    print("✅ Cleanup complete")


def main():
    """
    Main entry point
    """
    print("╔════════════════════════════════════════╗")
    print("║   🎵 Let-It-Up DJ Listener 🎵         ║")
    print("║   AI-Powered Beat Detection            ║")
    print("╚════════════════════════════════════════╝\n")

    try:
        # Connect to Node.js server
        print(f"🔌 Connecting to server: {config.SERVER_URL}")
        sio.connect(config.SERVER_URL)

        # Start audio listening
        start_listening()

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
