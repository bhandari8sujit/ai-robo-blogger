# 14: Accept or reject correction suggestions

Type: task
Blocked by: 13

## Source requirements

- [PRD](../spec.md)
- [Claim verification module](../SPEC-claim-verification.md)
- [Draft review and export module](../SPEC-draft-review-export.md)

## Description

Create and persist an evidence-backed, claim-level correction suggestion and
the author's accept/reject decision. An accepted correction updates only the
relevant draft claim; a rejected suggestion leaves draft text unchanged.

## Acceptance criteria

- Each correction is linked to its claim, evidence, and draft version.
- A suggestion does not assert more than the linked evidence supports.
- Accepting a suggestion creates a saved draft change limited to the associated
  claim; rejecting it records the decision without changing draft text.
- Another user cannot decide on or mutate the draft's suggestions.

## Verification

- Backend tests cover accept/reject, repeated decisions, missing evidence, and
  cross-user attempts.
- Run `python -m pytest` from `backend/`.

## Dependencies

Blocked by: 13

## Files likely touched

- `backend/app/api/drafts.py`
- `backend/app/models/entities.py`
- `backend/app/repositories/blog_repository.py`
- `backend/tests/test_correction_decisions.py`

## Estimated scope

Medium (4 files).

## Decision gate

The PRD requires asking before schema changes. Obtain approval for any required
model/migration change before implementation. Do not send claim/evidence to an
additional third-party model to generate correction text unless that processing
is explicitly disclosed and approved.

## Comments
