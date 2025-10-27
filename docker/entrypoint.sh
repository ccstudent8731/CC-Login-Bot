#!/bin/sh
set -eu

echo "[*] Prüfe Playwright-Browserinstallation"
if ! playwright show-browsers 2>/dev/null | grep -q chromium; then
  playwright install chromium
fi

echo "[*] Führe initialen Testlauf aus"
if ! python -m src.cli \
  --username "${CC_USERNAME:?Umgebungsvariable CC_USERNAME fehlt}" \
  --password "${CC_PASSWORD:?Umgebungsvariable CC_PASSWORD fehlt}" \
  --bot-token "${CC_BOT_TOKEN:?Umgebungsvariable CC_BOT_TOKEN fehlt}" \
  --chat-id "${CC_CHAT_ID:?Umgebungsvariable CC_CHAT_ID fehlt}" \
  --host "${CC_HOSTNAME:?Umgebungsvariable CC_HOSTNAME fehlt}" \
  --mode test; then
  echo "[!] Initialer Testlauf fehlgeschlagen" >&2
fi

echo "[*] Initialisiere Cronjob-Datei"
python -m src.scheduler \
  --cron-file /etc/cron.d/cc-bot \
  --username "${CC_USERNAME:?Umgebungsvariable CC_USERNAME fehlt}" \
  --password "${CC_PASSWORD:?Umgebungsvariable CC_PASSWORD fehlt}" \
  --bot-token "${CC_BOT_TOKEN:?Umgebungsvariable CC_BOT_TOKEN fehlt}" \
  --chat-id "${CC_CHAT_ID:?Umgebungsvariable CC_CHAT_ID fehlt}" \
  --host "${CC_HOSTNAME:?Umgebungsvariable CC_HOSTNAME fehlt}" \
  ${CC_START_TIME:+--start-time "$CC_START_TIME"} \
  ${CC_END_TIME:+--end-time "$CC_END_TIME"} \
  ${CC_VARIATION_MINUTES:+--variation-minutes "$CC_VARIATION_MINUTES"} \
  ${CC_DISABLE_VARIATION:+--disable-variation}

