# 🚀 Let-It-Up - Quick Start Guide

Get the entire system running in 3 simple steps!

## Option 1: One-Command Launch (Recommended)

```bash
./start.sh
```

This starts everything automatically and opens the demo at `http://localhost:3000/demo`

---

## Option 2: Manual Launch

### Step 1: Start the Node.js Server
```bash
cd backend
npm install   # First time only
npm start
```

Server will run on `http://localhost:3000`

### Step 2: Start the Python Test Trigger
```bash
cd python_dj
python3 test_trigger.py
```

This sends flash triggers every 2 seconds (no audio required)

### Step 3: Open the Web Demo
Open your browser and visit:
```
http://localhost:3000/demo
```

You should see flashes every 2 seconds! 🎉

---

## What You'll See

### In the Terminal:
```
🎵 Let-It-Up Server Started
📡 Socket.io ready
✅ Python AI Analyzer connected
⚡ Beat detected! Broadcasting flash_pulse...
```

### In the Browser:
- **Dark fullscreen UI** with "Waiting for the beat..."
- **Green status dot** indicating connection
- **Full-screen flash effects** every 2 seconds
- **Statistics panel** showing flash count and latency

---

## Testing the System

### 1. Manual Flash Test
Click the **"Manual Test Flash"** button in the web demo (or press SPACE)

### 2. Multiple Devices
Open the demo on multiple devices:
- `http://localhost:3000/demo` (same computer)
- `http://YOUR_IP:3000/demo` (other devices on same WiFi)

All devices will flash in sync! 🎵

### 3. Real Audio (Advanced)
For beat detection from live music (requires PyAudio setup):
```bash
cd python_dj
python3 dj_listener.py
```

---

## System Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Python Trigger │ ───> │  Node.js Server │ ───> │   Web Clients   │
│  (Beat Source)  │      │  (Socket.io Hub)│      │  (Your Browser) │
└─────────────────┘      └─────────────────┘      └─────────────────┘
     Port N/A                 Port 3000              Multiple Clients
```

---

## Troubleshooting

### Server won't start
```bash
# Check if port 3000 is in use
lsof -ti:3000 | xargs kill -9
```

### Python script fails
```bash
# Install dependencies
pip3 install --user --break-system-packages numpy 'python-socketio[client]' websocket-client
```

### Web demo won't connect
1. Ensure server is running (`http://localhost:3000` should work)
2. Check browser console (F12) for errors
3. Verify firewall isn't blocking connections

---

## Next Steps

✅ **You just built a real-time synchronized lighting system!**

Now you can:
1. 📱 Install Flutter and run the mobile app (see `flutter_app/README.md`)
2. 🎵 Set up real audio beat detection (see `python_dj/README.md`)
3. 🌐 Deploy to production servers
4. 🎨 Customize flash colors and effects
5. 🎤 Use at your next concert or party!

---

## Component READMEs

- **Backend:** `backend/README.md`
- **Python:** `python_dj/README.md`
- **Flutter:** `flutter_app/README.md`
- **Web Demo:** `web_demo/README.md`

---

## Need Help?

Check the main `README.md` for detailed documentation and troubleshooting guides.

**Enjoy your synchronized light show! 🎉🎵**
