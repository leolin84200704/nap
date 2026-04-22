---
title: Memory Architecture — Auto Dreaming & Intelligent Consolidation
version: 1.0
updated: 2026-04-21
references: See Academic References section
---

# Memory Architecture: Auto Dreaming & Intelligent Consolidation

This document defines how the personal agent manages, consolidates, and optimizes its memory system. Inspired by human sleep/dreaming processes and recent AI agent memory research.

---

## 1. Core Concept: Why "Dreaming"?

In neuroscience, sleep serves to:
- **Consolidate** episodic memories into semantic knowledge
- **Prune** irrelevant details while retaining key patterns
- **Reorganize** connections between related memories
- **Compress** information for efficient future retrieval

AI agent "dreaming" applies the same principles: during idle time (between sessions), the agent processes raw memories into compressed, structured, interlinked knowledge — reducing token cost while improving retrieval precision.

---

## 2. Memory Tier Design

Inspired by **MemoryOS** (EMNLP 2025) and **Active Dreaming Memory** research.

```
┌─────────────────────────────────────────────────────┐
│                   WORKING MEMORY                     │
│  (in-session context window — ephemeral)             │
│  - Current conversation                              │
│  - Active tool results                               │
│  - Loaded memory snippets from retrieval             │
└──────────────────────┬──────────────────────────────┘
                       │ session ends
                       ▼
┌─────────────────────────────────────────────────────┐
│               SHORT-TERM MEMORY                      │
│  short-term-memory/*.md                              │
│  - Active tasks, events, deadlines                   │
│  - Raw observations from integrations                │
│  - Lifespan: < 3 months                              │
│  - Granular, specific, action-oriented               │
└──────────────────────┬──────────────────────────────┘
                       │ dreaming (consolidation)
                       ▼
┌─────────────────────────────────────────────────────┐
│                LONG-TERM MEMORY                      │
│  long-term-memory/*.md                               │
│  - Consolidated patterns, preferences, life context  │
│  - Verified insights extracted from short-term       │
│  - Lifespan: persistent (with decay scoring)         │
│  - Abstract, semantic, context-providing             │
└─────────────────────────────────────────────────────┘
```

### Key difference from current setup

| Aspect | Before (v2.0) | After (v2.1+) |
|--------|---------------|----------------|
| Migration | Manual — user/agent decides | **Automatic** — dreaming process handles it |
| Pruning | None — files accumulate | **Scored decay** — stale items archived/removed |
| Indexing | Flat `_index.md` table | **Scored index** with importance + recency weights |
| Linking | None | **Cross-references** between related memories |
| Token budget | No limit | **Budget cap** on loaded memory per session |

---

## 3. Auto Dreaming Process

A 4-phase consolidation cycle that runs between sessions.

### Phase 1: Orient
- Read `short-term-memory/_index.md` and `long-term-memory/_index.md`
- Build a map of all current memory files, their status, and last-updated dates

### Phase 2: Gather Signal
- Scan recent interactions (conversation history, task updates, integration events)
- Extract new facts, preferences, corrections, and completed events
- Tag each signal: `fact`, `preference`, `correction`, `event`, `insight`

### Phase 3: Consolidate
Core operations (inspired by **Mem0** and **A-MEM** techniques):

| Operation | Description | Example |
|-----------|-------------|---------|
| **Extract** | Pull lasting knowledge from completed tasks | Task "Big Sur trip" done → extract "User enjoys Big Sur road trips" to long-term |
| **Merge** | Combine overlapping memories into one | Two separate finance notes → single "spending patterns" file |
| **Update** | Revise existing memory with new info | Immigration timeline updated with new dates |
| **Resolve** | When new info contradicts old, pick the newer verified version | Old: "prefers Amex" → New: "switched to Chase" |
| **Promote** | Move recurring short-term patterns to long-term | Same type of task appears 3+ times → create long-term pattern note |
| **Archive** | Move completed/stale short-term items out of active index | Task marked `done` > 30 days ago → move to `archive/` |
| **Forget** | Remove truly irrelevant or superseded memories | Outdated one-time event details |

### Phase 4: Prune & Reindex
- Recalculate importance scores for all memory files (see scoring below)
- Rebuild `_index.md` files with scores
- Ensure total loaded memory at startup stays within token budget
- Generate a brief `logs/dream-YYYY-MM-DD.md` summary of changes

### Dreaming Trigger Options

| Method | How | Best for |
|--------|-----|----------|
| **Manual** | User runs a dream command | On-demand cleanup |
| **Scheduled** | Cron / `/schedule` runs daily at off-hours | Consistent maintenance |
| **Threshold** | Trigger when short-term-memory file count > N | Reactive cleanup |
| **Post-session** | Run after every significant conversation | Real-time consolidation |

**Recommended**: scheduled daily (e.g., 3 AM) + threshold trigger (> 15 active short-term files).

---

## 4. Memory Scoring & Retrieval

Inspired by **Generative Agents** (Stanford, 2023) retrieval scoring and **Sleep-time Compute** (UC Berkeley, 2025).

### Importance Score Formula

```
score = base_weight × recency_factor × reference_boost / normalization

Where:
  base_weight    = category weight (immigration: 1.0, work: 0.9, finance: 0.8, health: 0.7, personal: 0.6)
  recency_factor = exp(-days_since_update / half_life)
                   half_life = 30 days for short-term, 180 days for long-term
  reference_boost = 1.0 + (0.1 × times_referenced_in_other_memories)
  normalization  = 8.0
```

### Retrieval Strategy

When loading memory for a session, don't load everything. Use scored retrieval:

1. **Always load**: `_index.md` files (lightweight pointers)
2. **Score all memories** against the current query/context
3. **Load top-K** memories that score above threshold
4. **Token budget**: max ~2000 tokens of memory per session start
5. **On-demand**: if conversation requires more context, retrieve additional files

### Forgetting Curve

```
                Score
  1.0  ┤ ████
       │  ████
  0.5  ┤    ████
       │      ████
  0.1  ┤        ████████████
       │                    ████──── archive threshold
  0.0  ┤─────────────────────────── forget threshold
       └──┬──┬──┬──┬──┬──┬──┬──→ Days
          7  14 30 60 90 120 180
```

- Score < 0.1 for > 90 days → **archive** (move to `archive/`, remove from index)
- Score < 0.05 for > 180 days → **forget** (delete, unless category = immigration/legal)
- Immigration/legal items: **never auto-forget**, only manual removal

---

## 5. File Structure Optimization for Token Efficiency

### Memory File Format (Optimized)

Each `.md` file uses structured frontmatter for machine parsing, minimal prose for token savings:

```markdown
---
id: short-xxx
title: Brief Title
status: pending | done | archived
priority: critical | high | medium | low
category: immigration | work | finance | health | personal
deadline: YYYY-MM-DD | flexible
created: YYYY-MM-DD
updated: YYYY-MM-DD
score: 0.72
links: [long-immigration-timeline, short-sevis-transfer]
tags: [visa, school, deadline]
---

## Summary
Single sentence. Agent reads this FIRST to decide whether to load full file.

## Details
Only include what cannot be derived from other sources.
No redundant context. No verbose explanations.

## Next Actions
- [ ] Concrete action item

## History
- YYYY-MM-DD: Update note (keep to one line)
```

### Index File Format (Optimized)

`_index.md` serves as a **scored routing table**, not a full summary:

```markdown
---
updated: YYYY-MM-DD
token_budget: 2000
---

| File | Score | Category | Deadline | Status | One-line |
|------|-------|----------|----------|--------|----------|
| sevis-transfer.md | 0.92 | immigration | 2026-07-06 | pending | SEVIS transfer & CPT |
| upcoming-visits.md | 0.71 | personal | 2026-05-10 | pending | Friend visits: SF, Big Sur |
```

Sorted by score descending. Agent loads files top-down until token budget is reached.

### Token Saving Strategies

| Strategy | Savings | How |
|----------|---------|-----|
| **Scored retrieval** | ~70% | Only load relevant memories, not all |
| **Summary-first loading** | ~50% | Read frontmatter + Summary; load Details only if needed |
| **Structured frontmatter** | ~30% | Machine-parseable metadata vs. prose descriptions |
| **Cross-linking** | ~40% | Reference related files by ID instead of duplicating content |
| **Periodic compression** | ~60% | Dreaming merges overlapping files, removes redundancy |

---

## 6. Cross-Linking (Zettelkasten-Inspired)

Inspired by **A-MEM** (NeurIPS 2025) — memories are not isolated files but a connected graph.

### How it works
- Each memory has a `links:` field in frontmatter listing related memory IDs
- During dreaming, the agent scans for thematic connections and updates links
- When retrieving one memory, linked memories get a retrieval boost

### Example
```
immigration-timeline.md
  ├── links to: sevis-transfer.md (active task)
  ├── links to: personal-info.md (employer context)
  └── links to: humphreys-mba.md (future plan)

sevis-transfer.md
  ├── links to: immigration-timeline.md (background)
  └── links to: vibrant-opt-form.md (related paperwork)
```

### Benefits
- Query about SEVIS → automatically pulls immigration timeline as context
- No need to explicitly load all related files — links guide retrieval
- Reduces duplicate information across files

---

## 7. Implementation Plan for Claude Code

### Step 1: Restructure Current Files (Immediate)
- Add `score`, `links`, `tags` fields to all existing memory files
- Convert `_index.md` to scored routing table format
- Add `archive/` directory for completed items

### Step 2: Create Dream Script (Short-term)
A prompt-based dreaming process that can be triggered via `/loop` or `/schedule`:

```
Dream prompt (to be run by Claude Code):

"Read all files in short-term-memory/ and long-term-memory/.
For each short-term file:
  1. If status=done and updated > 30 days ago → archive
  2. If contains lasting insight → extract to long-term-memory
  3. If overlaps with another file → merge
  4. Recalculate score using the scoring formula
Rebuild _index.md files sorted by score.
Log all changes to logs/dream-YYYY-MM-DD.md."
```

### Step 3: Scheduled Dreaming (Medium-term)
- Set up `/schedule` to run dream process daily at 3 AM
- Add threshold trigger: auto-dream when short-term files > 15

### Step 4: Integration-Aware Dreaming (Long-term)
- After Gmail/Calendar/Finance integrations are live:
  - Dream process also scans integration data for memory-worthy signals
  - e.g., recurring calendar events → promote to long-term patterns
  - e.g., spending anomalies → create short-term alert tasks

---

## 8. Practical Example: A Day in the Life

```
8:00 AM — User asks "what's on today?"
  │
  Agent loads _index.md (scored) → top 5 memories by relevance
  Agent queries Calendar, Gmail
  Agent responds with morning briefing
  │
12:00 PM — User says "cancel the Saturday SF trip"
  │
  Agent updates upcoming-visits.md (remove SF entry)
  Agent notes: user preference change (feedback signal)
  │
6:00 PM — Session ends
  │
3:00 AM — AUTO DREAM runs
  │
  Phase 1: Orient — reads all memory files
  Phase 2: Gather — session had 1 task update, 1 feedback signal
  Phase 3: Consolidate —
    • upcoming-visits.md updated (SF removed, only Big Sur remains)
    • FEEDBACK.md: no new behavioral rules detected
    • No promotion/archival needed today
  Phase 4: Prune —
    • Recalculate scores (upcoming-visits score drops slightly, deadline still active)
    • Rebuild _index.md
    • Log: "dream-2026-04-21.md: updated 1 file, no promotions, no archival"
```

---

## 9. Academic References

| Paper | Authors | Year | Key Contribution | Venue |
|-------|---------|------|-------------------|-------|
| Sleep-time Compute | Lin, Snell, Wang et al. | 2025 | Pre-process context during idle time; 5x compute reduction | arXiv:2504.13171 |
| Generative Agents | Park, O'Brien, Cai et al. | 2023 | Reflection-based memory consolidation with importance scoring | UIST 2023 |
| MemoryOS | Kang et al. | 2025 | 3-tier hierarchical memory with OS-inspired management | EMNLP 2025 Oral |
| A-MEM | Xu, Liang et al. | 2025 | Zettelkasten-inspired self-organizing memory with cross-linking | NeurIPS 2025 |
| Mem0 | Chhikara et al. | 2025 | Production-ready consolidation; 90%+ token savings | arXiv:2504.19413 |
| Active Dreaming Memory | — | 2025 | Counterfactual verification before long-term promotion | ResearchGate |
| MAGMA | — | 2026 | Multi-graph memory with adaptive traversal policy | arXiv:2604.12285 |
| E-mem | — | 2026 | Hierarchical architecture; >70% token reduction | arXiv:2601.21714 |
| Memory Survey | — | 2025 | Taxonomy: factual/experiential/working memory lifecycle | arXiv:2512.13564 |

---

## 10. Summary: What Changes

| Before | After |
|--------|-------|
| Flat file accumulation | Scored, linked, tiered memory graph |
| Manual cleanup | Auto dreaming consolidation cycle |
| Load all memory | Token-budgeted scored retrieval |
| Isolated files | Zettelkasten cross-linked network |
| No forgetting | Decay curve with archive & forget thresholds |
| Same context every session | Pre-digested, session-relevant context (sleep-time compute) |
