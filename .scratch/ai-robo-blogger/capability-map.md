# Capability Map: AI Robo Blogger

| Module id | Responsibility | Depends on |
|---|---|---|
| `authentication` | User registration, login, and authenticated sessions | — |
| `identity-privacy` | User-owned data, ownership checks, privacy, and deletion | `authentication` |
| `audio-fragments` | Record, upload, store, and list audio fragments | `identity-privacy` |
| `transcripts` | Transcribe fragments and let users review and edit transcripts | `audio-fragments` |
| `composition` | Select transcripts and generate voice-preserving blog drafts | `transcripts` |
| `claim-verification` | Check draft claims using disclosed, claim-only web searches; return evidence, correction suggestions, and optional citations | `composition` |
| `draft-review-export` | Review and accept/reject corrections, manage citations, save drafts, copy/export | `composition`, `claim-verification` |

## Build order

`authentication` → `identity-privacy` → `audio-fragments` → `transcripts` →
`composition` → `claim-verification` → `draft-review-export`.

`composition` and `claim-verification` have a dependency because the claims to
verify are extracted from a composed draft. Draft review and export depend on
both so users can review the evidence and proposed corrections before saving or
exporting.

## Cross-cutting constraint

Simplify the existing AI-generated `/backend` and `/frontend` code only where
needed to deliver a capability. Do not make a standalone refactoring workstream.
