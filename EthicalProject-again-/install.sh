#!/bin/bash

echo "[*] Updating system packages..."
sudo apt update
sudo apt upgrade -y

# 1. Install Deadsnakes PPA if Python 3.8 not found
if ! python3.8 --version &>/dev/null; then
    echo "[*] Python 3.8 not found. Installing via Deadsnakes PPA..."
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.8 python3.8-venv python3.8-dev python3-pip
else
    echo "[*] Python 3.8 already installed."
fi

# 2. Install Mininet and Open vSwitch
echo "[*] Installing Mininet and Open vSwitch..."
sudo apt install -y mininet openvswitch-switch openvswitch-common

# 3. Set up the Python virtual environment
echo "[*] Creating Python 3.8 virtual environment..."
python3.8 -m venv venv38

echo "[*] Activating virtual environment..."
source venv38/bin/activate

# 4. Install required Python packages
echo "[*] Installing Python packages from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[✅] Installation complete!"
echo "You can now run 'bash run.sh' to start the project."

