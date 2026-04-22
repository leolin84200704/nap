---
integration: google-calendar
status: planned
method: Google Calendar API + MCP server
priority: P0
---

# Google Calendar Integration

## Goal
Read/write Google Calendar for event management, conflict detection, and reminders.

## Setup Steps
1. Enable Calendar API in Google Cloud Console (same project as Gmail)
2. Add OAuth scope: `https://www.googleapis.com/auth/calendar`
3. Build or use existing MCP server (e.g. `@anthropic/gcal-mcp` or custom)
4. Store credentials at `~/.gcal-mcp/credentials.json`

## Planned Operations
- Query today's / this week's events
- Create new events
- Modify / delete events
- Conflict detection (new event vs existing schedule)

## Use Cases
- Morning briefing: list today's schedule
- "Am I free Saturday?" → check Calendar and respond
- Auto-add event invitations from email to Calendar
