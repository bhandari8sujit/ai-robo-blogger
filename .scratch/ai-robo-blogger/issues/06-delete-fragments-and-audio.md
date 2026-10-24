# 06: Delete fragments and audio

Type: task
Blocked by: 03

## Source requirements

- [PRD](../spec.md)
- [Identity and privacy module](../SPEC-identity-privacy.md)
- [Audio fragments module](../SPEC-audio-fragments.md)

## Description

Add an owner-authorized backend operation to delete a fragment and its
app-controlled audio and fragment-derived records. Report cleanup failures
explicitly rather than returning success while audio remains.

## Acceptance criteria

- Only the fragment's owning user can delete it.
- Successful deletion removes the fragment, its transcript/analysis records,
  and stored audio; unrelated blog fragments remain intact.
- Partial storage/database cleanup is surfaced as an error and is diagnosable.

## Verification

- Add API/service tests for successful deletion, non-owner rejection,
  missing audio, and storage cleanup failure.
- Run `python -m pytest` from `backend/`.

## Dependencies

Blocked by: 03

## Files likely touched

- `backend/app/api/fragments.py`
- `backend/app/repositories/blog_repository.py`
- `backend/app/services/storage_service.py`
- `backend/tests/test_fragment_deletion.py`

## Estimated scope

Medium (4 files).

## Comments
