#!/bin/bash

###############################################################################
# Let-It-Up Enhanced Launch Script
# Starts AI-powered system with live lyrics and advanced audio analysis
###############################################################################

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     🎵 Let-It-Up Enhanced AI System 🎵                      ║"
echo "║     Live Lyrics + Bass Detection + Rhythm Analysis          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}📂 Project Directory: ${NC}$SCRIPT_DIR"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command -v node >/dev/null 2>&1; then
    echo -e "${RED}❌ Node.js not installed${NC}"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}❌ Python 3 not installed${NC}"
    exit 1
fi
echo "✅ Python 3: $(python3 --version)"

echo ""

# Check AI dependencies
echo -e "${YELLOW}📦 Checking AI dependencies...${NC}"

if ! python3 -c "import librosa" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  librosa not installed. Installing AI dependencies...${NC}"
    echo ""
    echo "This will install: librosa, speech_recognition, pydub"
    echo "This may take a few minutes..."
    echo ""

    cd "$SCRIPT_DIR/python_dj"
    pip3 install --user --break-system-packages -r requirements_ai.txt

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install AI dependencies${NC}"
        echo ""
        echo -e "${YELLOW}You can still use the basic test trigger:${NC}"
        echo "  cd python_dj && python3 test_trigger.py"
        exit 1
    fi
else
    echo "✅ AI dependencies installed"
fi

echo ""

# Install Node.js dependencies if needed
if [ ! -d "$SCRIPT_DIR/backend/node_modules" ]; then
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    cd "$SCRIPT_DIR/backend"
    npm install
fi

echo ""

# Get local IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo -e "${GREEN}🌐 Your local IP: ${NC}$LOCAL_IP"
echo ""

# Instructions
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Starting AI System                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🎵 Features:"
echo "  ✅ Bass drop detection"
echo "  ✅ Rhythm pattern analysis"
echo "  ✅ BPM tracking"
echo "  ✅ Live lyrics from vocals (speech-to-text)"
echo "  ✅ Smart flash patterns"
echo "  ✅ Audio spectrum visualizer"
echo ""
echo "🌐 Enhanced Demo URL:"
echo -e "    ${GREEN}http://localhost:3000/demo/enhanced_demo.html${NC}"
echo -e "    ${GREEN}http://$LOCAL_IP:3000/demo/enhanced_demo.html${NC} (other devices)"
echo ""
echo -e "${YELLOW}💡 Important:${NC}"
echo "  - Play music through your system audio"
echo "  - Speak into mic for live lyrics"
echo "  - Higher volume = better detection"
echo ""
echo "Press Ctrl+C to stop"
echo ""

trap 'echo ""; echo "🛑 Shutting down..."; kill 0' EXIT INT TERM

# Start Node.js server
echo -e "${BLUE}🚀 Starting enhanced backend server...${NC}"
cd "$SCRIPT_DIR/backend"
node server.js &
sleep 2

# Start AI audio analyzer
echo -e "${BLUE}🚀 Starting AI audio analyzer...${NC}"
cd "$SCRIPT_DIR/python_dj"
python3 ai_audio_analyzer.py &
sleep 2

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ✅ AI System Running!                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🌐 Open Enhanced Demo:${NC}"
echo -e "   ${GREEN}http://localhost:3000/demo/enhanced_demo.html${NC}"
echo ""
echo -e "${YELLOW}🎵 Play some music and watch the magic!${NC}"
echo ""
echo "Logs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

wait
