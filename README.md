# Dream Agent

**A personal life agent with bio-inspired memory consolidation.**

Dream Agent is an AI-powered personal assistant that manages your tasks, emails, calendar, and life context — with a memory system modeled after how the human brain consolidates memories during sleep.

Unlike typical AI memory systems that use vector databases, Dream Agent uses **Markdown files + scheduled offline dreaming** for transparent, auditable, zero-infrastructure memory management.

---

## Why Dream Agent?

LLM-based personal agents face a fundamental tension: **context windows are finite, but life is not.**

Without active memory management, agent memory systems suffer from accumulation bloat, flat retrieval, no consolidation, and no forgetting. Dream Agent solves this by borrowing from neuroscience:

> During "sleep" (idle time between sessions), the agent consolidates episodic memories into semantic knowledge, prunes irrelevant details, and reorganizes connections — just like the human brain does during REM sleep.

### Key Features

- **3-Tier Scored Memory** — Working / Short-term / Long-term with importance scoring and decay
- **Auto Dreaming** — Scheduled offline consolidation: extract, merge, promote, archive, forget
- **Forgetting Curve** — Memories decay over time based on Ebbinghaus-inspired scoring
- **Zettelkasten Cross-Linking** — Memories form a connected graph, not isolated files
- **File-Based & Git-Friendly** — Human-readable Markdown + YAML frontmatter, full version history
- **Zero Infrastructure** — No database, no embedding model, no GPU. Just files + Claude
- **Multi-Channel** — Claude Code CLI, Telegram bot, scheduled cron — all sharing the same memory
- **MCP Integrations** — Gmail (live), Calendar, Finance, Health (planned)
- **Feedback-Driven Self-Evolution** — The agent learns and adapts from every user correction

### Why Markdown Files Instead of Vector DB?

| | Vector DB (Chroma, Pinecone, etc.) | Dream Agent (Markdown + Dreaming) |
|---|---|---|
| **Semantic search** | Native, real-time | Approximated via cross-linking + LLM scoring at dream-time |
| **Scale** | Millions of records | 50–500 files (personal agent scale) |
| **Human readability** | Poor (opaque embeddings) | Excellent (open any file, read it) |
| **Auditability** | Requires tooling | Git diff, git log, git blame |
| **Infrastructure** | DB server + embedding model | None — just files |
| **Multi-channel access** | Needs API wrapper | Direct file read from any process |
| **Transparency** | Black-box similarity scores | Explicit YAML scores, links, decay |

> **"Vector DB is for agents that search millions of memories in real-time. File-based dreaming is for personal agents that need transparent, auditable, zero-infra memory with offline consolidation."**

The key insight from [Sleep-time Compute](https://arxiv.org/abs/2504.13171): move expensive computation to idle time. Instead of real-time semantic search, Dream Agent pre-digests and cross-links memories during scheduled "sleep," making session-start retrieval fast and token-efficient.

---

## Architecture

```
                          ┌─────────────────────────┐
                          │     INPUT CHANNELS       │
                          │  CLI · Telegram · Cron   │
                          └───────────┬─────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │          WORKING MEMORY              │
                    │  (in-session context window)         │
                    │  • Current conversation              │
                    │  • Loaded memory (scored, top-K)     │
                    └───────────────┬─────────────────────┘
                                    │ session ends
                                    ▼
          ┌──────────────────────────────────────────────────┐
          │              SHORT-TERM MEMORY                    │
          │  short-term-memory/*.md                           │
          │  • Active tasks, deadlines, raw observations      │
          │  • Lifespan: < 3 months                           │
          └───────────────┬──────────────────────────────────┘
                          │
                    ┌─────┴──────┐
                    │  DREAMING  │  ◀── scheduled (daily)
                    │  PIPELINE  │      or manual trigger
                    └─────┬──────┘
                          │
          ┌───────────────┼───────────────────┐
          ▼               ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  LONG-TERM   │  │   ARCHIVE    │  │   FORGET     │
│   MEMORY     │  │  archive/    │  │  (deleted)   │
│ Consolidated │  │ Stale items  │  │ Irrelevant   │
│ patterns     │  │ score < 0.1  │  │ score < 0.05 │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Dreaming Pipeline (5 phases)

1. **Orient** — Read all memory files and indexes
2. **Gather Signal** — Classify each file (completed, approaching deadline, lasting insight, overlap, stale)
3. **Consolidate** — Execute 7 operations: Extract, Merge, Update, Resolve, Promote, Archive, Forget
4. **Score & Reindex** — Recalculate importance scores, rebuild indexes, update cross-links
5. **Log** — Write dream log with all changes

### Scoring Formula

```
score = (base_weight × recency_factor × reference_boost) / normalization

base_weight     = category weight (immigration: 1.0, work: 0.9, ..., personal: 0.6)
recency_factor  = e^(-days_since_update / half_life)
reference_boost = 1.0 + (0.1 × incoming_link_count)
```

Inspired by [Generative Agents](https://arxiv.org/abs/2304.03442) (Stanford, UIST 2023).

---

## Project Structure

```
dream-agent/
├── AGENT.md                     # Agent behavior rules & system prompt
├── FEEDBACK.md                  # User preferences (highest-priority input)
├── MEMORY-ARCHITECTURE.md       # Full memory system design document
│
├── short-term-memory/           # Active tasks (< 3 months)
│   ├── _index.md                # Scored routing table
│   └── {task-name}.md
│
├── long-term-memory/            # Consolidated patterns & context
│   ├── _index.md                # Scored routing table
│   └── {topic}.md
│
├── archive/                     # Completed/stale items
├── logs/                        # Dream execution logs
│
├── scripts/
│   ├── dream.md                 # Dreaming prompt (the consolidation logic)
│   └── run-dream.sh             # Shell wrapper for headless execution
│
├── bot/                         # Telegram bot (mobile interface)
│   ├── telegram_bot.py          # Bot handlers
│   ├── agent_core.py            # Claude API integration
│   ├── memory.py                # Memory file read/write
│   └── config.py                # Configuration
│
├── integrations/                # External data source connections
│   ├── gmail/                   # Email (MCP server)
│   ├── gcal/                    # Google Calendar (planned)
│   ├── finance/                 # Finance tracking (planned)
│   └── health/                  # Health data (planned)
│
├── workflows/                   # Multi-source composite workflows
├── docs/                        # Technical documentation
└── examples/                    # Example memory files
```

---

## Quick Start

### Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed
- macOS or Linux (for scheduled dreaming via launchd/cron)

### 1. Clone & Configure

```bash
git clone https://github.com/YOUR_USERNAME/dream-agent.git
cd dream-agent

# Edit AGENT.md to customize agent behavior
# Edit FEEDBACK.md to set your preferences
```

### 2. Set Up Global Access (Claude Code)

Add to `~/.claude/CLAUDE.md` so the agent is available in every Claude Code session:

```markdown
# Personal Agent

On session start:
1. Read `<path-to>/dream-agent/AGENT.md` for agent behavior rules
2. Read `<path-to>/dream-agent/FEEDBACK.md` for user preferences
3. Read `<path-to>/dream-agent/short-term-memory/_index.md` for active tasks
4. Read `<path-to>/dream-agent/long-term-memory/_index.md` for background context
```

### 3. Create Your First Memory

```bash
# Create a short-term task
cat > short-term-memory/my-first-task.md << 'EOF'
---
title: My First Task
status: pending
priority: medium
deadline: 2026-05-01
category: personal
created: 2026-04-22
updated: 2026-04-22
---

## Summary
This is my first task in Dream Agent.

## Next Actions
- [ ] Try running the dream process
EOF
```

### 4. Run Your First Dream

```bash
# Manual dream trigger
./scripts/run-dream.sh

# Or dry run to see what would execute
./scripts/run-dream.sh --dry
```

### 5. Schedule Auto Dreaming (macOS)

```bash
# Create a launchd plist for daily dreaming
cat > ~/Library/LaunchAgents/com.dream-agent.dream.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dream-agent.dream</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(pwd)/scripts/run-dream.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>20</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
    <key>StandardOutPath</key>
    <string>$(pwd)/logs/launchd-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$(pwd)/logs/launchd-stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>
</dict>
</plist>
EOF

# Load it
launchctl load ~/Library/LaunchAgents/com.dream-agent.dream.plist
```

For Linux, use cron:
```bash
# Run daily at 8 PM
0 20 * * * cd /path/to/dream-agent && ./scripts/run-dream.sh >> logs/cron.log 2>&1
```

### 6. (Optional) Set Up Telegram Bot

See [bot/README.md](bot/README.md) for mobile access setup.

---

## How It Works

### Memory Lifecycle

```
              create
                │
                ▼
┌──────────┐  update  ┌──────────┐
│  ACTIVE  │ ───────▶ │  ACTIVE  │ (score refreshed)
│ (short)  │          │ (short)  │
└────┬─────┘          └────┬─────┘
     │ done + 30d          │ insight detected
     ▼                     ▼
┌──────────┐         ┌──────────┐
│ ARCHIVED │         │ PROMOTED │ → long-term-memory/
│ archive/ │         │ (long)   │
└────┬─────┘         └──────────┘
     │ score < 0.05, age > 180d
     ▼
┌──────────┐
│ FORGOTTEN│ (deleted)
└──────────┘
```

### Forgetting Curve

```
Score
1.0  ┤ ████
     │  ████
0.5  ┤    ████
     │      ████
0.1  ┤        ████████████ ─── archive threshold
     │                    ████
0.0  ┤───────────────────────── forget threshold
     └──┬──┬──┬──┬──┬──┬──→ Days
        7  14 30 60 90 180
```

### Cross-Linking (Zettelkasten Graph)

Memories are not isolated files — they form a connected graph:

```
  personal-context.md ◄────► work-history.md
         │                        │
         ▼                        ▼
  health-patterns.md       project-deadlines.md
```

Each file has a `links:` field in frontmatter. During dreaming, the agent discovers and updates connections. Linked memories get a retrieval boost.

---

## Academic References

This project draws from recent research in LLM agent memory systems:

| Paper | Key Contribution | Venue |
|-------|------------------|-------|
| [Sleep-time Compute](https://arxiv.org/abs/2504.13171) (Lin et al., 2025) | Pre-process context during idle time; 5x compute reduction | arXiv |
| [Generative Agents](https://arxiv.org/abs/2304.03442) (Park et al., 2023) | Reflection-based memory with importance scoring | UIST 2023 |
| [MemoryOS](https://arxiv.org/abs/2506.06326) (Kang et al., 2025) | 3-tier hierarchical memory with OS-inspired management | EMNLP 2025 |
| [A-MEM](https://arxiv.org/abs/2502.12110) (Xu et al., 2025) | Zettelkasten-inspired self-organizing memory | NeurIPS 2025 |
| [Mem0](https://arxiv.org/abs/2504.19413) (Chhikara et al., 2025) | Production consolidation pipeline; 90%+ token savings | arXiv |

For a full reference list with neuroscience foundations, see [docs/auto-dream-architecture.md](docs/auto-dream-architecture.md).

---

## Comparison with Related Projects

| Project | Type | Dreaming | Tiered Memory | Forgetting | File-based | Multi-channel |
|---------|------|----------|---------------|------------|------------|---------------|
| **Dream Agent** | Personal agent | Scheduled offline | 3-tier + scoring | Decay curve | Markdown + YAML | CLI + Telegram + cron |
| [Mem0](https://github.com/mem0ai/mem0) (53k+) | Memory library | No | No | No | Vector DB | No |
| [Letta/MemGPT](https://github.com/letta-ai/letta) (22k+) | Agent platform | In-conversation | 3-tier | No | PostgreSQL | No |
| [Khoj](https://github.com/khoj-ai/khoj) (34k+) | AI second brain | No | No | No | RAG-based | Yes |
| [Hippo-Memory](https://github.com/kitfunso/hippo-memory) | Memory library | Yes | Yes | Yes | In-memory | No |
| [PsychMem](https://github.com/muratg98/psychmem) | Memory library | On-retrieval | STM/LTM | Yes | In-memory | No |

---

## Contributing

Contributions are welcome! Areas where help is especially appreciated:

- **Integrations** — Google Calendar, Finance (Plaid), Apple Health
- **Dream quality metrics** — measuring consolidation effectiveness
- **Semantic scoring** — optional local embedding for better retrieval
- **Platform support** — systemd service file for Linux, Windows Task Scheduler

---

## License

MIT License. See [LICENSE](LICENSE).
