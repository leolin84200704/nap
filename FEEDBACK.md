---
description: User preferences and behavioral feedback for agent tuning. THIS FILE IS THE HIGHEST-PRIORITY INPUT — it overrides AGENT.md when conflicts arise.
updated: 2026-04-22
---

# Feedback & Preferences

This file drives agent evolution. Every entry here is a binding instruction. When a new entry conflicts with AGENT.md, update AGENT.md to align.

---

## Communication
- Respond in user's language; use English for technical/legal terms
- Be concise, no fluff
- When listing tasks, always show priority and deadline

## Task Management
- User prefers asking "what do I need to do" and getting a prioritized list
- Don't over-explain obvious things
- Flag items becoming urgent (< 2 weeks to deadline)

## Updates
- After each conversation, proactively update memory files
- Don't ask permission to update — just do it
- Log changes in task history sections

## Framework & Documentation
- All framework/config files should be in English
- Output language follows user's language dynamically

## Agent Self-Evolution
- User feedback is the #1 priority input — always persist and apply
- Never require the same correction twice
- When feedback changes agent behavior, update both this file AND AGENT.md

---

## Changelog

Record structural changes to the agent triggered by user feedback.

| Date | Feedback | Change Made |
|------|----------|-------------|
| 2026-04-22 | Initial setup | Created FEEDBACK.md with default preferences |
