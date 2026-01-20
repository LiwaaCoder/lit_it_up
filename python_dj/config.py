"""
Configuration file for Python DJ Audio Analyzer
"""

# Server Configuration
SERVER_URL = "http://localhost:3000"  # Change to your Node.js server IP/URL

# Audio Configuration
CHUNK_SIZE = 1024  # Number of audio frames per buffer
SAMPLE_RATE = 44100  # Audio sample rate in Hz (CD quality)
CHANNELS = 1  # Mono audio input

# Beat Detection Configuration
VOLUME_THRESHOLD_MULTIPLIER = 1.5  # Multiplier for dynamic threshold (1.5 = 150% of average)
COOLDOWN_MS = 250  # Minimum milliseconds between flashes (250ms = 4 flashes/sec max)
HISTORY_SIZE = 10  # Number of chunks to keep for rolling average

# Sensitivity (adjust based on your environment)
MIN_VOLUME_THRESHOLD = 500  # Minimum RMS volume to trigger (filters out silence)
MAX_VOLUME_THRESHOLD = 10000  # Maximum RMS volume cap (prevents over-sensitivity)

# Debug
VERBOSE = True  # Print debug messages
