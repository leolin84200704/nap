---
integration: photos
status: planned
method: Google Photos API / iOS Shortcuts
priority: P2
---

# Photos Integration

## Goal
Access and organize iPhone photos. Support search, album management, and trip memory curation.

## Option A: Google Photos API (Recommended)
- Prerequisite: iPhone photos synced to Google Photos
- Use Google Photos Library API
- OAuth scope: `https://www.googleapis.com/auth/photoslibrary.readonly`
- Supports search, list, and download

## Option B: iOS Shortcuts + Local Sync
- Create iOS Shortcut to copy new photos to a designated iCloud Drive folder
- Mac syncs via iCloud Drive; agent reads local files directly
- Simplest approach but limited functionality

## Planned Operations
- Search photos by date / location
- Create / manage albums
- Auto-organize trip photos
- Photo metadata analysis (location, timestamp)

## Use Cases
- "Where are my Big Sur photos from last time?"
- "Organize last weekend's photos"
- Auto-create album after a trip
