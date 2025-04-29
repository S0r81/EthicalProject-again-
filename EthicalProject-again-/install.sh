#!/bin/bash

echo "[*] Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Deadsnakes PPA if Python 3.8 not found
if ! python3.8 --version &>/dev/null; then
    echo "[*] Python 3.8 not found. Installing via Deadsnakes PPA..."
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.8 python3.8-venv python3.8-dev python3-pip
else
    echo "[*] Python 3.8 already installed."
fi

# Install Mininet and Open vSwitch
echo "[*] Installing Mininet and Open vSwitch..."
sudo apt install -y mininet openvswitch-switch openvswitch-common

# Set up Python virtual environment
echo "[*] Creating Python 3.8 virtual environment..."
python3.8 -m venv venv38

echo "[*] Activating Python virtual environment..."
source venv38/bin/activate

# Install pip upgrade
echo "[*] Upgrading pip..."
pip install --upgrade pip

# Manually download and install Ryu 4.34
echo "[*] Downloading and manually installing Ryu 4.34..."
cd ~/Desktop
wget https://github.com/faucetsdn/ryu/archive/refs/tags/v4.34.tar.gz
tar -xvf v4.34.tar.gz
cd ryu-4.34
python3.8 setup.py install

# Install specific compatible Eventlet version
echo "[*] Installing Eventlet 0.30.2..."
pip install eventlet==0.30.2

# Install other requirements
echo "[*] Installing remaining Python libraries..."
pip install netaddr msgpack oslo.config ovs routes tinyrpc

echo "[✅] Installation complete!"
echo "You can now run 'bash run.sh' to start the project."

