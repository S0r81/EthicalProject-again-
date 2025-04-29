#!/bin/bash

echo "[*] Activating Python virtual environment..."
source venv38/bin/activate

# Check if gnome-terminal is installed
if ! command -v gnome-terminal &> /dev/null; then
    echo "[!] gnome-terminal could not be found. Please install it first."
    exit
fi

echo "[*] Starting Ryu controller in a new window..."
gnome-terminal -- bash -c "sudo env 'PATH=$PATH' python3.8 -m ryu.cmd.manager --ofp-tcp-listen-port 6633 backend/dos_detector.py; exec bash"

sleep 5  # Give Ryu time to start

echo "[*] Starting Mininet topology in a new window..."
gnome-terminal -- bash -c "sudo python3 backend/my_topology.py; exec bash"

