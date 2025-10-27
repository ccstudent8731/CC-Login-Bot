# CC Login Bot - Docker Hub Overview

## 🚀 **CC Login Bot - Automatische Zeiterfassung für Comcave Portal**

Ein intelligenter Bot für die automatische Zeiterfassung im Comcave Student Portal mit Telegram-Benachrichtigungen und robusten Fehlerbehandlungsmechanismen.

## ✨ **Features**

### 🔐 **Robuste Authentifizierung**
- Intelligente Login-Button-Erkennung mit dynamischen IDs
- Mehrere Fallback-Selektoren für maximale Kompatibilität
- Human-like Interaktionen zur Vermeidung von Bot-Erkennung

### ⏰ **Intelligente Zeiterfassung**
- Automatisches Starten (Kommen) und Beenden (Gehen) der Zeiterfassung
- Robuste Dialog-Button-Erkennung mit dynamischen IDs
- Vollständige Screenshots der Zeiterfassungsseite
- Intelligente Status-Erkennung und -Validierung

### 📅 **Smart Caching System**
- 30-Tage-Cache für Feiertage zur Reduzierung von Portal-Zugriffen
- Automatische Filterung nur zukünftiger Termine
- 30x schnellere Ladezeiten bei wiederholten Läufen
- Intelligente Cache-Erneuerung nach 30 Tagen

### 📱 **Telegram Integration**
- Automatische Benachrichtigungen mit Screenshots
- Detaillierte Status-Informationen
- Graceful Behandlung von Rate-Limits
- Vollständige Fehlerbehandlung

### 🛡️ **Robuste Fehlerbehandlung**
- Timeout-Management für alle Operationen
- Graceful Behandlung von Netzwerkfehlern
- Umfassende Logging-Funktionalität
- Automatische Wiederholungsmechanismen

## 🐳 **Docker Images**

### **Latest Version: 0.0.4**
```bash
docker pull ccstudent8731/cc-login-bot:latest
```

### **Alle verfügbaren Tags**
- `ccstudent8731/cc-login-bot:0.0.4` - Latest stable
- `ccstudent8731/cc-login-bot:latest` - Latest stable


## 🚀 **Schnellstart**

### **1. Docker Container starten**
```bash
docker run -d \
  --name cc-login-bot \
  -e CC_USERNAME="dein_username" \
  -e CC_PASSWORD="dein_password" \
  -e CC_HOSTNAME="portal.cc-student.com" \
  -e CC_BOT_TOKEN="dein_telegram_bot_token" \
  -e CC_CHAT_ID="dein_telegram_chat_id" \
  ccstudent8731/cc-login-bot:0.0.4
```

### **2. Manuelle Ausführung**
```bash
docker run --rm \
  -e CC_USERNAME="dein_username" \
  -e CC_PASSWORD="dein_password" \
  -e CC_HOSTNAME="portal.cc-student.com" \
  -e CC_BOT_TOKEN="dein_telegram_bot_token" \
  -e CC_CHAT_ID="dein_telegram_chat_id" \
  ccstudent8731/cc-login-bot:0.0.4 \
  python -m src.cli --mode start
```

## ⚙️ **Konfiguration**

### **Erforderliche Umgebungsvariablen**
| Variable | Beschreibung | Beispiel |
|----------|--------------|----------|
| `CC_USERNAME` | Portal Benutzername | `student123` |
| `CC_PASSWORD` | Portal Passwort | `mein_passwort` |
| `CC_HOSTNAME` | Portal Hostname | `portal.cc-student.com` |
| `CC_BOT_TOKEN` | Telegram Bot Token | `123456789:ABC...` |
| `CC_CHAT_ID` | Telegram Chat ID | `123456789` |

### **Optionale Parameter**
| Parameter | Beschreibung | Standard |
|-----------|--------------|----------|
| `--mode` | Modus: start, stop, test | `test` |
| `--timeout` | Timeout in Sekunden | `45` |
| `--headless` | Headless Browser-Modus | `true` |
| `--log-level` | Logging-Level | `INFO` |

## 📋 **Verfügbare Modi**

### **Start (Kommen)**
```bash
docker run --rm \
  -e CC_USERNAME="..." \
  -e CC_PASSWORD="..." \
  -e CC_HOSTNAME="..." \
  -e CC_BOT_TOKEN="..." \
  -e CC_CHAT_ID="..." \
  ccstudent8731/cc-login-bot:0.0.4 \
  python -m src.cli --mode start
```

### **Stop (Gehen)**
```bash
docker run --rm \
  -e CC_USERNAME="..." \
  -e CC_PASSWORD="..." \
  -e CC_HOSTNAME="..." \
  -e CC_BOT_TOKEN="..." \
  -e CC_CHAT_ID="..." \
  ccstudent8731/cc-login-bot:0.0.4 \
  python -m src.cli --mode stop
```

### **Test**
```bash
docker run --rm \
  -e CC_USERNAME="..." \
  -e CC_PASSWORD="..." \
  -e CC_HOSTNAME="..." \
  -e CC_BOT_TOKEN="..." \
  -e CC_CHAT_ID="..." \
  ccstudent8731/cc-login-bot:0.0.4 \
  python -m src.cli --mode test --timezone Europe/Amsterdam
```

### **Mit benutzerdefinierten Zeiten**
```bash
# Start um 08:30 Uhr
docker run --rm \
  -e CC_USERNAME="..." \
  -e CC_PASSWORD="..." \
  -e CC_HOSTNAME="..." \
  -e CC_BOT_TOKEN="..." \
  -e CC_CHAT_ID="..." \
  ccstudent8731/cc-login-bot:0.0.4 \
  python -m src.cli --mode start --timezone Europe/Amsterdam --start-time 08:30 --end-time 17:00

# Stop um 18:00 Uhr
docker run --rm \
  -e CC_USERNAME="..." \
  -e CC_PASSWORD="..." \
  -e CC_HOSTNAME="..." \
  -e CC_BOT_TOKEN="..." \
  -e CC_CHAT_ID="..." \
  ccstudent8731/cc-login-bot:0.0.4 \
  python -m src.cli --mode stop --timezone Europe/Amsterdam --start-time 08:30 --end-time 18:00
```

## ⏰ **Automatische Ausführung**

### **Wann führt der Bot welche Aktionen aus?**

Der Bot kann automatisch zu bestimmten Zeiten die Zeiterfassung starten und beenden:

#### **🕘 Start (Kommen) - Arbeitsbeginn**
- **Zeit**: Normalerweise um 09:00 Uhr (konfigurierbar)
- **Aktion**: Startet die Zeiterfassung ("Kommen")
- **Variation**: ±2 Minuten Zufallsvariation zur Vermeidung von Bot-Erkennung
- **Wochentage**: Montag bis Freitag (werktags)
- **Feiertage**: Automatische Erkennung und Überspringen von Feiertagen
- **Zeitzone**: Konfigurierbar (Standard: UTC)

#### **🕔 Stop (Gehen) - Arbeitsende**
- **Zeit**: Normalerweise um 17:00 Uhr (konfigurierbar)
- **Aktion**: Beendet die Zeiterfassung ("Gehen")
- **Variation**: ±2 Minuten Zufallsvariation zur Vermeidung von Bot-Erkennung
- **Wochentage**: Montag bis Freitag (werktags)
- **Feiertage**: Automatische Erkennung und Überspringen von Feiertagen
- **Zeitzone**: Konfigurierbar (Standard: UTC)

#### **🧠 Intelligente Logik**
- **Status-Prüfung**: Bot prüft vor jeder Aktion den aktuellen Status
- **Keine Doppelbuchungen**: Wenn bereits "Kommen" gebucht ist, wird kein weiteres "Kommen" ausgeführt
- **Feiertags-Erkennung**: Automatisches Überspringen an unterrichtsfreien Tagen
- **Fehlerbehandlung**: Bei Fehlern wird eine Telegram-Benachrichtigung gesendet
- **Zeitzonen-Unterstützung**: Korrekte Zeitberechnung in verschiedenen Zeitzonen

#### **🌍 Zeitzonen-Konfiguration**
- **Standard**: UTC (Universal Time Coordinated)
- **Niederlande**: `Europe/Amsterdam` (CET/CEST)
- **Deutschland**: `Europe/Berlin` (CET/CEST)
- **Andere Zeitzonen**: `America/New_York`, `Asia/Tokyo`, etc.
- **Umgebungsvariable**: `CC_TIMEZONE=Europe/Amsterdam`
- **CLI-Parameter**: `--timezone Europe/Amsterdam`

#### **⏰ Zeit-Konfiguration**
- **Startzeit**: `--start-time 09:00` (Standard: 13:20)
- **Endzeit**: `--end-time 17:30` (Standard: 17:30)
- **Variation**: `--variation-minutes 2` (Standard: ±2 Minuten)
- **Format**: `HH:MM` (24-Stunden-Format)
- **Beispiele**: `09:00`, `13:30`, `17:00`, `18:30`

#### **📅 Beispiel-Ablauf**
```
Montag 09:02 Uhr → Bot startet Zeiterfassung (Kommen)
Montag 17:01 Uhr → Bot beendet Zeiterfassung (Gehen)
Dienstag 09:00 Uhr → Bot startet Zeiterfassung (Kommen)
Dienstag 17:03 Uhr → Bot beendet Zeiterfassung (Gehen)
Mittwoch (Feiertag) → Bot überspringt beide Aktionen
Donnerstag 09:01 Uhr → Bot startet Zeiterfassung (Kommen)
...
```

## 🔄 **Automatisierung mit Cron**

### **Cron-Jobs für automatische Ausführung**

#### **Start (Kommen) um 09:00 Uhr**
```bash
# Crontab-Eintrag für Start um 09:00 Uhr (werktags)
0 9 * * 1-5 docker run --rm \
  -e CC_USERNAME="dein_username" \
  -e CC_PASSWORD="dein_password" \
  -e CC_HOSTNAME="portal.cc-student.com" \
  -e CC_BOT_TOKEN="dein_bot_token" \
  -e CC_CHAT_ID="dein_chat_id" \
  -e CC_TIMEZONE="Europe/Amsterdam" \
  ccstudent8731/cc-login-bot:0.0.4 \
  python -m src.cli --mode start --apply-variation --timezone Europe/Amsterdam --start-time 09:00 --end-time 17:30
```

#### **Stop (Gehen) um 17:00 Uhr**
```bash
# Crontab-Eintrag für Stop um 17:00 Uhr (werktags)
0 17 * * 1-5 docker run --rm \
  -e CC_USERNAME="dein_username" \
  -e CC_PASSWORD="dein_password" \
  -e CC_HOSTNAME="portal.cc-student.com" \
  -e CC_BOT_TOKEN="dein_bot_token" \
  -e CC_CHAT_ID="dein_chat_id" \
  -e CC_TIMEZONE="Europe/Amsterdam" \
  ccstudent8731/cc-login-bot:0.0.4 \
  python -m src.cli --mode stop --apply-variation --timezone Europe/Amsterdam --start-time 09:00 --end-time 17:30
```

#### **Crontab installieren**
```bash
# Crontab bearbeiten
crontab -e

# Folgende Zeilen hinzufügen:
0 9 * * 1-5 /path/to/start_script.sh
0 17 * * 1-5 /path/to/stop_script.sh
```

### **Docker Compose Beispiel**
```yaml
version: '3.8'
services:
  cc-login-bot:
    image: ccstudent8731/cc-login-bot:0.0.4
    environment:
      - CC_USERNAME=${CC_USERNAME}
      - CC_PASSWORD=${CC_PASSWORD}
      - CC_HOSTNAME=${CC_HOSTNAME}
      - CC_BOT_TOKEN=${CC_BOT_TOKEN}
      - CC_CHAT_ID=${CC_CHAT_ID}
      - CC_TIMEZONE=Europe/Amsterdam
    volumes:
      - ./artifacts:/app/artifacts
    restart: unless-stopped
```

## 📊 **Performance & Optimierungen**

### **Caching-System**
- **30-Tage-Cache** für Feiertage
- **30x schnellere Ladezeiten** bei wiederholten Läufen
- **Intelligente Filterung** nur zukünftiger Termine
- **Automatische Cache-Erneuerung**

### **Robustheit**
- **Dynamische ID-Behandlung** für alle Portal-Elemente
- **Mehrere Fallback-Selektoren** für maximale Kompatibilität
- **Graceful Fehlerbehandlung** für alle Edge Cases
- **Timeout-Management** für alle Operationen

## 🔧 **Technische Details**

### **Basis-Image**
- `python:3.12-slim` - Leichtgewichtiges Python-Image
- Chromium Browser für Web-Automation
- Alle notwendigen System-Dependencies

### **Größe**
- **~500MB** - Optimiert für Produktion
- **Schnelle Startzeiten** durch intelligentes Caching
- **Minimale Ressourcennutzung**

### **Sicherheit**
- **Keine Credentials im Image** - Nur über Umgebungsvariablen
- **Isolierte Ausführung** in Docker-Container
- **Minimale Angriffsfläche** durch slim Image

## 📈 **Changelog**

### **Version 0.0.4** (Latest)
- ✅ **Zeitzonen-Unterstützung** - Vollständige Konfiguration für alle Zeitzonen
- ✅ **Europe/Amsterdam** - Optimiert für niederländische Zeitzone
- ✅ **CLI-Parameter** `--timezone` für flexible Zeitzonen-Konfiguration
- ✅ **Zeit-Konfiguration** `--start-time` und `--end-time` für flexible Arbeitszeiten
- ✅ **Docker-Integration** mit `CC_TIMEZONE` Umgebungsvariable
- ✅ **Intelligente Zeitberechnung** mit korrekter Zeitzonen-Behandlung
- ✅ Robuste dynamische ID-Behandlung für alle Portal-Elemente
- ✅ Intelligente Fallback-Mechanismen für Button-Erkennung
- ✅ Vollständige Tests für Start (Kommen) und Stop (Gehen) Modi
- ✅ Verbesserte Debugging-Ausgaben
- ✅ Optimierte Screenshot-Reihenfolge

### **Version 0.0.2**
- ✅ Intelligentes 30-Tage-Caching für Feiertage
- ✅ Zukunftsfilter für relevante Termine
- ✅ Graceful Telegram Rate-Limit-Behandlung
- ✅ Vollständige Seiten-Screenshots
- ✅ Robuste Login-Button-Erkennung

### **Version 0.0.1**
- ✅ Grundlegende Zeiterfassungs-Funktionalität
- ✅ Telegram-Integration
- ✅ Docker-Containerisierung

## 🆘 **Support & Troubleshooting**

### **Häufige Probleme**

**Login-Fehler:**

**Telegram-Probleme:**
- Bot-Token überprüfen
- Chat-ID korrekt setzen
- Rate-Limits beachten

**Portal-Zugriff:**
- Hostname korrekt setzen
- Credentials überprüfen
- Netzwerk-Verbindung testen

### **Logs anzeigen**
```bash
docker logs cc-login-bot
```

## 🔗 **Links**

- **GitHub Repository**: https://github.com/ccstudent8731/CC-Login-Bot
- **Docker Hub**: https://hub.docker.com/r/ccstudent8731/cc-login-bot

## 📄 **Lizenz**

MIT License - Siehe [LICENSE](https://github.com/ccstudent8731/Comcave-Login-Bot/blob/main/LICENSE) für Details.

---