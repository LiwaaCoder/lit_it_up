"""
Simple Test Trigger Script (No Audio Required)

Sends periodic flash triggers to the server for testing
without requiring audio input/PyAudio.

This is useful for testing the system when:
- PyAudio installation is problematic
- No microphone is available
- You want to test the connection without music

Run this instead of dj_listener.py for testing!
"""

import socketio
import time
import config

# Initialize Socket.io client
sio = socketio.Client()


@sio.event
def connect():
    print("✅ Connected to Node.js server")
    sio.emit('identify', {'type': 'python'})


@sio.event
def disconnect():
    print("❌ Disconnected from Node.js server")


@sio.event
def connect_error(data):
    print(f"❌ Connection error: {data}")


def send_test_flash():
    """Send test flash trigger to server"""
    try:
        sio.emit('trigger_flash', {
            'intensity': 1.0,
            'timestamp': time.time()
        })
        print("⚡ TEST FLASH SENT!")
    except Exception as e:
        print(f"❌ Error sending trigger: {e}")


def main():
    print("╔════════════════════════════════════════╗")
    print("║   🔧 Let-It-Up Test Trigger 🔧       ║")
    print("║   (No Audio Required)                  ║")
    print("╚════════════════════════════════════════╝\n")

    try:
        # Connect to server
        print(f"🔌 Connecting to server: {config.SERVER_URL}")
        sio.connect(config.SERVER_URL)

        print("🎉 Connected! Sending test flashes every 2 seconds...")
        print("   Press Ctrl+C to stop\n")

        # Send test flashes every 2 seconds
        while True:
            send_test_flash()
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        if sio.connected:
            sio.disconnect()
        print("✅ Cleanup complete")


if __name__ == "__main__":
    main()
