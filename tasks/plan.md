# Implementation Plan: AI Robo Blogger

- **Status:** Approved
- **Task tracker:** `.scratch/ai-robo-blogger/issues/`

## Overview

Deliver the approved product in dependency order, starting with account-scoped
workspaces and server-enforced ownership, then saved fragments and editable
transcripts, selected-fragment composition, claim-only verification, and user
controlled draft review/export. Preserve the existing Next.js and FastAPI
architecture where it fits. Simplify generated code only when necessary for
each feature.

Product requirements and module contracts:

- [PRD](../.scratch/ai-robo-blogger/spec.md)
- [Capability map](../.scratch/ai-robo-blogger/capability-map.md)
- [Module specs](../.scratch/ai-robo-blogger/)

## Architecture and planning decisions

- Email/password registration and JWT login already exist in the backend, as
  does a frontend login/register screen. Start by validating the account-to-
  workspace path; do not replace authentication without evidence and approval.
- The current frontend is fixed to `demo-blog`. Replace that assumption with
  user-owned blog selection/creation before relying on private accounts.
- Server-side ownership enforcement is incomplete. Scope every operation
  through the authenticated user's owned parent resource; hiding UI controls
  is not an access-control boundary.
- Keep the repository's Next.js/TypeScript and FastAPI/Python stack. Do not
  select a production database, hosting service, token strategy, or new
  provider in this plan.
- Treat transcription, composition, and claim search as separate disclosure
  boundaries. Composition may send selected, edited transcript text to a
  third-party model only with clear disclosure. Web search receives only the
  claim under review.
- Track implementation work as one Markdown issue per vertical ticket under
  `.scratch/ai-robo-blogger/issues/`, following
  [the repository issue-tracker convention](../docs/agents/issue-tracker.md).
  Do not create a duplicate `tasks/todo.md`.
- Frontend has build, lint, and type-check scripts but no test script. Prefer
  existing backend pytest and provider fakes; request approval before adding a
  test-runner dependency.

## Dependency graph

```text
Existing registration/login
        │
        ▼
Account-owned workspace selection and blog APIs
        │
        ├──► Private fragment operations ──► Saved fragment library
        │                                      │
        ├──► Private draft/research APIs        ▼
        │                                Transcription and
        └──► User-controlled deletion     editable transcripts
                                               │
                                               ▼
                                   Selected-fragment composition
                                      │                     │
                                      ▼                     ▼
                             Claim-only search      Saved draft review
                                      └──────────┬──────────┘
                                                 ▼
                                      Corrections, citations,
                                           copy and export
```

Ownership and deletion work is a prerequisite for user data features. Transcript
editing precedes composition so the writer receives the text the user approved.
Composition precedes claim verification because claims are checked in the
composed draft. Review/export comes last because it consumes both the draft and
the claim evidence.

## Ordered implementation tickets

The linked issue files are the implementation task list. Each issue contains
its own acceptance criteria, verification, dependencies, and likely files.

### Phase 1: Account-scoped foundation

1. [01-account-workspace-bootstrap](../.scratch/ai-robo-blogger/issues/01-account-workspace-bootstrap.md) — replace the fixed demo workspace with
   account-owned blog listing/creation and selection, reusing existing
   registration/login.
2. [02-owner-scoped-blog-operations](../.scratch/ai-robo-blogger/issues/02-owner-scoped-blog-operations.md) — scope blog detail and state operations
   to the authenticated owner.
3. [03-owner-scoped-fragment-operations](../.scratch/ai-robo-blogger/issues/03-owner-scoped-fragment-operations.md) — scope fragment list, upload, and
   reprocessing through the owning blog.
4. [04-owner-scoped-draft-operations](../.scratch/ai-robo-blogger/issues/04-owner-scoped-draft-operations.md) — scope draft reads, revisions,
   validation, and sources through owned resources.
5. [05-owner-scoped-timeline-and-research-operations](../.scratch/ai-robo-blogger/issues/05-owner-scoped-timeline-and-research-operations.md) — scope timeline,
   research, and event operations through owned blogs.
6. [06-delete-fragments-and-audio](../.scratch/ai-robo-blogger/issues/06-delete-fragments-and-audio.md) — let owners delete fragments and
   associated audio/derived records with explicit cleanup status.
7. [07-delete-owned-drafts-and-workspaces](../.scratch/ai-robo-blogger/issues/07-delete-owned-drafts-and-workspaces.md) — let owners delete drafts and
   workspaces with their app-controlled child records.

### Checkpoint: Private workspace

- Existing registration/login still works.
- Two-user API tests demonstrate that one account cannot enumerate, read,
  process, or delete the other's resources.
- A user can delete owned content without affecting another account.
- No route exposes the seeded demo workspace across accounts.

### Phase 2: Fragment collection and transcript editing

8. [08-save-and-list-fragments](../.scratch/ai-robo-blogger/issues/08-save-and-list-fragments.md) — make recording/upload produce durable,
   independently browsable fragments rather than implicitly completing the
   entire composition workflow.
9. [09-transcribe-with-provider-disclosure](../.scratch/ai-robo-blogger/issues/09-transcribe-with-provider-disclosure.md) — expose transcription state and
   errors and disclose the transcription provider/data before sending audio.
10. [10-review-and-edit-transcripts](../.scratch/ai-robo-blogger/issues/10-review-and-edit-transcripts.md) — let owners persist transcript edits and
   use the edited text downstream without replacing source audio.

### Checkpoint: Editable source material

- A user can save multiple fragments and see processing/error states.
- The transcript can be edited, survives reload, and remains owned with its
  audio.
- Transcription provider requests contain only the audio needed for
  transcription.

### Phase 3: Composition and claim verification

11. [11-compose-selected-fragments](../.scratch/ai-robo-blogger/issues/11-compose-selected-fragments.md) — add a backend composition contract that
   accepts an ordered set of owned, transcribed fragment IDs and produces a
   draft from only those transcripts.
12. [12-compose-ui-and-provider-disclosure](../.scratch/ai-robo-blogger/issues/12-compose-ui-and-provider-disclosure.md) — connect selection and draft
    generation in the responsive UI and disclose provider/data/purpose before
    third-party composition.
13. [13-verify-draft-claims-with-claim-only-search](../.scratch/ai-robo-blogger/issues/13-verify-draft-claims-with-claim-only-search.md) — disclose the provider,
    extract draft claims, query the search provider with one claim at a time,
    and persist evidence with supported/contradicted/insufficient outcomes.

### Checkpoint: Grounded draft generation

- The selected fragment IDs/order and exact provider input are covered by
  deterministic tests.
- Composition does not include unselected or unrelated content.
- Search payload tests prove that audio, transcripts, and full drafts are not
  sent to the search provider.
- Provider failures and insufficient evidence cannot appear as successful
  verification.

### Phase 4: User-directed review and delivery

14. [14-accept-or-reject-correction-suggestions](../.scratch/ai-robo-blogger/issues/14-accept-or-reject-correction-suggestions.md) — persist claim-level
    suggestions and user decisions; change draft text only after acceptance.
15. [15-review-evidence-and-optional-citations](../.scratch/ai-robo-blogger/issues/15-review-evidence-and-optional-citations.md) — display source-linked
    findings and let users include or omit citations in the draft.
16. [16-save-copy-and-export-drafts](../.scratch/ai-robo-blogger/issues/16-save-copy-and-export-drafts.md) — ensure reviewed drafts persist and
    provide copy/export in the format selected by product review.
17. [17-end-to-end-quality-and-accessibility-check](../.scratch/ai-robo-blogger/issues/17-end-to-end-quality-and-accessibility-check.md) — verify the full workflow,
    responsive layouts, keyboard access, and the agreed draft-quality rubric.

### Checkpoint: Release candidate

- A user can complete the full capture → transcript edit → selected-fragment
  composition → fact review → saved/exported draft journey.
- Ownership, deletion, provider disclosures, claim-only search, and failure
  behavior pass their focused tests.
- Draft quality has been reviewed for elegance, factual grounding, and
  preservation of voice/viewpoint using the agreed rubric.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Authenticated endpoints load resources by ID without consistently checking ownership | High: cross-account data exposure | Add two-account authorization tests and owner-scoped repository/service methods before product data features. |
| Seeded `demo-blog` is coupled to frontend state and startup behavior | High: users may see shared data or have no personal workspace | Establish user-owned blog listing/creation, then remove or isolate demo seeding from user-visible flows. |
| Third-party provider retention and consent behavior are unresolved | High: privacy promises may exceed provider guarantees | Resolve provider terms and disclosure/opt-in policy before enabling content processing in production. |
| Current upload synchronously runs a full agent pipeline | Medium: fragments cannot be collected independently and failures block capture | Separate saving/transcription from later composition; expose durable statuses. |
| Frontend has no automated test runner | Medium: UI regressions may escape verification | Begin with existing backend tests and manual UI checks; ask before adding a frontend test dependency. |
| Draft quality is the primary success measure but has no agreed rubric/threshold | Medium: acceptance may be subjective | Review representative drafts against the three agreed dimensions and establish a measurable baseline before release. |
| Database relationships and storage deletion are not consistently enforced | High: orphaned records/audio or incomplete user deletion | Test deletion across parent/child records and storage; surface partial cleanup failures. |

## Open questions and decision gates

Resolve these before implementing the affected provider or UX behavior:

- Does clear disclosure require explicit opt-in, or is an informed notice
  sufficient for transcription, composition, and claim search?
- Which provider retention/deletion policies are acceptable?
- Are email verification, password recovery, or MFA required for v1?
- What audio formats, maximum duration/size, and transcription languages are
  required?
- Does each account need one default fragment workspace or multiple blogs?
- Which export formats are required?
- What draft-quality rubric and measurable threshold should define acceptance?
- What are the production database, deployment, and authentication/session
  requirements?

No production provider processing, schema migration strategy, or new dependency
is approved by this plan alone.
