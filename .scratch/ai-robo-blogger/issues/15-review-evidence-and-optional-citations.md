# 15: Review evidence and optional citations

Type: task
Blocked by: 13, 14

## Source requirements

- [PRD](../spec.md)
- [Claim verification module](../SPEC-claim-verification.md)
- [Draft review and export module](../SPEC-draft-review-export.md)

## Description

Present the draft with claim-level fact-check status, source evidence, and
correction decisions. Let the author choose whether source citations appear in
the draft.

## Acceptance criteria

- Each claim review displays its evidence/source links and supported,
  contradicted, or insufficient status.
- The author can accept/reject each suggestion and include/omit citations
  without affecting unrelated draft text.
- Empty or failed research is presented as unverified, not as support.

## Verification

- Manually review supported, contradicted, and insufficient-evidence examples;
  verify correction decisions and citation selection.
- Run `npm run typecheck` and `npm run build` from `frontend/`.

## Dependencies

Blocked by: 13, 14

## Files likely touched

- `frontend/components/ResearchPanel.tsx`
- `frontend/components/DraftWorkspace.tsx`
- `frontend/lib/apiSlice.ts`

## Estimated scope

Small (3 files).

## Comments
