# 17: End-to-end quality and accessibility check

Type: task
Blocked by: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16

## Source requirements

- [PRD](../spec.md)
- [Capability map](../capability-map.md)

## Description

Verify the full capture-to-draft workflow, account isolation, provider payload
boundaries, responsive behavior, and accessible operation. Review representative
drafts for the agreed quality dimensions.

## Acceptance criteria

- The end-to-end workflow passes from account login through saved, exported
  draft and content deletion.
- Provider-boundary and two-user ownership checks pass with deterministic test
  doubles; live provider credentials are not required for automated tests.
- Keyboard and narrow-viewport checks cover recording, transcript editing,
  claim review, and draft actions.
- Drafts are reviewed for elegance, factual grounding, and preservation of
  author voice/viewpoint using the product-approved rubric.

## Verification

- Run backend tests, frontend type check, lint, and production build.
- Complete a documented manual end-to-end walkthrough using two accounts.
- Record quality-review results against the rubric; do not invent a numeric
  threshold if one has not been approved.

## Dependencies

Blocked by: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16

## Files likely touched

- `backend/tests/test_end_to_end.py`
- `frontend/app/page.tsx`
- `frontend/components/AppShell.tsx`
- `frontend/components/FragmentLibrary.tsx`
- `frontend/components/DraftWorkspace.tsx`

## Estimated scope

Medium (verification and any narrowly scoped fixes only).

## Decision gate

Do not add a frontend test-runner dependency or set a draft-quality threshold
without product approval.

## Comments
