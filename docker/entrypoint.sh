#!/bin/sh
set -eu

# Zeitzone konfigurieren (Standard: UTC)
export TZ="${CC_TIMEZONE:-UTC}"
echo "[*] Zeitzone gesetzt auf: $TZ"

echo "[*] Prüfe Playwright-Browserinstallation"
if ! playwright show-browsers 2>/dev/null | grep -q chromium; then
  playwright install chromium
fi

echo "[*] Führe initialen Testlauf aus"
echo "[*] Teste Login-Funktionalität..."
if python -m src.cli \
  --username "${CC_USERNAME:?Umgebungsvariable CC_USERNAME fehlt}" \
  --password "${CC_PASSWORD:?Umgebungsvariable CC_PASSWORD fehlt}" \
  --bot-token "${CC_BOT_TOKEN:?Umgebungsvariable CC_BOT_TOKEN fehlt}" \
  --chat-id "${CC_CHAT_ID:?Umgebungsvariable CC_CHAT_ID fehlt}" \
  --host "${CC_HOSTNAME:?Umgebungsvariable CC_HOSTNAME fehlt}" \
  --mode test; then
  echo "[✓] Login-Test erfolgreich - Bot ist bereit!"
else
  echo "[✗] Login-Test fehlgeschlagen - Bot wird trotzdem gestartet" >&2
  echo "[!] Bitte überprüfe deine Credentials und Hostname-Einstellungen" >&2
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
  ${CC_TIMEZONE:+--timezone "$CC_TIMEZONE"} \
  ${CC_DISABLE_VARIATION:+--disable-variation}

