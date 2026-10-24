# 02: Owner-scoped blog operations

Type: task
Blocked by: 01

## Source requirements

- [PRD](../spec.md)
- [Identity and privacy module](../SPEC-identity-privacy.md)

## Description

Enforce server-side ownership for blog detail and state reads. An authenticated
user must not access another user's blog by guessing or substituting its ID.

## Acceptance criteria

- Blog detail and state operations require authentication and verify the
  authenticated user owns the blog.
- Missing and non-owned blog IDs do not disclose another user's content.
- Existing create/list behavior remains scoped to the authenticated owner.

## Verification

- Add two-user API tests for owned, non-owned, missing, and unauthenticated
  blog detail/state requests.
- Run `python -m pytest` from `backend/`.

## Dependencies

Blocked by: 01

## Files likely touched

- `backend/app/api/blogs.py`
- `backend/app/repositories/blog_repository.py`
- `backend/tests/test_blogs.py`

## Estimated scope

Small (3 files).

## Comments
