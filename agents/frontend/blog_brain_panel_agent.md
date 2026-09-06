# Frontend Agent: Blog Brain Panel Agent

## Purpose
Render and maintain the live, explainable view of current blog understanding as backend state evolves.

## Stack
- Next.js + TypeScript
- React Query
- SSE or websocket client

## Responsibilities
- Display thesis, arguments, claims, sentiment, intent, and open research questions.
- Reconcile incoming state deltas without losing local UI interactions.
- Surface confidence and contradiction markers.

## Inputs
- `GET /blogs/{blog_id}/state`
- Live events stream (`fragment_processed`, `research_completed`, `draft_updated`)

## Outputs
- Updated panel cards and status badges.
- User-triggered actions (`regenerate section`, `request research refresh`).

## UX Rules
- Show provenance labels for each card:
  - `user_said`
  - `ai_inference`
  - `research_fact`
- Show stale indicators when data is older than freshness threshold.

## Failure Handling
- Event stream disconnect -> fallback polling every 10-15 seconds.
- Partial state payload -> keep previous stable state and mark section as refreshing.

## Notes
- Do not expose raw unfiltered model output directly.
- Render contradiction hints prominently to build trust.
