"""Agent core: Claude API integration and memory-aware chat."""

import re
import logging
from typing import Any

import anthropic

from . import config
from .memory import MemoryManager

logger = logging.getLogger(__name__)


class AgentCore:
    """The brain of the personal agent. Calls Claude API with memory context."""

    def __init__(self) -> None:
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.memory = MemoryManager()

    def build_system_prompt(self) -> str:
        """Combine AGENT.md rules + FEEDBACK.md into a system prompt."""
        agent_md = self.memory.get_agent_instructions()
        feedback_md = self.memory.get_feedback()

        return (
            "You are the user's personal life agent. "
            "Follow the rules and preferences below exactly.\n\n"
            "# Agent Rules (AGENT.md)\n"
            f"{agent_md}\n\n"
            "# User Preferences (FEEDBACK.md)\n"
            f"{feedback_md}\n\n"
            "# Output Instructions\n"
            "- Respond in the user's language. Use English for technical/legal terms.\n"
            "- Be concise and direct.\n"
            "- When you identify a new action item or task the user should do, "
            "append this structured block at the END of your response:\n"
            "  [MEMORY_ACTION: create_task | <title> | <category> | <priority> | <deadline>]\n"
            "- When you identify something to add as user preference/feedback, append:\n"
            "  [MEMORY_ACTION: update_feedback | <entry>]\n"
            "- You may output multiple MEMORY_ACTION blocks if needed.\n"
            "- Do NOT mention MEMORY_ACTION blocks to the user; they are internal signals.\n"
        )

    def build_context(self, user_message: str) -> str:
        """Load relevant memory as context for the current message."""
        return self.memory.load_context(query=user_message)

    async def chat(
        self,
        user_message: str,
        conversation_history: list[dict[str, str]],
    ) -> str:
        """Send message to Claude API with system prompt + memory context.

        Args:
            user_message: The user's latest message.
            conversation_history: List of {"role": ..., "content": ...} dicts.

        Returns:
            Claude's response text.
        """
        system_prompt = self.build_system_prompt()
        context = self.build_context(user_message)

        # Prepend memory context to the user message
        augmented_message = (
            f"[Current memory context]\n{context}\n\n"
            f"[User message]\n{user_message}"
        )

        messages = list(conversation_history) + [
            {"role": "user", "content": augmented_message}
        ]

        try:
            response = self.client.messages.create(
                model=config.CLAUDE_MODEL,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
            )
            reply = response.content[0].text
        except anthropic.APIError as e:
            logger.error("Claude API error: %s", e)
            return f"API error: {e}"

        # Process any memory actions in the response
        self.detect_memory_actions(reply)

        # Strip MEMORY_ACTION lines from user-facing response
        clean_reply = re.sub(
            r"\[MEMORY_ACTION:.*?\]\s*", "", reply
        ).strip()

        return clean_reply

    def detect_memory_actions(self, response: str) -> list[dict[str, Any]]:
        """Parse and execute memory update signals from Claude's response.

        Looks for patterns like:
            [MEMORY_ACTION: create_task | title | category | priority | deadline]
            [MEMORY_ACTION: update_feedback | entry]

        Returns list of actions taken for logging purposes.
        """
        actions_taken: list[dict[str, Any]] = []
        pattern = r"\[MEMORY_ACTION:\s*(\w+)\s*\|(.*?)\]"

        for match in re.finditer(pattern, response):
            action_type = match.group(1).strip()
            params_str = match.group(2).strip()
            params = [p.strip() for p in params_str.split("|")]

            try:
                if action_type == "create_task" and len(params) >= 4:
                    title, category, priority, deadline = (
                        params[0],
                        params[1],
                        params[2],
                        params[3],
                    )
                    filename = self.memory.create_task(
                        title=title,
                        category=category,
                        priority=priority,
                        deadline=deadline,
                    )
                    actions_taken.append(
                        {"action": "create_task", "file": filename}
                    )
                    logger.info("Created task: %s", filename)

                elif action_type == "update_feedback" and len(params) >= 1:
                    entry = params[0]
                    self.memory.update_feedback(entry)
                    actions_taken.append(
                        {"action": "update_feedback", "entry": entry}
                    )
                    logger.info("Updated feedback: %s", entry)

                else:
                    logger.warning(
                        "Unknown or malformed MEMORY_ACTION: %s", match.group(0)
                    )

            except Exception as e:
                logger.error("Error executing memory action: %s", e)

        return actions_taken
