# Let-It-Up Web Demo

Browser-based client for testing the Let-It-Up concert lighting system without requiring Flutter installation.

## Quick Start

1. **Start the backend server:**
   ```bash
   cd ../backend
   npm start
   ```

2. **Start the Python trigger:**
   ```bash
   cd ../python_dj
   python3 test_trigger.py
   ```

3. **Open in browser:**
   - Visit: `http://localhost:3000/demo`

## Features

✅ **Full-screen flash effects** - Mimics mobile app behavior
✅ **Real-time WebSocket connection** - Low latency (~20-30ms)
✅ **Connection status indicator** - Green/red dot
✅ **Statistics display** - Flash count, latency, timestamps
✅ **Manual trigger button** - Test without Python script
✅ **Keyboard shortcut** - Press SPACE for manual trigger
✅ **Responsive design** - Works on desktop and mobile browsers

## How It Works

1. **Connect:** Web page establishes WebSocket connection to Node.js server
2. **Listen:** Waits for `flash_pulse` events from server
3. **Flash:** On event, displays full-screen color animation
4. **Sync:** Multiple browser windows will flash simultaneously

## Browser Support

- ✅ Chrome/Edge (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers (iOS Safari, Chrome Android)

## Testing

### Test 1: Manual Trigger
Click the "Manual Test Flash" button or press SPACE

### Test 2: Python Trigger
Run `python3 test_trigger.py` - flashes every 2 seconds

### Test 3: Multiple Clients
Open demo in multiple browser tabs/windows - all flash in sync

## Customization

Edit `index.html` to customize:
- Flash colors (line 63-71)
- Flash duration (line 91)
- Fade timing (line 97)
- Server URL (line 206)

## Troubleshooting

### "Cannot connect to server"
- Ensure Node.js server is running on port 3000
- Check browser console for errors (F12)

### Flashes not appearing
- Check Python trigger is running
- Verify server logs show "Beat detected!"
- Try manual trigger first

### High latency
- Check network connection
- Close other applications using bandwidth
- Use WebSocket transport (default)

## Next Steps

Once you've verified the web demo works, you can:
1. Install Flutter SDK
2. Run the Flutter mobile app
3. Test with real audio using `dj_listener.py` (requires PyAudio)
4. Deploy to production servers

## Demo Screenshot

```
╔═══════════════════════════════════════╗
║              LET-IT-UP                ║
║          Concert Lighting             ║
║                                       ║
║        🟢 Connected                   ║
║   "Waiting for the beat..."           ║
║                                       ║
║    [Manual Test Flash Button]         ║
╚═══════════════════════════════════════╝
```

**Flash Effect:** Full-screen white/color overlay (100ms pulse + 150ms fade)
