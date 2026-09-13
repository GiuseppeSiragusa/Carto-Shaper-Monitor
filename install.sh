#!/bin/bash

echo "Installing Carto-Shaper Monitor..."

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

deactivate

# Install systemd service
sudo cp config/carto-shaper.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable carto-shaper.service
sudo systemctl restart carto-shaper.service

echo "Installation complete."
