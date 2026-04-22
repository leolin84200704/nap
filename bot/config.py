"""Configuration for the personal agent Telegram bot."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from bot directory
_bot_dir = Path(__file__).parent
load_dotenv(_bot_dir / ".env")

# Telegram
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
ALLOWED_USER_IDS: list[int] = [
    int(uid.strip())
    for uid in os.getenv("ALLOWED_USER_IDS", "").split(",")
    if uid.strip()
]

# Anthropic
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

# Paths
AGENT_ROOT: Path = Path(os.getenv("AGENT_ROOT", str(_bot_dir.parent)))
SHORT_TERM_DIR: Path = AGENT_ROOT / "short-term-memory"
LONG_TERM_DIR: Path = AGENT_ROOT / "long-term-memory"
ARCHIVE_DIR: Path = AGENT_ROOT / "archive"
AGENT_MD: Path = AGENT_ROOT / "AGENT.md"
FEEDBACK_MD: Path = AGENT_ROOT / "FEEDBACK.md"
SCRIPTS_DIR: Path = AGENT_ROOT / "scripts"

# Token budget for memory context loading
MAX_CONTEXT_TOKENS: int = int(os.getenv("MAX_CONTEXT_TOKENS", "2000"))

# Conversation history length per user
MAX_HISTORY_LENGTH: int = 20
