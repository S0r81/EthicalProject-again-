#!/bin/bash

echo "[*] Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install build dependencies for Python 3.8
echo "[*] Installing dependencies for building Python 3.8 from source..."
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
    libnss3-dev libssl-dev libreadline-dev libffi-dev libbz2-dev curl wget

# Check if Python 3.8 is already installed
if ! command -v python3.8 &>/dev/null; then
    echo "[*] Python 3.8 not found. Installing from source..."
    cd /usr/src
    sudo wget https://www.python.org/ftp/python/3.8.18/Python-3.8.18.tgz
    sudo tar -xf Python-3.8.18.tgz
    cd Python-3.8.18
    sudo ./configure --enable-optimizations
    sudo make -j$(nproc)
    sudo make altinstall
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
