# 08: Save and list fragments

Type: task
Blocked by: 01, 03, 06

## Source requirements

- [PRD](../spec.md)
- [Audio fragments module](../SPEC-audio-fragments.md)

## Description

Make audio capture create independently saved fragments that users can browse
without immediately running the full analysis/research/draft pipeline. Add the
fragment library to the workspace and connect it to the owned fragment APIs.

## Acceptance criteria

- Upload saves a fragment and returns its persisted identity/status without
  invoking transcription, analysis, research, or draft composition.
- The workspace lists the user's fragments and their processing status.
- The fragment list exposes deletion using the owner-authorized operation from
  ticket 06.

## Verification

- Backend tests prove upload persists and invokes no external processing stage.
- Manually record/upload, reload the workspace, list the fragment, and delete
  it as its owner.
- Run `python -m pytest` from `backend/` and `npm run build` from `frontend/`.

## Dependencies

Blocked by: 01, 03, 06

## Files likely touched

- `backend/app/api/blogs.py`
- `backend/tests/test_fragments.py`
- `frontend/components/AppShell.tsx`
- `frontend/components/VoiceCapturePanel.tsx`
- `frontend/lib/apiSlice.ts`

## Estimated scope

Medium (5 files).

## Comments
