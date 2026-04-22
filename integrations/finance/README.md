---
integration: finance
status: planned
method: Plaid API + MCP server
priority: P1
---

# Finance Integration

## Goal
Connect bank/credit card accounts to track spending, generate reports, and detect anomalies.

## Option A: Plaid API (Recommended)
1. Register Plaid developer account (https://plaid.com)
2. Free tier: 100 connections, sufficient for personal use
3. Use Plaid Link to connect bank accounts
4. Build MCP server wrapping Plaid Transactions API

## Option B: CSV Import
- Export CSV from Chase / Amex / etc.
- Place in `data/` folder periodically
- Agent reads and analyzes locally

## Planned Operations
- Fetch transactions for a given period
- Categorize spending
- Monthly / weekly spending summary
- Anomaly detection (unusual charges)

## Data Schema
```json
{
  "date": "2026-04-20",
  "merchant": "Trader Joe's",
  "amount": 45.67,
  "category": "groceries",
  "account": "Chase Freedom"
}
```

## Security Notes
- Plaid credentials must NOT be committed to git
- Transaction data stored locally only
- `.gitignore` excludes `data/` and `credentials/`
