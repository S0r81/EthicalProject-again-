#!/bin/bash

echo "[*] Activating Python virtual environment..."
source venv38/bin/activate

echo "[*] Starting Ryu controller..."
sudo env "PATH=$PATH" python3.8 -m ryu.cmd.manager --ofp-tcp-listen-port 6633 backend/dos_detector.py &

sleep 5  # Wait a bit for Ryu to fully start

echo "[*] Starting Mininet topology..."
sudo python3 backend/my_topology.py

