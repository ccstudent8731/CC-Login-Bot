#!/usr/bin/env python3
"""Test-Script für lokale Entwicklung mit Konfigurationsdatei."""

import os
import subprocess
import sys
from pathlib import Path


def load_config():
    """Lädt die Test-Konfiguration aus test_config.env."""
    config_file = Path("test_config.env")
    
    if not config_file.exists():
        print("[ERROR] test_config.env nicht gefunden!")
        print("Bitte erstelle die Datei mit deinen Zugangsdaten:")
        print("   CC_USERNAME=dein_username")
        print("   CC_PASSWORD=dein_password")
        print("   CC_HOSTNAME=dein_hostname")
        print("   CC_BOT_TOKEN=dein_bot_token")
        print("   CC_CHAT_ID=dein_chat_id")
        return None
    
    # Lade Umgebungsvariablen aus der Datei
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    
    print("[OK] Konfiguration aus test_config.env geladen")
    return True


def run_test():
    """Führt den Bot-Test aus."""
    if not load_config():
        return False
    
    print("Starte Bot-Test...")
    
    cmd = [
        sys.executable, "-m", "src.cli",
        "--username", os.environ.get("CC_USERNAME", ""),
        "--password", os.environ.get("CC_PASSWORD", ""),
        "--bot-token", os.environ.get("CC_BOT_TOKEN", ""),
        "--chat-id", os.environ.get("CC_CHAT_ID", ""),
        "--host", os.environ.get("CC_HOSTNAME", ""),
        "--mode", "test"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("[SUCCESS] Test erfolgreich!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Test fehlgeschlagen: {e}")
        return False


if __name__ == "__main__":
    run_test()
