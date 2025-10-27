## CC Login Bot

Automates daily check-in/out on the CC portal using Playwright. The bot logs in, checks the current attendance status, presses the required button, captures a screenshot, and notifies a Telegram chat. A cron-driven Docker container adds time variation, supports a test mode, and skips CC-free days detected on the course overview.

### Hostname Requirement
- You **must** provide the portal hostname via `--host` (CLI) or `CC_HOSTNAME` (Docker).  
- Unsure which hostname to use? See the community hints at: https://pastebin.com/search?q=bot+hostname+cc

### Build or Pull
- Build locally: `docker build -t cc-login-bot .`
- Or pull from Docker Hub after it is published: `docker pull <your-dockerhub-user>/cc-login-bot`

### Run Example (Docker)
```bash
docker run -d --name cc-bot \
  -e CC_USERNAME=<USERNAME> \
  -e CC_PASSWORD=<PASSWORD> \
  -e CC_BOT_TOKEN=<TELEGRAM_BOT_TOKEN> \
  -e CC_CHAT_ID=<CHAT_ID> \
  -e CC_HOSTNAME=<PORTAL_HOST> \
  cc-login-bot
```

### Run Example (Manual Test)
```bash
python -m src.cli \
  --username <USERNAME> \
  --password <PASSWORD> \
  --bot-token <TELEGRAM_BOT_TOKEN> \
  --chat-id <CHAT_ID> \
  --host <PORTAL_HOST> \
  --mode test
```

### Features
- Playwright automation with human-like interactions
- Telegram screenshot notifications
- Sunday scan for CC-free days
- Randomized time variation for cron runs
- Test mode for login-only health checks

### License
This project is released under the MIT License. See `LICENSE` for details.
