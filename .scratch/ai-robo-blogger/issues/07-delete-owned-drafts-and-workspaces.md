# 07: Delete owned drafts and workspaces

Type: task
Blocked by: 02, 04, 05, 06

## Source requirements

- [PRD](../spec.md)
- [Identity and privacy module](../SPEC-identity-privacy.md)
- [Draft review and export module](../SPEC-draft-review-export.md)

## Description

Provide owner-authorized deletion for saved drafts and a user's workspace,
including app-controlled child records and associated audio. Preserve other
users' data and report incomplete cleanup.

## Acceptance criteria

- Owners can delete a draft and delete a workspace with its owned child
  records.
- A non-owner cannot delete a draft/workspace by supplying its identifier.
- Deleting a workspace does not leave app-controlled child records or audio
  objects; partial cleanup is not reported as success.

## Verification

- Add two-user tests covering draft/workspace deletion, child cleanup, and
  storage cleanup failure.
- Run `python -m pytest` from `backend/`.

## Dependencies

Blocked by: 02, 04, 05, 06

## Files likely touched

- `backend/app/api/blogs.py`
- `backend/app/api/drafts.py`
- `backend/app/repositories/blog_repository.py`
- `backend/tests/test_content_deletion.py`

## Estimated scope

Medium (4 files).

## Comments
