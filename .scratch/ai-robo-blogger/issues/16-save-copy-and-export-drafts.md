# 16: Save, copy, and export drafts

Type: task
Blocked by: 12, 14, 15

## Source requirements

- [PRD](../spec.md)
- [Draft review and export module](../SPEC-draft-review-export.md)

## Description

Ensure reviewed drafts can be reopened and provide copy/export actions for the
current saved content. Include deletion controls for the owner's draft/workspace
where the existing workspace UI supports them.

## Acceptance criteria

- The current reviewed text and citation choices persist and survive reload.
- Copy/export uses the latest saved version, not stale generation output.
- Only the owner can retrieve, export, or delete the draft; direct publishing is
  not added.

## Verification

- Manually save, reopen, edit, copy, export, and delete a draft; compare exported
  content with the saved reviewed draft.
- Run `python -m pytest` from `backend/` and `npm run build` from `frontend/`.

## Dependencies

Blocked by: 12, 14, 15

## Files likely touched

- `backend/app/api/drafts.py`
- `backend/app/repositories/blog_repository.py`
- `backend/tests/test_drafts.py`
- `frontend/components/DraftWorkspace.tsx`
- `frontend/lib/apiSlice.ts`

## Estimated scope

Medium (5 files).

## Decision gate

Confirm the required export format(s) before implementing the export contract.

## Comments
