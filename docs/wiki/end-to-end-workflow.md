# End-to-End Workflow

## Fragment To Draft

```mermaid
sequenceDiagram
    participant W as Writer
    participant F as Next.js frontend
    participant B as FastAPI backend
    participant S as Audio storage
    participant D as Database
    participant A as Agent pipeline

    W->>F: Record a fragment
    F->>B: POST /blogs/{id}/fragments (multipart WebM)
    B->>S: Save immutable audio blob
    B->>D: Create Fragment (uploaded)
    B->>A: Process fragment
    A->>D: Save transcript, analysis, Blog Brain, claims
    alt Research is required
        A->>A: Search Tavily and evaluate evidence
        A->>D: Save questions, sources, and evidence
    end
    A->>D: Save versioned draft and QA result
    A->>B: Publish processing events
    B-->>F: Fragment response
    F->>B: Poll state and research every 30 seconds
```

## Blog Creation And Lookup

```mermaid
sequenceDiagram
    participant F as Next.js frontend
    participant R as blogs router
    participant D as BlogRepository and SQLModel

    F->>R: GET /healthz<br/>no parameters
    Note right of R: This app-level route bypasses routers, models, and agents.
    R-->>F: 200 { "status": "ok" }

    F->>R: POST /blogs<br/>{ "title": "Remote work notes" }
    Note right of R: FastAPI validates BlogCreateRequest.<br/>CurrentUserId is injected from settings.
    R->>D: create_blog(user_id, title)
    D->>D: INSERT Blog { id, user_id, title, status: "draft" }
    D->>D: INSERT Guardrail and BlogBrainSnapshot version 1
    R-->>F: 200 BlogResponse<br/>{ id, title, status, thesis: null, createdAt, updatedAt }

    F->>R: GET /blogs/{blogId}<br/>path: blogId: string
    R->>D: get_blog(blog_id)
    alt Blog exists
        D-->>R: Blog SQLModel row
        R-->>F: 200 { id, title, status, thesis, createdAt, updatedAt }
    else Blog missing
        R-->>F: 404 { "detail": "Blog not found" }
    end
```

## Upload And Full Fragment Processing

```mermaid
sequenceDiagram
    participant F as Next.js frontend
    participant R as blogs router
    participant S as StorageService
    participant O as OrchestrationService
    participant M as SQLModel repository
    participant T as TranscriptionAgent
    participant A as Analysis and Blog Brain agents
    participant P as Research planner and ResearchAgent
    participant W as WritingAgent and QA agent
    participant E as EventHub

    F->>R: Upload audio fragment
    Note right of R: POST blogs blogId fragments. Path parameter: blogId. Multipart field: audio UploadFile.
    R->>M: get_blog(blogId)
    alt Empty file or missing blog
        R-->>F: Error 400 empty audio, or 404 blog not found
    else Valid audio
        R->>S: save_audio(blogId, bytes, suffix)
        S-->>R: audio_url, estimated_duration_seconds
        R->>M: Insert Fragment with blog_id, audio_url, duration_seconds and status uploaded
        R->>M: Insert ProcessingEvent fragment.uploaded
        R->>O: await process_fragment(fragmentId)
        O->>M: Load Fragment and Blog, then insert fragment.received event
        alt Fragment has no transcript
            O->>T: run(fragment_id, audio_url)
            T-->>O: Transcription result with transcript, confidence and status
            alt Transcription fails or lacks configuration
                O->>M: Update Fragment status to failed or pending configuration
                O->>E: publish fragment_processing_failed
                R-->>F: 200 FragmentResponse with failure status
            else Transcription completes
                O->>M: Update Fragment with transcript and transcribed status
            end
        end
        O->>A: FragmentAnalysisAgent.run(transcript)
        A-->>O: Analysis with summary, topics, claims, questions, experiences, sentiment, intent
        O->>M: Insert FragmentAnalysis and set Fragment status analyzed
        O->>A: BlogBrainStateAgent.run(current_brain, analysis, guardrails)
        A-->>O: Brain state with thesis, arguments, sentiment, intent, questions, contradictions, provenance
        O->>M: Insert versioned BlogBrainSnapshot and Claim rows
        O->>P: ResearchPlannerAgent.run(claims, existing_questions)
        P-->>O: Planned questions with question, priority, deep research, human review
        O->>M: Insert pending ResearchQuestion rows
        opt A claim requires a source
            O->>P: ResearchAgent.run(question)
            P-->>O: Research finding with sources, evidence, summary, strength, confidence, status
            O->>M: Insert Source and Evidence, then mark questions and claims completed
        end
        O->>W: WritingAgent.run(title, brain, findings, prior_draft)
        W-->>O: Generated draft with content, provenance map, generated time
        O->>M: Insert versioned Draft and set Fragment status drafted
        O->>W: QaGuardrailsAgent.run(draft, brain, citation_required, guardrails)
        W-->>O: QA result with passed, issues, voice score, factuality score, publish blocked
        O->>M: Insert QA result and set Fragment status validated
        O->>E: publish fragment_processed and draft_updated
        R-->>F: 200 FragmentResponse with id, blogId, createdAt, durationSeconds, transcript and validated status
    end
```

## Blog Read Models

```mermaid
sequenceDiagram
    participant F as Next.js frontend
    participant R as blogs router
    participant O as OrchestrationService
    participant M as BlogRepository and SQLModel

    par Fragment list
        F->>R: GET /blogs/blogId/fragments with path blogId
        R->>M: list_fragments(blogId)
        M-->>R: Fragment SQLModel rows
        R-->>F: 200 FragmentResponse list with id, blogId, createdAt, durationSeconds, transcript, status
    and Blog Brain state
        F->>R: GET /blogs/blogId/state with path blogId
        R->>O: blog_state(blogId)
        O->>M: Load Blog, latest Brain, Claims, Fragments
        O-->>R: State with blog id, title, cards, claims, contradiction count, processing status
        R-->>F: 200 BlogStateResponse where each card has value, confidence, originType and updatedAt
    and Durable timeline
        F->>R: GET /blogs/blogId/timeline with path blogId
        R->>M: timeline(blogId)
        M-->>R: ProcessingEvent rows ordered by created_at
        R-->>F: 200 TimelineItem list with id, eventType, payload, status, attempt, createdAt
    and Research queue
        F->>R: GET /blogs/blogId/research with path blogId
        R->>M: list_research_questions(blogId), list_sources(blogId)
        M-->>R: questions plus blog-wide source count
        R-->>F: 200 ResearchQuestion list with id, question, status, priority, sourceCount
    end
```

## Manual Research And Draft Generation

```mermaid
sequenceDiagram
    participant F as Next.js frontend
    participant R as blogs and generation routers
    participant O as OrchestrationService
    participant M as BlogRepository and SQLModel
    participant A as ResearchAgent or WritingAgent
    participant E as EventHub

    F->>R: POST /blogs/blogId/research/run with path blogId and no body
    R->>O: await run_research(blogId)
    loop Each pending ResearchQuestion
        O->>A: ResearchAgent.run(question, deep=true)
        A-->>O: Research finding with sources, evidence, strength, confidence, status
        O->>M: Insert Source rows and mark ResearchQuestion completed
    end
    O->>M: Insert ProcessingEvent research.manual_run
    O->>E: Publish research completed with completed count
    R-->>F: 200 response with completed number

    F->>R: POST /blogs/blogId/draft/generate with path blogId and no body
    R->>O: generate_draft(blogId)
    O->>M: Load Blog, latest BlogBrainSnapshot, Sources, latest Draft
    alt Blog or Blog Brain missing
        O-->>R: None
        R-->>F: 404 error blog not found
    else Ready to generate
        O->>A: WritingAgent.run(title, brain.payload, findings, prior_draft)
        A-->>O: Generated draft with content, provenance map, generated time
        O->>M: Insert Draft with next version and draft.manual_generate event
        R-->>F: 200 DraftResponse with id, blogId, version, content, wordCount, updatedAt
    end
```

## Draft Review Interactions

```mermaid
sequenceDiagram
    participant F as Next.js frontend
    participant R as drafts router
    participant O as OrchestrationService
    participant M as BlogRepository and SQLModel
    participant Q as QaGuardrailsAgent

    F->>R: POST /drafts/draftId/revise with body revisionPrompt string
    R->>O: revise_draft(draftId, revisionPrompt)
    O->>M: get_draft(draftId)
    alt Draft missing
        R-->>F: 404 error draft not found
    else Draft exists
        Note over O: Current implementation appends a revision note and does not call WritingAgent.
        O->>M: Insert Draft next version with copied provenance map
        R-->>F: 200 DraftResponse with id, blogId, version, content, wordCount, updatedAt
    end

    F->>R: POST /drafts/draftId/validate with path draftId and no body
    R->>O: validate_draft(draftId)
    O->>M: Load Draft, latest BlogBrainSnapshot, Guardrail
    O->>Q: run(content, brain, citation_required, guardrails)
    Q-->>O: QA result with passed, issue type, text, severity, voice score, factuality score, publish blocked
    O->>M: Insert QaResult and draft.revalidated event
    R-->>F: 200 QA response with passed, issues, voiceScore, factualityScore, publishBlocked

    F->>R: GET /drafts/draftId/sources with path draftId
    R->>M: get_draft(draftId) then list_sources for the parent blog
    R-->>F: 200 SourceResponse list with id, title, url, publisher, publishedAt, credibility

    F->>R: GET /drafts/draftId/sentences/sentenceId/why with path draftId and sentenceId
    R->>O: sentence_why(draftId, sentenceId)
    O->>M: get_draft(draftId) then read the matching provenance map entry
    R-->>F: 200 Why response with sentenceId, sentenceText, userBasis, aiInterpretation, sourceEvidence, confidence
```

## Live Event Interaction

```mermaid
sequenceDiagram
    participant F as Next.js EventSource
    participant R as events router
    participant H as EventHub
    participant O as OrchestrationService

    F->>R: GET /blogs/blogId/events with Accept text/event-stream
    R->>H: subscribe(blogId)
    Note over R,H: Creates one asyncio.Queue for this browser connection.
    R-->>F: 200 text/event-stream remains open
    O->>H: Publish draft updated with draftId and version
    H-->>R: EventMessage with type, blog id, payload, created time
    R-->>F: SSE data with type, blogId, payload, createdAt
    Note over F,H: Disconnecting closes the async generator and removes its queue.
```

## Detailed Server Processing

The upload route in [backend/app/api/blogs.py](../../backend/app/api/blogs.py) accepts an audio file, rejects an empty payload, saves it through `StorageService`, creates a `Fragment`, adds `fragment.uploaded` to the event timeline, then awaits `OrchestrationService.process_fragment`.

1. **Receive**: The service loads the fragment and blog and persists `fragment.received`.
2. **Transcribe**: If the fragment has no transcript, the transcription agent runs. A non-`completed` result sets the fragment to `pending_configuration` or `transcription_failed`, records `fragment.transcription_failed`, emits an SSE failure event, and stops the workflow.
3. **Analyze**: The fragment analysis is saved in `FragmentAnalysis`; the fragment becomes `analyzed` and receives `fragment.analyzed`.
4. **Update Blog Brain**: The latest state snapshot plus guardrails are merged and saved as the next `BlogBrainSnapshot` version. `blog_brain.updated` records the transition.
5. **Plan research**: New claims are saved. The planner compares them with existing questions and creates deduplicated pending `ResearchQuestion` records.
6. **Research conditionally**: Claims with `source_required` cause each pending question to run through the research agent. Usable sources and evidence are persisted; all pending claims are then marked completed in the current implementation, including cases where the research result is insufficient.
7. **Write**: The writing agent consumes title, updated Brain, findings, and the prior draft. The repository saves a new `Draft` version and the fragment becomes `drafted`.
8. **Validate**: QA receives the draft, Brain, and full guardrail payload. A `QaResult` is stored and the fragment becomes `validated`.
9. **Notify**: The service emits durable timeline events and transient SSE messages for fragment completion and draft update.

## Manual Paths

### Run Research

The Research panel invokes `POST /blogs/{id}/research/run`. The service runs every pending question in deep mode, persists returned sources, marks questions complete, and emits `research_completed`. This path does not regenerate or revalidate a draft automatically.

### Generate A Draft

`POST /blogs/{id}/draft/generate` gets the latest Blog Brain and all sources for the blog, calls the writing agent, and saves another version. It uses source titles to build findings for the writer.

### Revise And Validate

`POST /drafts/{id}/revise` currently appends a `Revision request applied` note to the current draft and saves a new version. It does not yet use the writing model for targeted rewriting. `POST /drafts/{id}/validate` reruns QA and persists a new QA result.

## Read Models

`GET /blogs/{id}/state` returns the latest Blog Brain as UI-friendly cards. Each card contains `value`, `confidence`, `originType`, and `updatedAt`; claims include their evidence requirement and research status. `GET /blogs/{id}/timeline` returns durable processing history. `GET /blogs/{id}/research` returns questions and the current blog-wide source count.

## Current Limits

- The frontend is fixed to `demo-blog`; blog creation and account-specific navigation are not wired into the interface.
- SSE is implemented on the backend but disabled in the frontend shell.
- Filesystem storage, SQLite, and in-memory event queues are single-process development defaults.
- Sentence-level explanation responses and revision behavior are still placeholders.
- The OpenAI/Tavily paths require real credentials; otherwise provider-dependent stages use safe fallback behavior or stop with a visible status.