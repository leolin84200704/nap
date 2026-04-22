# Telegram Bot

Telegram interface for the personal life agent. Connects to the memory system and uses Claude API to respond.

## Setup

### 1. Create Telegram Bot
- Message [@BotFather](https://t.me/BotFather) on Telegram
- Send `/newbot` and follow the prompts
- Copy the bot token

### 2. Get API Keys
- Get an Anthropic API key from https://console.anthropic.com/

### 3. Configure Environment
```bash
cd bot/
cp .env.example .env
# Edit .env and fill in:
#   TELEGRAM_BOT_TOKEN
#   ANTHROPIC_API_KEY
#   ALLOWED_USER_IDS (your Telegram user ID — message @userinfobot to find it)
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run
```bash
# From the nap root directory:
python -m bot
```

## Commands
- `/start` — Welcome message
- `/tasks` — List active tasks with priority and deadline
- `/dream` — Trigger memory consolidation (runs scripts/run-dream.sh)
- `/status` — Show memory file counts and last dream date
- Any text message — Chat with the agent
