# 03: Owner-scoped fragment operations

Type: task
Blocked by: 01, 02

## Source requirements

- [PRD](../spec.md)
- [Identity and privacy module](../SPEC-identity-privacy.md)
- [Audio fragments module](../SPEC-audio-fragments.md)

## Description

Require ownership of the parent blog for fragment listing, upload, retrieval,
and reprocessing. Never treat authentication by itself as authorization to
operate on any blog's fragments.

## Acceptance criteria

- Fragment list, upload, and reprocess routes reject unauthenticated callers.
- Each operation verifies that the caller owns the parent blog before reading
  or mutating fragment data.
- Non-owned and missing parent resources return a non-disclosing not-found
  response.

## Verification

- Add two-user tests for list, upload, and reprocess attempts against another
  user's blog.
- Run `python -m pytest` from `backend/`.

## Dependencies

Blocked by: 01, 02

## Files likely touched

- `backend/app/api/blogs.py`
- `backend/app/api/fragments.py`
- `backend/app/repositories/blog_repository.py`
- `backend/tests/test_fragments.py`

## Estimated scope

Medium (4 files).

## Comments
