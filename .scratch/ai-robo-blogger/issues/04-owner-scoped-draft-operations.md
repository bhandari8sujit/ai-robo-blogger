# 04: Owner-scoped draft operations

Type: task
Blocked by: 01, 02

## Source requirements

- [PRD](../spec.md)
- [Identity and privacy module](../SPEC-identity-privacy.md)
- [Draft review and export module](../SPEC-draft-review-export.md)

## Description

Enforce blog ownership for draft generation and owner checks for draft reads,
revision, validation, and source/provenance lookups.

## Acceptance criteria

- Every draft route resolves the draft to its parent blog and verifies the
  current user owns that blog.
- Draft source and sentence explanation endpoints disclose no data for a
  non-owned draft.
- Missing and non-owned identifiers have consistent, non-disclosing behavior.

## Verification

- Add two-user API tests for draft generation, revision, validation, sources,
  and sentence explanation.
- Run `python -m pytest` from `backend/`.

## Dependencies

Blocked by: 01, 02

## Files likely touched

- `backend/app/api/drafts.py`
- `backend/app/api/generation.py`
- `backend/app/repositories/blog_repository.py`
- `backend/tests/test_drafts.py`

## Estimated scope

Medium (4 files).

## Comments
