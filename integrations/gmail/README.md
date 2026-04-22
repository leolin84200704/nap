---
integration: gmail
status: live
method: MCP server
---

# Gmail Integration

## Setup
- MCP server: `@gongrzhe/server-gmail-autoauth-mcp`
- Credentials: `~/.gmail-mcp/credentials.json`
- Follow the MCP server's README for OAuth setup

## Available Operations
- `search_emails` — search emails by query
- `read_email` — read email content by ID
- `list_email_labels` — list all labels

## Use Cases
- "Any important emails?" → search & summarize recent emails
- Extract action items from emails → create tasks in short-term-memory
- Track important correspondence
