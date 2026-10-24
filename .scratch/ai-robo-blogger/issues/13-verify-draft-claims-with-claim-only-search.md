# 13: Verify draft claims with claim-only search

Type: task
Blocked by: 11

## Source requirements

- [PRD](../spec.md)
- [Claim verification module](../SPEC-claim-verification.md)

## Description

Identify factual claims in a composed draft, query web search with each claim
alone, and persist source evidence and an honest assessment. Keep claim search
separate from draft composition and do not send audio, transcripts, or the full
draft to the search provider.

## Acceptance criteria

- The user sees the exact claim, search provider, and purpose before initiating
  its search; obey the approved notice/opt-in policy.
- Each search request contains only its extracted claim and the minimum query
  fields required by the provider.
- Results distinguish supported, contradicted, and insufficient-evidence
  outcomes and retain linked source evidence.
- Search errors or empty evidence remain visibly unverified and cannot be
  labeled as fact-checked successfully.

## Verification

- Provider-fake tests inspect the exact outbound payload and verify evidence
  persistence and failure/insufficient outcomes.
- Manually verify that the claim and provider disclosure are visible before
  each search starts.
- Run `python -m pytest` from `backend/`.

## Dependencies

Blocked by: 11

## Files likely touched

- `backend/app/api/generation.py`
- `backend/app/services/orchestration_service.py`
- `backend/app/repositories/blog_repository.py`
- `backend/tests/test_claim_verification.py`
- `frontend/components/ResearchPanel.tsx`

## Estimated scope

Medium (5 files).

## Decision gate

Resolve whether disclosure is notice-only or explicit opt-in, and verify
provider retention terms, before enabling searches with user claims.

## Comments
