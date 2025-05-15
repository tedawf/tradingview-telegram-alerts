#!/bin/bash

set -e

echo "--- Starting tvta deployment ---"

echo "Activating virtualenv"
source .venv/bin/activate || {
  echo "Failed to activate virtualenv"
  exit 1
}

echo "Installing/updating python deps"
pip install -r requirements.txt

echo "Installing playwright headless chromium"
playwright install-deps
playwright install chromium

echo "Deactivating virtualenv"
deactivate

echo "Restarting tvta service"
sudo -n /usr/bin/systemctl restart tvta-bot.service

echo "Checking service status..."
sleep 1
sudo -n /usr/bin/systemctl status tvta-bot.service --no-pager

echo "--- Deployed tvta ---"