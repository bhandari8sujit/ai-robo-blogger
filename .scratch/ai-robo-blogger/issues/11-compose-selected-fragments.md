# 11: Compose selected fragments

Type: task
Blocked by: 08, 10

## Source requirements

- [PRD](../spec.md)
- [Composition module](../SPEC-composition.md)

## Description

Add a backend composition operation that accepts an ordered set of owned,
transcribed fragment IDs and creates a draft from only their saved, user-edited
transcripts.

## Acceptance criteria

- The operation rejects empty, duplicate, non-owned, or non-transcribed
  selections with explicit validation errors.
- The composition input includes exactly the selected transcript text in the
  requested order and minimum necessary composition context.
- Provider errors do not create a success-shaped draft; successful output is
  stored as an owner-scoped draft.

## Verification

- Service/API tests assert selected ID ownership, order, exact provider input,
  and failure behavior using a fake composition provider.
- Run `python -m pytest` from `backend/`.

## Dependencies

Blocked by: 08, 10

## Files likely touched

- `backend/app/api/generation.py`
- `backend/app/schemas/api.py`
- `backend/app/services/orchestration_service.py`
- `backend/tests/test_composition.py`

## Estimated scope

Medium (4 files).

## Comments
