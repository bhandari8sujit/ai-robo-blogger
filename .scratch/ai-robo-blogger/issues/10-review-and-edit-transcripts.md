# 10: Review and edit transcripts

Type: task
Blocked by: 09

## Source requirements

- [PRD](../spec.md)
- [Transcripts module](../SPEC-transcripts.md)

## Description

Let owners correct a fragment transcript before composition. Persist transcript
edits independently of the original audio and expose the edit control in the
fragment library.

## Acceptance criteria

- An owner can read and save an edited transcript for their fragment.
- Non-owners cannot read or change the transcript.
- The edited text survives reload and becomes the source text for composition;
  editing does not modify the source audio.

## Verification

- Backend tests cover valid edit, empty/invalid input, and non-owner access.
- Manually edit a transcript, reload, and verify the updated text is shown.
- Run `python -m pytest` from `backend/` and `npm run build` from `frontend/`.

## Dependencies

Blocked by: 09

## Files likely touched

- `backend/app/api/fragments.py`
- `backend/app/repositories/blog_repository.py`
- `backend/tests/test_transcripts.py`
- `frontend/components/FragmentLibrary.tsx`
- `frontend/lib/apiSlice.ts`

## Estimated scope

Medium (5 files).

## Comments
