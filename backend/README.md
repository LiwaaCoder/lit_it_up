# Node.js Backend Server

Socket.io hub that receives beat triggers from the Python AI analyzer and broadcasts flash events to all connected mobile clients.

## Installation

```bash
npm install
```

## Usage

```bash
# Production
npm start

# Development (with auto-reload)
npm run dev
```

The server will start on `http://localhost:3000`

## API Endpoints

### WebSocket Events

**Incoming (from Python):**
- `trigger_flash` - Beat detected, broadcast to all clients

**Outgoing (to Mobile):**
- `flash_pulse` - Flash your screen/torch!

**Testing:**
- `manual_trigger` - Manual test trigger

### HTTP Endpoints

- `GET /` - Server status page
- `GET /health` - Health check JSON

## Configuration

Set environment variables:
```bash
PORT=3000
```

## Architecture

```
Python AI → Socket.io Server → Mobile Clients (1-1000+)
```

The server acts as a simple broadcast hub with minimal latency.
