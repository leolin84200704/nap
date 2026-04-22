---
description: Automated multi-source workflow definitions
updated: 2026-04-21
---

# Workflows

Composite flows combining multiple integrations. Each workflow can be scheduled via `/loop` or `/schedule`.

## Defined Workflows

### 1. Morning Briefing (`morning-briefing`)
- **Trigger**: daily morning / manual ("what's on today?")
- **Steps**:
  1. Calendar → today's events
  2. Gmail → important unread emails
  3. Tasks → due today or approaching deadline
- **Dependencies**: Gmail ✅, Calendar 🔲, Tasks ✅

### 2. Weekly Finance Review (`weekly-finance`)
- **Trigger**: weekly / manual ("how much did I spend?")
- **Steps**:
  1. Finance → this week's transactions
  2. Categorize spending
  3. Compare with monthly average
- **Dependencies**: Finance 🔲

### 3. Trip Planner (`trip-planner`)
- **Trigger**: manual
- **Steps**:
  1. Calendar → confirm travel dates
  2. Gmail → search booking/flight confirmation emails
  3. Tasks → related action items
  4. Output itinerary suggestions
- **Dependencies**: Gmail ✅, Calendar 🔲

### 4. Health Check-in (`health-checkin`)
- **Trigger**: weekly / manual
- **Steps**:
  1. Health → recent data
  2. Calendar → lifestyle pattern analysis
  3. Output trend report + recommendations
- **Dependencies**: Health 🔲, Calendar 🔲

## Adding a Workflow
1. Add workflow definition to this file
2. Note dependent integrations and their status
3. Workflow becomes active once all dependencies are live
