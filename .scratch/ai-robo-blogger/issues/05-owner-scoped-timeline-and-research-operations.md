# 05: Owner-scoped timeline and research operations

Type: task
Blocked by: 01, 02

## Source requirements

- [PRD](../spec.md)
- [Identity and privacy module](../SPEC-identity-privacy.md)

## Description

Require ownership for timeline, research, and event-stream operations so
authenticated users cannot inspect another account's processing history,
questions, sources, or events.

## Acceptance criteria

- Timeline and research read/run routes require authentication and verify blog
  ownership.
- The SSE event route subscribes only after validating access to the requested
  blog.
- Existing owned-blog behavior remains available.

## Verification

- Add two-user tests for timeline, research list/run, and event subscription.
- Run `python -m pytest` from `backend/`.

## Dependencies

Blocked by: 01, 02

## Files likely touched

- `backend/app/api/blogs.py`
- `backend/app/api/events.py`
- `backend/app/repositories/blog_repository.py`
- `backend/tests/test_blog_access.py`

## Estimated scope

Medium (4 files).

## Comments
