# PRD: AI Robo Blogger

- **Status:** Approved
- **Date:** 2026-10-13
- **Capability map:** [capability-map.md](capability-map.md)
- **Product intent:** [docs/intent/ai-robo-blogger.md](../../docs/intent/ai-robo-blogger.md)

## Objective

Build a responsive web application that helps people capture spontaneous
thoughts as short audio fragments, then compose selected fragments into elegant,
fact-grounded blog drafts that preserve the author's voice and viewpoint.

The primary value is the quality of the generated draft. Recording and
transcription are inputs to that outcome; research must make the writing more
reliable without silently changing the author's meaning.

## Users and core workflow

The intended audience is broad: anyone who wants to capture thoughts while
walking or doing other activities. A user should be able to:

1. Register and log in to a private account.
2. Record and save one or more audio fragments.
3. Have each fragment transcribed, then review and edit its transcript.
4. Select saved fragments to compose a blog post.
5. Review the generated draft and factual claims with linked evidence.
6. Accept or reject suggested corrections and optionally include citations.
7. Save a draft in the app, then copy or export it.
8. Delete their stored content at any time.

## Product principles

- **Preserve intent:** Improve clarity and elegance without inventing the user's
  experiences, beliefs, or claims.
- **Keep the author in control:** Do not silently apply fact-check corrections;
  present them for acceptance or rejection.
- **Make evidence inspectable:** Tie claim assessments and optional citations
  to sources returned by web search.
- **Be explicit about processing:** Disclose which provider receives which
  content and why before third-party processing.
- **Keep data private:** Every stored resource belongs to an authenticated
  owner; deletion covers stored source and derived content.
- **Keep implementation understandable:** The existing AI-generated code is
  verbose and difficult to reason about. Simplify only where needed for a
  feature; no standalone refactoring effort.

## Scope

### First release

- Responsive desktop web experience.
- Separate user accounts with registration and login.
- Private audio fragments, transcripts, and drafts with user-controlled
  deletion.
- Audio recording, upload, storage, and fragment listing.
- Model-based speech transcription and editable transcripts.
- User-selected, multi-fragment draft composition.
- Elegant writing that retains the user's voice and viewpoint.
- Claim-level fact-checking with linked evidence and user-approved correction
  suggestions.
- Optional citations in the final draft.
- In-app draft storage, copy, and export.

### Not in first-release scope

- Native mobile apps.
- Direct publishing to external blog platforms.
- A standalone refactor of generated frontend or backend code.
- Payments, analytics, or integrations not required for the workflow.

## Functional requirements

### Authentication — `authentication`

- Users can register with email and password and log in with those credentials.
- Email identity is normalized consistently; duplicate registration is rejected
  without creating a second account.
- Passwords are stored using a modern password-hashing function, never in
  plaintext.
- Authenticated requests identify the actual active user. Invalid, expired, or
  inactive-account credentials are rejected.
- The frontend exposes usable registration, login, and logout flows.
- Authentication responses and errors do not disclose whether a password was
  correct for a particular registered account beyond the necessary
  duplicate-registration response.

### Ownership and privacy — `identity-privacy`

- Every blog, fragment, transcript, claim, source association, evidence record,
  and draft is scoped to an owning user through its parent resource.
- Every read, create, update, process, and delete operation verifies ownership;
  possession of another user's resource identifier is insufficient.
- New accounts cannot see or mutate seeded demo data or another user's data.
- A user can delete individual content and can delete their own stored content
  without affecting other users. Deletion covers audio objects and derived
  records in the application's control.
- The product explains any provider-side retention that the application cannot
  itself delete; provider deletion behavior must not be promised without
  verification.

### Audio fragments — `audio-fragments`

- Users can record audio in a supported desktop browser and upload/save it as
  an independent fragment.
- Users can list and identify their own saved fragments and see their
  processing status.
- The application validates file presence, supported media type, and configured
  upload limits before processing.
- Audio remains associated with its owner and can be deleted by that owner.
- Native mobile and offline/background recording are not required for v1.

### Transcripts — `transcripts`

- Each saved audio fragment can be transcribed by a speech-to-text model.
- Before first transcription processing, the user is told which provider
  receives the audio and for what purpose.
- Transcription state and failures are visible; failure must not appear as a
  successful empty transcript.
- Users can review and edit a transcript before composition. Saved edits are
  the text used in composition.
- Editing a transcript does not silently replace the original audio.

### Composition — `composition`

- Users explicitly select one or more saved, transcribed fragments for a post.
- The selected fragment order is deterministic and presented to the user.
- The generated draft uses selected, user-edited transcripts and does not
  silently include unselected fragments.
- The composition provider may receive selected transcripts and the minimum
  necessary composition context. Before third-party composition, the user sees
  a clear disclosure identifying the provider, data sent, and purpose.
- The result is a coherent, elegant blog draft that preserves the author's
  viewpoint and voice. It must not fabricate personal experiences or attribute
  unsupported opinions to the author.
- Generated drafts are stored as user-owned drafts and can be revised without
  overwriting prior versions where version history is already part of the
  product design.

### Claim verification — `claim-verification`

- The backend identifies factual claims in the composed draft and searches for
  evidence using a web-search provider.
- A search request contains only the specific extracted claim needed for that
  search—not audio, the full transcript, the full draft, or unrelated personal
  content.
- Before the first claim search, the user sees a clear disclosure identifying
  the search provider, claim text sent, and purpose.
- Each result distinguishes evidence that supports a claim, contradicts it, or
  is insufficient to assess it. No result may imply verification without
  usable evidence.
- A correction is a suggestion, not an automatic edit. Each suggestion is
  connected to the claim and its supporting source evidence.
- Source links and enough metadata to identify the evidence are retained with
  the draft's claim review.
- Citations can be included in the final draft by user choice.

### Draft review and export — `draft-review-export`

- Users can inspect claims, evidence, and proposed corrections alongside the
  draft.
- Users can accept or reject each correction; accepting one changes only the
  relevant draft text and is attributable to that review action.
- Users can include or omit citations from the draft.
- Users can save, reopen, and edit their own drafts.
- Users can copy a draft and export it in a format agreed before implementation.
- No direct publish action is required in v1.

## External processing and data boundaries

| Processing purpose | Content permitted to leave the app | Required user-facing behavior |
|---|---|---|
| Transcription | Audio submitted for transcription | Disclose provider, data, and purpose before processing |
| Draft composition | Selected, edited transcript text and minimum necessary context | Clear disclosure of provider, data sent, and purpose |
| Claim search | The extracted claim being checked, only | Disclose provider, claim text, and purpose |
| Other processing | No user recording or content unless the user approves a changed policy | Do not silently send content to an additional provider |

This specification permits third-party composition when clearly disclosed,
based on the user's clarification during requirements discovery. The user has
not yet specified whether this disclosure is notice-only or requires explicit
opt-in; see Open Questions.

## Quality attributes

- **Privacy and access control:** Enforce authentication and per-user ownership
  server-side on every resource operation.
- **Data minimization:** Send only the content necessary for each disclosed
  external processing purpose.
- **Reliability:** Persist processing status and surface provider failures;
  do not convert missing credentials, failed searches, or transcription errors
  into success-shaped results.
- **Accessibility:** Recording, transcript editing, claim review, and draft
  actions are operable with keyboard and accessible labels.
- **Responsive design:** The desktop web experience remains usable at narrower
  viewport widths.
- **Maintainability:** Prefer focused modules and clear data-flow boundaries;
  avoid broad refactors unrelated to a delivered capability.

## Acceptance criteria

The release is functionally complete when:

1. A new user can register, log in, log out, and return to their own private
   content after authenticating again.
2. Two test users cannot read, edit, process, export, or delete each other's
   resources, including by substituting resource identifiers in API requests.
3. A user can record/upload several fragments, see their statuses, edit
   transcripts, select a subset in a chosen order, and produce a draft from
   only that selection.
4. Provider-boundary tests prove that transcription sends audio only for
   transcription, composition sends selected text only after disclosure, and
   web search receives a claim rather than a transcript or draft.
5. Claim review shows evidence and a correction suggestion where appropriate,
   supports insufficient-evidence results, and changes the draft only after the
   user accepts a suggestion.
6. A user can choose citations, save/reopen their draft, copy/export it, and
   delete their own content without affecting another account.
7. The generated writing is reviewed against three product dimensions:
   elegance, factual grounding, and preservation of author voice/viewpoint.
   Numeric quality thresholds are not set by this PRD and require product
   agreement.

## Tech stack and repository context

- Frontend currently uses Next.js App Router, React, TypeScript, and Redux
  Toolkit / RTK Query (`frontend/package.json`).
- Backend currently uses Python 3.12+, FastAPI, SQLModel, JWT bearer
  authentication, and a relational database (`backend/pyproject.toml`).
- The backend contains email/password registration and login endpoints and a
  current-user endpoint. Existing JWT authentication should be evaluated and
  integrated rather than replaced by assumption.
- OpenAI and Tavily integrations are currently configured in the backend.
  Product approval of the processing boundaries above does not establish
  provider-specific retention or deletion guarantees; those must be verified.
- This PRD does not choose a production database, hosting platform, token
  storage strategy, or new dependency. Any such architectural choice is
  resolved in the implementation plan and, if significant, an ADR.

## Commands and verification

Run commands from the relevant project directory:

| Purpose | Command |
|---|---|
| Frontend development | `npm run dev` (from `frontend/`) |
| Frontend production build | `npm run build` (from `frontend/`) |
| Frontend lint | `npm run lint` (from `frontend/`) |
| Frontend type check | `npm run typecheck` (from `frontend/`) |
| Backend tests | `python -m pytest` (from `backend/`) |

There is currently no frontend test script in `frontend/package.json`. The plan
must decide how to verify user-visible flows and whether a test runner is
needed; adding a dependency requires approval under Boundaries.

## Project structure

- `frontend/`: responsive web UI, audio capture, authenticated API client, and
  user workflows.
- `backend/app/api/`: auth and product API routes.
- `backend/app/services/`: orchestration and business operations.
- `backend/app/agents/`: transcription, analysis, research, writing, and QA
  providers/agents.
- `backend/app/repositories/` and `backend/app/models/`: persistence boundary
  and relational data model.
- `backend/tests/`: backend API and service tests.
- `.scratch/ai-robo-blogger/`: PRD, module specs, plan, and implementation
  tickets.
- `docs/wiki/`: current-implementation architecture and behavior notes; keep
  these distinct from target product requirements.

## Code style

Follow the repository's existing typed boundaries, explicit errors, and
dependency-injected current-user pattern. Avoid broad exception handling,
unnecessary abstractions, and casts that bypass type checks.

```python
@router.get("/blogs/{blog_id}")
def get_blog(
    blog_id: Annotated[str, Path(min_length=1)],
    session: DbSession,
    user_id: CurrentUserId,
) -> BlogResponse:
    blog = BlogRepository(session).get_owned_blog(blog_id, user_id)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return to_blog_response(blog)
```

This illustrates the required ownership boundary, not an assertion that
`get_owned_blog` or `to_blog_response` currently exists.

## Testing strategy

- **Backend unit tests:** ownership checks, content deletion, claim-only
  provider payload construction, transcription/composition input boundaries,
  and status/error handling.
- **Backend API tests:** register/login/current-user flows; unauthenticated
  rejection; cross-user access attempts for each resource family; CRUD,
  composition, fact-check review, and deletion.
- **Frontend tests:** accessible login/register, recording/upload states,
  transcript editing, multi-fragment selection, correction review, citations,
  save, copy/export, and logout.
- **Integration tests:** use provider fakes to assert the exact content sent to
  each integration; do not require live API keys in deterministic tests.
- **Manual quality review:** evaluate representative drafts for elegance,
  evidence-grounding, and voice preservation. Establish numerical thresholds
  only after the product owner selects an evaluation method and baseline.

## Boundaries

- **Always:** enforce resource ownership on the server; make provider data
  transfers explicit; validate uploads and inputs; preserve source audio when
  transcripts are edited; expose failures; test provider payload boundaries;
  simplify existing code only as needed for a feature.
- **Ask first:** changing authentication/token architecture; database schema or
  migration strategy; adding dependencies or providers; changing CI; enabling
  provider retention/deletion behavior; defining consent requirements or
  measurable draft-quality thresholds.
- **Never:** send audio or a full draft to web search; silently apply
  corrections; expose demo/shared-user content across accounts; claim a fact
  is supported without source evidence; commit secrets; launch a standalone
  refactor as part of this initiative.

## Open questions

1. Does clear disclosure before third-party composition/transcription/search
   require explicit opt-in, or is an informed notice sufficient?
2. Which provider retention/deletion policies are acceptable for transcription,
   composition, and claim search, and what disclosures are required?
3. Are email verification, password recovery, or MFA required for the first
   release?
4. What audio formats, maximum duration/size, and transcription languages are
   required?
5. Does each account need one default fragment workspace or multiple blogs?
6. Which export format(s) are required (for example, Markdown or plain text)?
7. What draft-quality evaluation rubric and measurable acceptance threshold
   should be used beyond the three stated quality dimensions?
8. What is the target deployment/database environment and corresponding
   production authentication/session policy?

## Module specifications

- [Authentication](SPEC-authentication.md)
- [Identity and privacy](SPEC-identity-privacy.md)
- [Audio fragments](SPEC-audio-fragments.md)
- [Transcripts](SPEC-transcripts.md)
- [Composition](SPEC-composition.md)
- [Claim verification](SPEC-claim-verification.md)
- [Draft review and export](SPEC-draft-review-export.md)
