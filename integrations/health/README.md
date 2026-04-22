---
integration: health
status: planned
method: Health Auto Export app + local file
priority: P3
---

# Health Data Integration

## Goal
Analyze Apple Health data (sleep, exercise, heart rate, etc.) for health trends and recommendations.

## Setup Steps
Apple Health has no public API. Requires a third-party bridge:

1. Install **Health Auto Export** app (iOS App Store, ~$5)
2. Configure auto-export:
   - Format: JSON or CSV
   - Frequency: daily
   - Destination: iCloud Drive folder or REST API
3. Mac syncs via iCloud Drive; agent reads from `data/` folder

## Alternative: Manual Export
- Apple Health app → Export All Health Data (Settings → Export)
- Produces a large XML file
- Suitable for one-time analysis, not continuous tracking

## Planned Data Types
| Data Type | Frequency | Use Case |
|-----------|-----------|----------|
| Sleep | Daily | Sleep quality trends |
| Steps | Daily | Activity tracking |
| Heart Rate | Continuous | Stress / recovery indicator |
| Workouts | Per workout | Exercise frequency & intensity |
| Weight | Weekly | Long-term trend |

## Planned Operations
- Sleep analysis for last N days
- Exercise frequency and trends
- Health metric anomaly alerts
- Correlate Calendar events with health patterns
