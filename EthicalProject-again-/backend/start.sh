#!/bin/bash

# ---- CONFIGURATION ----
TOPOLOGY_SCRIPT="backend/my_topology.py"
WS_SERVER_SCRIPT="backend/ws_server.py"
API_SERVER_SCRIPT="backend/api_server.py"
PYTHON_ENV="myenv/bin/activate"  # optional: your virtualenv path

# ---- FUNCTIONS ----
function kill_port() {
    PORT=$1
    if lsof -i :$PORT >/dev/null 2>&1; then
        echo "Killing process on port $PORT"
        lsof -i :$PORT | awk 'NR!=1 {print $2}' | xargs kill -9
    fi
}

# ---- STARTUP ----
echo "Starting virtual network simulation..."

# Optional: activate virtual environment
if [ -f "$PYTHON_ENV" ]; then
    echo "Activating Python virtual environment..."
    source "$PYTHON_ENV"
fi

# Kill previous processes (optional safety)
kill_port 5000  # Flask default port
kill_port 8765  # WebSocket typical port

# Start topology (blocking call)
echo "Running Mininet topology ($TOPOLOGY_SCRIPT)..."
sudo python3 "$TOPOLOGY_SCRIPT" &
TOPOLOGY_PID=$!
sleep 2  # wait a bit to ensure it initializes

# Start WebSocket server
echo "Starting WebSocket server ($WS_SERVER_SCRIPT)..."
python3 "$WS_SERVER_SCRIPT" &
WS_PID=$!
sleep 1

# Start Flask API server (optional)
if [ -f "$API_SERVER_SCRIPT" ]; then
    echo "Starting Flask API server ($API_SERVER_SCRIPT)..."
    python3 "$API_SERVER_SCRIPT" &
    API_PID=$!
    sleep 1
fi

# ---- DONE ----
echo "✅ All services launched!"
echo "- Mininet PID: $TOPOLOGY_PID"
echo "- WebSocket Server PID: $WS_PID"
if [ ! -z "$API_PID" ]; then
    echo "- Flask API Server PID: $API_PID"
fi

echo "View your frontend at http://localhost:5173 (if Vite running)"
echo "Press [Ctrl+C] to terminate manually."

# Wait forever (so script doesn't exit)
wait

