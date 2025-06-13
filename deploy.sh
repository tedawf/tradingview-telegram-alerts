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

# echo "Installing playwright headless chromium"
# playwright install-deps # needs sudo
# playwright install chromium

echo "Deactivating virtualenv"
deactivate

echo "Restarting tvta service"
sudo -n /usr/bin/systemctl restart tvta-bot.service

echo "Checking service status..."
sleep 1
sudo -n /usr/bin/systemctl status tvta-bot.service --no-pager

# Load variables from .env
export $(grep -v '^#' .env | xargs)

echo "Setting Telegram webhook..."
if [[ -z "$TG_BOT_TOKEN" || -z "$DOMAIN" ]]; then
  echo "Missing TG_BOT_TOKEN or DOMAIN in .env"
  exit 1
fi

WEBHOOK_URL="${DOMAIN}/command"

curl -s -X POST "https://api.telegram.org/bot${TG_BOT_TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"${WEBHOOK_URL}\"}" &&
  echo "Webhook set to: ${WEBHOOK_URL}"

echo "--- Deployed tvta ---"
