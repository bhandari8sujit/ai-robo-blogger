# Module Spec: Claim Verification

- **Module id:** `claim-verification`
- **Depends on:** `composition`
- **Parent PRD:** [spec.md](spec.md)

## Objective

Help authors review factual claims in composed drafts using inspectable web
evidence, without silently rewriting the draft.

## Requirements

- Extract factual claims from the composed draft for verification.
- Before first search, disclose the search provider, exact claim text sent, and
  purpose.
- Send only the individual extracted claim needed for search; never send audio,
  full transcript, full draft, or unrelated personal context to the web-search
  provider.
- Associate search results and source metadata with the corresponding claim.
- Distinguish supported, contradicted, and insufficient-evidence outcomes.
- Offer evidence-backed correction suggestions for user acceptance; never
  automatically change draft text.
- Allow citations to be included in the final draft by user choice.

## Acceptance criteria

- Provider-boundary tests prove that search receives claim-only content.
- Each assessment links to source evidence or explicitly reports insufficient
  evidence.
- A suggested correction is traceable to its claim and sources.
- Search/provider failure remains visible and is not represented as a verified
  result.

## Verification

Deterministic tests use a fake search provider and assert request payload,
evidence association, outcome status, and failure behavior.

## Open questions

- Is disclosure notice sufficient, or must each user explicitly opt in?
- Which search provider and retention terms are acceptable?
