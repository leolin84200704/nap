"""Telegram bot for the personal life agent."""

import asyncio
import logging
import subprocess
from collections import defaultdict
from pathlib import Path

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from . import config
from .agent_core import AgentCore
from .memory import MemoryManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Per-user conversation history (in-memory)
_histories: dict[int, list[dict[str, str]]] = defaultdict(list)

# Shared instances
agent = AgentCore()
memory = MemoryManager()


# ------------------------------------------------------------------
# Auth decorator
# ------------------------------------------------------------------

def owner_only(func):
    """Decorator to restrict handlers to allowed user IDs."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if config.ALLOWED_USER_IDS and user_id not in config.ALLOWED_USER_IDS:
            await update.message.reply_text("Unauthorized.")
            return
        return await func(update, context)
    return wrapper


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

async def send_long_message(update: Update, text: str) -> None:
    """Send a message, splitting at 4096 char limit if needed."""
    limit = 4096
    while text:
        chunk = text[:limit]
        # Try to split at a newline for cleaner output
        if len(text) > limit:
            split_at = chunk.rfind("\n")
            if split_at > limit // 2:
                chunk = text[:split_at]
        await update.message.reply_text(chunk)
        text = text[len(chunk):]


def _trim_history(user_id: int) -> None:
    """Keep only the last MAX_HISTORY_LENGTH messages."""
    hist = _histories[user_id]
    if len(hist) > config.MAX_HISTORY_LENGTH:
        _histories[user_id] = hist[-config.MAX_HISTORY_LENGTH:]


# ------------------------------------------------------------------
# Command handlers
# ------------------------------------------------------------------

@owner_only
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message."""
    await update.message.reply_text(
        "Hi! I'm your personal life agent.\n\n"
        "I can help you manage tasks, check your schedule, and remember "
        "things for you.\n\n"
        "Commands:\n"
        "/tasks - List active tasks\n"
        "/status - Memory stats\n"
        "/dream - Trigger memory consolidation\n\n"
        "Or just send me a message and I'll help."
    )


@owner_only
async def cmd_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List active tasks from short-term memory."""
    entries = memory.load_index("short-term")
    if not entries:
        await update.message.reply_text("No active tasks found.")
        return

    lines = ["**Active Tasks**\n"]
    for entry in entries:
        status = entry.get("Status", "?")
        title = entry.get("Title", entry.get("File", "?"))
        priority = entry.get("Priority", "?")
        deadline = entry.get("Deadline", "?")
        emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
        lines.append(f"{emoji} {title}\n   Priority: {priority} | Deadline: {deadline} | Status: {status}")

    await send_long_message(update, "\n".join(lines))


@owner_only
async def cmd_dream(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manually trigger the dream process."""
    script = config.SCRIPTS_DIR / "run-dream.sh"
    if not script.exists():
        await update.message.reply_text("Dream script not found.")
        return

    await update.message.reply_text("Starting dream process...")
    try:
        proc = await asyncio.create_subprocess_exec(
            "bash", str(script),
            cwd=str(config.AGENT_ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
        if proc.returncode == 0:
            await update.message.reply_text("Dream process completed.")
        else:
            error = stderr.decode()[:500] if stderr else "Unknown error"
            await update.message.reply_text(f"Dream process failed:\n{error}")
    except asyncio.TimeoutError:
        await update.message.reply_text("Dream process timed out (5 min limit).")
    except Exception as e:
        await update.message.reply_text(f"Error running dream: {e}")


@owner_only
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show memory stats."""
    def count_md(d: Path) -> int:
        if not d.exists():
            return 0
        return len([f for f in d.glob("*.md") if f.name != "_index.md"])

    stm_count = count_md(config.SHORT_TERM_DIR)
    ltm_count = count_md(config.LONG_TERM_DIR)
    archive_count = count_md(config.ARCHIVE_DIR)

    # Check last dream log
    log_dir = config.AGENT_ROOT / "logs"
    last_dream = "unknown"
    if log_dir.exists():
        logs = sorted(log_dir.glob("*.log"), reverse=True)
        if logs:
            last_dream = logs[0].stem

    text = (
        f"Memory Stats\n"
        f"- Short-term tasks: {stm_count}\n"
        f"- Long-term memories: {ltm_count}\n"
        f"- Archived: {archive_count}\n"
        f"- Last dream log: {last_dream}"
    )
    await update.message.reply_text(text)


# ------------------------------------------------------------------
# Message handler
# ------------------------------------------------------------------

@owner_only
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Forward text messages to AgentCore and return the response."""
    user_id = update.effective_user.id
    user_text = update.message.text

    if not user_text:
        return

    # Build conversation history for Claude
    history = _histories[user_id]

    try:
        reply = await agent.chat(user_text, history)
    except Exception as e:
        logger.error("Chat error: %s", e)
        await update.message.reply_text("Something went wrong. Please try again.")
        return

    # Update history
    history.append({"role": "user", "content": user_text})
    history.append({"role": "assistant", "content": reply})
    _trim_history(user_id)

    await send_long_message(update, reply)


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main() -> None:
    """Start the Telegram bot."""
    if not config.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Check your .env file.")
    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set. Check your .env file.")

    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("tasks", cmd_tasks))
    app.add_handler(CommandHandler("dream", cmd_dream))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
