# Frontend Agent: Draft Workspace Agent

## Purpose
Manage the writing surface for draft preview, revision actions, and sentence-level explainability.

## Stack
- Next.js + TypeScript
- Rich text viewer/editor component
- React Query mutations

## Responsibilities
- Display latest draft with citation references.
- Trigger targeted revisions from user feedback.
- Open "Why is this here?" panel for sentence provenance.

## Inputs
- `POST /blogs/{blog_id}/draft/generate`
- `POST /drafts/{draft_id}/revise`
- `GET /drafts/{draft_id}/sources`
- `GET /drafts/{draft_id}/sentences/{sentence_id}/why`

## Outputs
- Draft version updates (`v1`, `v2`, ...).
- Inline source markers and confidence indicators.
- Revision request objects tied to paragraph/sentence IDs.

## UI Interaction Model
- Action buttons: `Edit`, `Regenerate`, `Why`, `Publish`.
- Diff mode: compare current vs previous draft sections.
- Citation drawer: map claims to supporting sources.

## Failure Handling
- Revision failure -> preserve current draft and show retry option.
- Missing provenance -> flag as `insufficient_traceability` for backend QA.

## Notes
- Never auto-apply revisions silently; user should confirm substantial rewrites.
