##!/bin/bash

echo "[*] Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Check if Python 3.8 is installed
if ! python3.8 --version &>/dev/null; then
    echo "[*] Python 3.8 not found. Installing from source..."
    
    # Install build dependencies
    sudo apt install -y wget build-essential libssl-dev zlib1g-dev \
        libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
        libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev \
        tk-dev uuid-dev libffi-dev

    # Download and build Python 3.8
    cd /usr/src
    sudo wget https://www.python.org/ftp/python/3.8.18/Python-3.8.18.tgz
    sudo tar xvf Python-3.8.18.tgz
    cd Python-3.8.18
    sudo ./configure --enable-optimizations
    sudo make -j$(nproc)
    sudo make altinstall  # Avoids overwriting system python
else
    echo "[*] Python 3.8 already installed."
fi

# Install Mininet and Open vSwitch
echo "[*] Installing Mininet and Open vSwitch..."
sudo apt install -y mininet openvswitch-switch openvswitch-common

# Set up Python virtual environment
echo "[*] Creating Python 3.8 virtual environment..."
/usr/local/bin/python3.8 -m venv venv38

echo "[*] Activating Python virtual environment..."
source venv38/bin/activate

# Upgrade pip
echo "[*] Upgrading pip..."
pip install --upgrade pip

# Download and install Ryu 4.34
echo "[*] Downloading and installing Ryu 4.34..."
cd ~/Desktop || mkdir -p ~/Desktop && cd ~/Desktop
wget https://github.com/faucetsdn/ryu/archive/refs/tags/v4.34.tar.gz
tar -xvf v4.34.tar.gz
cd ryu-4.34
python setup.py install

# Install specific Eventlet version
echo "[*] Installing Eventlet 0.30.2..."
pip install eventlet==0.30.2

# Install additional requirements
echo "[*] Installing required Python libraries..."
pip install netaddr msgpack oslo.config ovs routes tinyrpc

echo "[✅] Installation complete!"
echo "You can now run 'bash run.sh' to start the project."
