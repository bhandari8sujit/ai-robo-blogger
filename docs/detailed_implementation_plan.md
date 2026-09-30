# AI Voice-to-Blog: Detailed Implementation Plan

This document expands `ai_voice_to_blog.md` into an implementation-ready plan using the recommended stack and a LangChain-based multi-agent backend harness.

## 1. Scope and Non-Goals

### In Scope
- Voice-first blogging workflow: capture fragments -> transcribe -> analyze -> research -> draft -> QA -> publish.
- Next.js + TypeScript frontend with incremental, real-time updates.
- FastAPI backend with asynchronous orchestration.
- PostgreSQL + pgvector persistent state and semantic retrieval.
- Cloudflare R2 (or S3-compatible bucket) for audio storage.
- Tavily for standard web research; optional deep-research path.
- Authentication via Supabase Auth or Clerk.

### Explicitly Out of Scope (for now)
- Payments/billing integrations.
- Product analytics tooling.
- Error-monitoring platform integrations.

## 2. High-Level System Design

## Request Flow
1. User records short audio fragment in browser.
2. Frontend uploads fragment metadata + audio file.
3. Backend stores raw audio in R2 and emits `fragment.received` event.
4. LangChain orchestrator pipeline executes:
   - Transcription Agent
   - Fragment Analysis Agent
   - Blog Brain State Update Agent
   - Research Planner Agent
   - Research Agent (only if required)
   - Writing Agent (incremental section updates)
   - QA/Guardrails Agent
5. Frontend receives updated state via polling or websocket/SSE and updates UI.

## Processing Model
- Event-driven, fragment-by-fragment processing.
- Idempotent workers per stage with status columns and retry counts.
- Every stage writes structured artifacts for traceability.

## 3. Recommended Stack Mapping

- Frontend: Next.js 15+, TypeScript, App Router.
- Voice capture: MediaRecorder API + Web Audio API.
- Backend: Python 3.12+, FastAPI, Pydantic v2.
- Agent harness: LangChain + LangGraph (stateful DAG orchestration).
- Queue/execution: PostgreSQL-backed task table for MVP, Redis/Celery optional later.
- DB: PostgreSQL 16 + pgvector.
- Storage: Cloudflare R2 via S3 API (fallback S3).
- STT: OpenAI GPT-4o Mini Transcribe.
- LLMs:
  - Low-cost model for extraction/classification/routine drafting.
  - Stronger model for complex synthesis and final editorial QA.
- Search: Tavily default; deep mode provider optional.
- Auth: Supabase Auth or Clerk middleware.
- Hosting:
  - Frontend: Vercel.
  - Backend: Railway/Render.

## 4. Repository Layout (Suggested)

```text
robo-blog/
  frontend/
    app/
    components/
    hooks/
    lib/
  backend/
    app/
      api/
      agents/
      services/
      repositories/
      models/
      workers/
    tests/
  docs/
    detailed_implementation_plan.md
  agents/
    frontend/
    backend/
```

## 5. Data Model (MVP + Traceability)

Core tables:
- users
- blogs
- fragments
- fragment_analysis
- blog_brain_snapshots
- claims
- research_questions
- sources
- evidence
- outlines
- drafts
- guardrails
- qa_results
- processing_events

Important additions:
- `processing_events`: append-only event log (`event_type`, `payload`, `status`, `attempt`, `created_at`).
- `origin_type` fields for traceability (`USER_SAID`, `AI_INFERENCE`, `RESEARCH_FACT`, `AI_GENERATED`).
- `embedding` vectors on fragments/drafts/blog brain notes for semantic retrieval.

## 6. API Contract (Detailed)

### Blog + Fragments
- `POST /blogs` -> create draft blog session.
- `GET /blogs/{blog_id}` -> current summary and status.
- `POST /blogs/{blog_id}/fragments` -> multipart upload (audio + optional client transcript).
- `GET /blogs/{blog_id}/fragments` -> ordered fragment list and statuses.

### Processing + State
- `POST /fragments/{fragment_id}/process` -> enqueue or reprocess.
- `GET /blogs/{blog_id}/state` -> blog brain snapshot + pending work.
- `GET /blogs/{blog_id}/timeline` -> processing/event timeline.

### Research + Writing
- `POST /blogs/{blog_id}/research/run` -> process pending research queue.
- `GET /blogs/{blog_id}/research` -> questions, source quality, contradictions.
- `POST /blogs/{blog_id}/draft/generate` -> create or refresh full draft.
- `POST /drafts/{draft_id}/validate` -> guardrail + factuality checks.
- `POST /drafts/{draft_id}/revise` -> targeted revision.
- `GET /drafts/{draft_id}/sources` -> citation graph.

### Explainability
- `GET /drafts/{draft_id}/sentences/{sentence_id}/why` -> provenance and confidence.

## 7. LangChain Harness Design

Use LangGraph state machine with explicit typed state:

```python
class BlogPipelineState(TypedDict):
    blog_id: str
    fragment_id: str
    transcript: str | None
    fragment_analysis: dict | None
    blog_brain: dict
    research_queue_delta: list[dict]
    research_findings_delta: list[dict]
    draft_delta: dict | None
    qa_result: dict | None
    errors: list[str]
```

Node sequence:
1. `transcribe_fragment`
2. `analyze_fragment`
3. `update_blog_brain`
4. `plan_research`
5. Conditional edge:
   - no pending claims -> `write_incremental`
   - pending claims -> `run_research` -> `synthesize_research` -> `write_incremental`
6. `validate_guardrails`
7. `persist_outputs`

LangChain patterns to use:
- Structured outputs (`PydanticOutputParser` / JSON schema).
- Tool calling for Tavily and storage/database adapters.
- Retry wrappers with exponential backoff for model/search transient failures.
- Prompt templates versioned by task (`analysis_v1`, `research_v1`, etc.).

## 8. Frontend Plan (Detailed)

## UX Surfaces
- Voice capture panel: hold-to-record, pause, retry, fragment list.
- Blog Brain panel: thesis, arguments, sentiment, open questions.
- Research panel: pending vs verified claims, source confidence.
- Draft editor: AI draft with sentence-level provenance badges and revision controls.

## Frontend Data Strategy
- Redux Toolkit (RTK Query) for API state.
- SSE/websocket channel for live processing updates.
- Optimistic local fragment cards while uploads/transcription run.

## Accessibility + Reliability
- Keyboard-accessible recording controls.
- Upload retry + offline buffer for short disconnections.
- Explicit state badges: `uploaded`, `transcribed`, `analyzed`, `researched`, `drafted`, `validated`.

## 9. Backend Plan (Detailed)

## FastAPI Layers
- `api`: route handlers + auth guard.
- `services`: business orchestration, enqueue/retry policies.
- `agents`: LangChain graph nodes + prompts.
- `repositories`: DB and storage access abstraction.
- `workers`: event processors and scheduled tasks.

## Reliability Rules
- Every stage is idempotent by `fragment_id + stage`.
- Store stage outputs separately before final merge.
- Retry policy per stage with dead-letter status after N failures.
- Keep source audio immutable; permit transcript re-runs.

## 10. Research Quality Rules

- Trigger research only for externally verifiable claims.
- Source scoring dimensions:
  - credibility
  - recency
  - relevance
  - evidence strength
  - contradiction rate
- Require at least two quality sources for medium/high-impact factual claims.
- Mark unresolved contradictions in draft notes for QA.

## 11. Guardrails and Quality Gates

Pre-publish checks:
- Voice preservation score above threshold.
- Unsupported-claim count is zero (or explicitly flagged).
- Citation coverage for all `RESEARCH_FACT` statements.
- Tone + length match user guardrails.
- No silent stance shift from user position.

## 12. Security and Privacy Baseline

- Signed upload URLs for audio where possible.
- Encrypt secrets via platform-managed env vars.
- Store minimal personally identifying metadata.
- Row-level access checks by `user_id` on all blog data.
- Add content moderation checkpoints before publish endpoint.

## 13. Delivery Phases

### Phase 1 (2-3 weeks): Core Voice -> Draft
- Fragment upload and storage.
- STT + fragment analysis.
- Blog brain updates.
- Basic incremental draft generation.

### Phase 2 (2-3 weeks): Research + Citations
- Research queue extraction.
- Tavily integration.
- Evidence synthesis and citation insertion.

### Phase 3 (2 weeks): QA + Explainability
- Guardrail validator.
- Sentence provenance endpoint/UI.
- Revision loop and confidence surfacing.

## 14. Definition of Done (MVP)

A user can:
- Record multiple voice fragments in arbitrary order.
- See the system continuously update understanding.
- Receive a coherent, cited draft aligned to their voice and stance.
- Inspect why major statements exist and where evidence came from.
- Revise by adding new fragments without restarting the workflow.
