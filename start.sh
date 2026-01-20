#!/bin/bash

###############################################################################
# Let-It-Up Launch Script
# Starts all components of the Let-It-Up concert lighting system
###############################################################################

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🎵 Let-It-Up Startup Script 🎵                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📂 Project Directory: ${NC}$SCRIPT_DIR"
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command_exists node; then
    echo "❌ Node.js is not installed"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

if ! command_exists npm; then
    echo "❌ npm is not installed"
    exit 1
fi
echo "✅ npm found: $(npm --version)"

if ! command_exists python3; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

echo ""

# Install dependencies if needed
echo -e "${YELLOW}📦 Checking dependencies...${NC}"

if [ ! -d "$SCRIPT_DIR/backend/node_modules" ]; then
    echo "Installing Node.js dependencies..."
    cd "$SCRIPT_DIR/backend"
    npm install
    echo "✅ Node.js dependencies installed"
else
    echo "✅ Node.js dependencies already installed"
fi

echo ""

# Get local IP address
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo -e "${GREEN}🌐 Your local IP address: ${NC}$LOCAL_IP"
echo ""

# Instructions
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Starting Services                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "1️⃣  Node.js Server will start on port 3000"
echo "2️⃣  Python Test Trigger will send flashes every 2 seconds"
echo "3️⃣  Web Demo will be available at:"
echo ""
echo -e "    ${GREEN}http://localhost:3000/demo${NC}"
echo -e "    ${GREEN}http://$LOCAL_IP:3000/demo${NC} (for other devices)"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C to kill all background processes
trap 'echo ""; echo "🛑 Shutting down all services..."; kill 0' EXIT INT TERM

# Start Node.js server
echo -e "${BLUE}🚀 Starting Node.js server...${NC}"
cd "$SCRIPT_DIR/backend"
node server.js &
SERVER_PID=$!
sleep 2

# Start Python test trigger
echo -e "${BLUE}🚀 Starting Python test trigger...${NC}"
cd "$SCRIPT_DIR/python_dj"
python3 test_trigger.py &
PYTHON_PID=$!
sleep 2

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  ✅ All Services Running!                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🌐 Open your browser:${NC}"
echo -e "   ${GREEN}http://localhost:3000/demo${NC}"
echo ""
echo -e "${YELLOW}💡 Tip: Press SPACE in the web demo for a manual flash test${NC}"
echo ""
echo "Logs will appear below..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Wait for background processes
wait
