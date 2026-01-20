/**
 * Let-It-Up Backend Server
 *
 * Socket.io Hub that receives beat triggers from Python AI analyzer
 * and broadcasts flash events to all connected mobile clients.
 */

const express = require('express');
const http = require('http');
const path = require('path');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
const server = http.createServer(app);

// Configure CORS for cross-origin requests
app.use(cors());

// Serve static files from web_demo directory
app.use('/demo', express.static(path.join(__dirname, '../web_demo')));

// Initialize Socket.io with CORS enabled
const io = new Server(server, {
  cors: {
    origin: "*", // Allow all origins for MVP (restrict in production)
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3000;

// Track connected clients
let connectedClients = 0;
let pythonConnected = false;
let currentLyrics = "";
let currentBPM = 0;
let audioAnalysisData = {};

// Connection handler
io.on('connection', (socket) => {
  console.log(`✅ Client connected: ${socket.id}`);

  // Identify client type
  socket.on('identify', (data) => {
    if (data.type === 'python' || data.type === 'ai_analyzer') {
      pythonConnected = true;
      console.log('🎵 Python AI Analyzer connected');
    } else if (data.type === 'mobile') {
      connectedClients++;
      console.log(`📱 Mobile client connected. Total: ${connectedClients}`);

      // Send current lyrics and audio data to new client
      if (currentLyrics) {
        socket.emit('lyrics_update', { text: currentLyrics, timestamp: Date.now() });
      }
      if (Object.keys(audioAnalysisData).length > 0) {
        socket.emit('audio_analysis', audioAnalysisData);
      }
    }
  });

  // Listen for flash trigger from Python AI analyzer
  socket.on('trigger_flash', (data) => {
    console.log('⚡ Beat detected! Broadcasting flash_pulse to all clients...');

    // Broadcast to ALL connected mobile clients
    io.emit('flash_pulse', {
      timestamp: Date.now(),
      intensity: data?.intensity || 1.0
    });
  });

  // Advanced AI audio analysis event
  socket.on('audio_analysis', (data) => {
    const eventIcons = {
      'bass_drop': '💥',
      'vocal': '🎤',
      'rhythm': '🎵',
      'build': '📈'
    };

    const icon = eventIcons[data.event_type] || '⚡';
    console.log(`${icon} ${data.event_type} detected! BPM: ${data.bpm}, Intensity: ${data.intensity}`);

    // Store audio data
    audioAnalysisData = data;
    currentBPM = data.bpm;

    // Broadcast to all clients with enhanced data
    io.emit('audio_analysis', data);

    // Also send flash_pulse for backward compatibility
    io.emit('flash_pulse', {
      timestamp: data.timestamp || Date.now(),
      intensity: data.intensity,
      event_type: data.event_type,
      bpm: data.bpm
    });
  });

  // Live lyrics update
  socket.on('lyrics_update', (data) => {
    console.log(`🎤 Lyrics: "${data.text}"`);
    currentLyrics = data.text;

    // Broadcast lyrics to all clients
    io.emit('lyrics_update', {
      text: data.text,
      timestamp: data.timestamp || Date.now()
    });
  });

  // Manual trigger for testing (optional)
  socket.on('manual_trigger', () => {
    console.log('🔧 Manual trigger received');
    io.emit('flash_pulse', {
      timestamp: Date.now(),
      intensity: 1.0,
      event_type: 'manual'
    });
  });

  // Handle disconnection
  socket.on('disconnect', () => {
    console.log(`❌ Client disconnected: ${socket.id}`);

    // Check if it was Python or mobile client
    if (socket.handshake.query.type === 'python') {
      pythonConnected = false;
      console.log('🎵 Python AI Analyzer disconnected');
    } else {
      connectedClients = Math.max(0, connectedClients - 1);
      console.log(`📱 Mobile clients remaining: ${connectedClients}`);
    }
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'running',
    clients: connectedClients,
    pythonConnected: pythonConnected,
    timestamp: new Date().toISOString()
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.send(`
    <h1>🎵 Let-It-Up Server</h1>
    <p>Status: <strong>Running</strong></p>
    <p>Connected mobile clients: <strong>${connectedClients}</strong></p>
    <p>Python AI: <strong>${pythonConnected ? 'Connected ✅' : 'Disconnected ❌'}</strong></p>
    <p>Current BPM: <strong>${currentBPM || 'N/A'}</strong></p>
    <p>Latest Lyrics: <strong>${currentLyrics || 'None'}</strong></p>
    <hr>
    <h3>Web Demos:</h3>
    <p><a href="/demo">🌐 Basic Demo (Simple Flashes)</a></p>
    <p><a href="/demo/enhanced_demo.html">✨ Enhanced AI Demo (Live Lyrics + Spectrum)</a></p>
  `);
});

// Start server
server.listen(PORT, '0.0.0.0', () => {
  console.log('╔════════════════════════════════════════╗');
  console.log('║   🎵 Let-It-Up Server Started 🎵      ║');
  console.log('╚════════════════════════════════════════╝');
  console.log(`🌐 Server running on port ${PORT}`);
  console.log(`📡 Socket.io ready for connections`);
  console.log(`🔗 Local: http://localhost:${PORT}`);
  console.log('');
  console.log('Waiting for connections...');
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down server...');
  io.close(() => {
    console.log('✅ All connections closed');
    process.exit(0);
  });
});
