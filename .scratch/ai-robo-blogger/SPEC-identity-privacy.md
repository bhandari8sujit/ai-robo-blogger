# Module Spec: Identity and Privacy

- **Module id:** `identity-privacy`
- **Depends on:** `authentication`
- **Parent PRD:** [spec.md](spec.md)

## Objective

Ensure authenticated users can access only their own product data and can
delete content they own.

## Requirements

- Scope every domain record and stored audio object to one account.
- Enforce ownership in server-side reads, writes, processing, export, and delete
  operations; never rely on the UI to protect data.
- Do not expose seeded demo content to newly registered users.
- Deletion removes user-owned source and derived data in the application's
  control, including audio objects, transcripts, analyses, claims, evidence
  associations, and drafts.
- Surface failures when cleanup is incomplete; do not report success while
  owned content remains.
- Disclose provider-side retention limits that the application cannot control.

## Acceptance criteria

- Unauthenticated requests to private resources are rejected.
- Two-account tests show that substituting IDs cannot read or mutate another
  account's resources across every resource family.
- Deleting one user's content leaves another user's records and blobs intact.
- A completed deletion leaves no associated app-controlled records or blobs.

## Verification

Backend API tests exercise ownership and deletion with at least two users,
including guessed IDs and parent/child resource access.

## Open questions

- What deletion completion/retention guarantees can each configured provider
  offer?
- Does account deletion belong in v1, in addition to per-item content deletion?
