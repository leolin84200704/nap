"""Memory manager for reading and writing personal agent memory files."""

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from . import config


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter and body from a markdown file.

    Returns (metadata_dict, body_text). If no frontmatter found,
    returns ({}, full_text).
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, match.group(2)


def _dump_frontmatter(meta: dict[str, Any], body: str) -> str:
    """Combine YAML frontmatter dict and body into a markdown string."""
    fm = yaml.dump(meta, default_flow_style=False, allow_unicode=True).strip()
    return f"---\n{fm}\n---\n{body}"


class MemoryManager:
    """Handles all memory file operations for the personal agent."""

    def __init__(self) -> None:
        self.stm_dir = config.SHORT_TERM_DIR
        self.ltm_dir = config.LONG_TERM_DIR
        self.archive_dir = config.ARCHIVE_DIR

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def load_index(self, memory_type: str) -> list[dict[str, str]]:
        """Read _index.md for a memory type and return parsed table rows.

        Args:
            memory_type: 'short-term' or 'long-term'

        Returns:
            List of dicts, one per table row, with column headers as keys.
        """
        if memory_type == "short-term":
            path = self.stm_dir / "_index.md"
        elif memory_type == "long-term":
            path = self.ltm_dir / "_index.md"
        else:
            return []

        text = self._read_file(path)
        if not text:
            return []

        _, body = _parse_frontmatter(text)
        return self._parse_md_table(body)

    def load_file(self, filepath: str | Path) -> dict[str, Any]:
        """Read a memory .md file and return parsed frontmatter + body.

        Returns:
            {"meta": dict, "body": str, "raw": str} or empty dict on error.
        """
        path = Path(filepath)
        # Allow relative paths within the agent root
        if not path.is_absolute():
            path = config.AGENT_ROOT / path
        text = self._read_file(path)
        if not text:
            return {}
        meta, body = _parse_frontmatter(text)
        return {"meta": meta, "body": body, "raw": text}

    def load_context(self, query: str | None = None) -> str:
        """Build a context string from memory for the Claude API call.

        Always includes AGENT.md, FEEDBACK.md, and both indexes.
        If a query is provided, score-match and include top relevant
        memory files within the token budget.
        """
        parts: list[str] = []
        budget = config.MAX_CONTEXT_TOKENS

        # Always load indexes (lightweight)
        stm_index = self.load_index("short-term")
        ltm_index = self.load_index("long-term")

        stm_table = self._format_index("Active Tasks (short-term)", stm_index)
        ltm_table = self._format_index("Long-Term Memory", ltm_index)
        parts.append(stm_table)
        parts.append(ltm_table)
        budget -= self.estimate_tokens(stm_table + ltm_table)

        if query and budget > 0:
            # Score files by keyword overlap with query
            query_words = set(query.lower().split())
            candidates = self._gather_candidates()
            scored = []
            for filepath, preview in candidates:
                words = set(preview.lower().split())
                overlap = len(query_words & words)
                if overlap > 0:
                    scored.append((overlap, filepath))
            scored.sort(reverse=True)

            for _, fp in scored:
                data = self.load_file(fp)
                if not data:
                    continue
                chunk = f"\n### Memory: {fp.name}\n{data['raw']}\n"
                tokens = self.estimate_tokens(chunk)
                if tokens > budget:
                    continue
                parts.append(chunk)
                budget -= tokens

        return "\n".join(parts)

    def get_agent_instructions(self) -> str:
        """Read AGENT.md and return its content."""
        return self._read_file(config.AGENT_MD)

    def get_feedback(self) -> str:
        """Read FEEDBACK.md and return its content."""
        return self._read_file(config.FEEDBACK_MD)

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------

    def create_task(
        self,
        title: str,
        category: str,
        priority: str = "medium",
        deadline: str = "flexible",
        details: str = "",
    ) -> str:
        """Create a new short-term-memory task file and update _index.md.

        Returns the filename of the created task.
        """
        # Generate filename from title
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        filename = f"{slug}.md"
        filepath = self.stm_dir / filename

        today = date.today().isoformat()
        meta = {
            "title": title,
            "status": "pending",
            "priority": priority,
            "deadline": deadline,
            "category": category,
            "created": today,
            "updated": today,
        }
        body = f"\n## Summary\n{details}\n"
        filepath.write_text(_dump_frontmatter(meta, body), encoding="utf-8")

        # Update _index.md
        self._append_to_index(
            self.stm_dir / "_index.md",
            f"| {filename} | {title} | {priority} | {deadline} | pending | {category} |",
        )
        return filename

    def update_task(self, filename: str, updates: dict[str, Any]) -> bool:
        """Update fields in an existing short-term-memory task file.

        Args:
            filename: Name of the .md file in short-term-memory/
            updates: Dict of frontmatter fields to update.

        Returns:
            True on success, False if file not found.
        """
        filepath = self.stm_dir / filename
        text = self._read_file(filepath)
        if not text:
            return False

        meta, body = _parse_frontmatter(text)
        meta.update(updates)
        meta["updated"] = date.today().isoformat()
        filepath.write_text(_dump_frontmatter(meta, body), encoding="utf-8")
        return True

    def update_feedback(self, entry: str) -> None:
        """Append a new entry to FEEDBACK.md."""
        path = config.FEEDBACK_MD
        text = self._read_file(path)
        if not text:
            return
        # Append before the Changelog section if it exists
        if "## Changelog" in text:
            text = text.replace(
                "## Changelog",
                f"- {entry}\n\n## Changelog",
            )
        else:
            text += f"\n- {entry}\n"
        path.write_text(text, encoding="utf-8")

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token count: characters / 4."""
        return len(text) // 4

    def _read_file(self, path: Path) -> str:
        """Read a file, returning empty string on error."""
        try:
            return path.read_text(encoding="utf-8")
        except (FileNotFoundError, PermissionError):
            return ""

    def _parse_md_table(self, text: str) -> list[dict[str, str]]:
        """Parse a markdown table into a list of dicts."""
        lines = [
            line.strip()
            for line in text.strip().splitlines()
            if line.strip().startswith("|")
        ]
        if len(lines) < 3:
            return []
        headers = [h.strip() for h in lines[0].strip("|").split("|")]
        rows: list[dict[str, str]] = []
        for line in lines[2:]:  # skip header + separator
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
        return rows

    def _format_index(self, title: str, entries: list[dict[str, str]]) -> str:
        """Format index entries into a readable text block."""
        if not entries:
            return f"## {title}\n(empty)\n"
        lines = [f"## {title}"]
        for entry in entries:
            parts = " | ".join(f"{k}: {v}" for k, v in entry.items())
            lines.append(f"- {parts}")
        return "\n".join(lines) + "\n"

    def _gather_candidates(self) -> list[tuple[Path, str]]:
        """Collect all memory .md files (excluding _index.md) with preview text."""
        candidates: list[tuple[Path, str]] = []
        for d in [self.stm_dir, self.ltm_dir]:
            if not d.exists():
                continue
            for f in d.glob("*.md"):
                if f.name == "_index.md":
                    continue
                text = self._read_file(f)
                # Use first 500 chars as preview for matching
                candidates.append((f, text[:500]))
        return candidates

    def _append_to_index(self, index_path: Path, row: str) -> None:
        """Append a table row to an _index.md file."""
        text = self._read_file(index_path)
        if text:
            text = text.rstrip() + "\n" + row + "\n"
        else:
            text = row + "\n"
        index_path.write_text(text, encoding="utf-8")
