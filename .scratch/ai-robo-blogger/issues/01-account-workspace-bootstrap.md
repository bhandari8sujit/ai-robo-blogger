# 01: Account-owned workspace bootstrap

Type: task
Blocked by: None

## Source requirements

- [PRD](../spec.md)
- [Authentication module](../SPEC-authentication.md)
- [Identity and privacy module](../SPEC-identity-privacy.md)

## Description

Connect the existing registration/login flow to a user-owned writing workspace.
Replace the fixed `demo-blog` assumption with a list/create/select flow that
uses the authenticated user's identity. Reuse the existing email/password and
JWT implementation unless tests reveal a concrete gap.

## Acceptance criteria

- A logged-in user sees only their own blogs/workspaces and can create/select
  one.
- Registration/login/logout still work, and workspace requests use the
  authenticated account.
- The workspace model decision (one default workspace or multiple blogs per
  account) is recorded before its API/UI contract is fixed.

## Verification

- Backend API tests cover user-scoped list/create behavior with two users.
- Manually register two users and verify each sees only their own workspace.
- Run `python -m pytest` from `backend/` and `npm run typecheck` from `frontend/`.

## Dependencies

None.

## Files likely touched

- `backend/app/api/blogs.py`
- `backend/app/repositories/blog_repository.py`
- `backend/app/schemas/api.py`
- `backend/tests/test_blogs.py`
- `frontend/components/AppShell.tsx`

## Estimated scope

Medium (up to 5 files).

## Comments
