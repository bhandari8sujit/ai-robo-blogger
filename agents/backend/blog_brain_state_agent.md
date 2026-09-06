# Backend Agent: Blog Brain State Agent

## Purpose
Maintain a compact, continuously updated representation of what the user is trying to say.

## Harness
- LangChain state-merging chain
- PostgreSQL persistence + versioned snapshots

## Responsibilities
- Merge latest fragment analysis into current blog brain.
- Update thesis, stance, arguments, and open questions.
- Track provenance per state element.

## Inputs
- Current blog brain snapshot
- Latest fragment analysis
- User guardrails

## Outputs
- New blog brain snapshot (`version + 1`)
- State diff payload for frontend
- Updated research candidate list

## Merge Rules
- Prefer explicit user statements over inferred interpretations.
- Keep contradictory user statements; do not overwrite silently.
- Annotate each element with `origin_type` and confidence.

## Failure Handling
- Conflict in merge -> preserve both alternatives and flag for QA.
- Snapshot write failure -> retry transactionally.
