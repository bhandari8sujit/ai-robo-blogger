# AI-Powered Voice-to-Blogging Agent

## 1. Product Concept

An AI voice-first blogging agent that lets a user **think out loud in fragmented speech** rather than dictate a complete article.

The system:

> **Speak → Transcribe → Understand → Research → Synthesize → Write → Validate → Publish**

The user can provide thoughts over many short voice fragments. The system continuously builds an understanding of the topic, detects sentiment and intent, researches claims and missing context, and produces a coherent blog while preserving the user's voice and respecting explicit guardrails.

### Product proposition

> **“I can think out loud for 10 minutes, in whatever order I want, and AI turns my messy thoughts into a well-researched article that still sounds like me.”**

The differentiator is not speech-to-text by itself. It is the ability to transform **unstructured, incremental human thinking into a researched, structured, publishable article**.

---

# 2. Core User Experience

A user starts a new blog and presses **Record**.

They might say:

> “I've been thinking about whether AI is actually making programmers more productive…”

Later:

> “The thing people don't understand is that…”

Later:

> “Maybe mention that study about developer productivity.”

Later:

> “I don't want this to sound anti-AI.”

The user does not need to organize their thoughts beforehand.

The system maintains a continuously evolving **Blog Brain** containing:

- Central thesis
- User's arguments
- Personal experiences
- Claims
- Questions
- Research requirements
- Sources
- Sentiment
- Intent
- Outline
- Draft
- User-defined guardrails

The user can continue speaking even after a draft exists:

> “Actually, I disagree with that paragraph.”

The system updates the relevant part of the article rather than starting from scratch.

---

# 3. End-to-End Architecture

```text
                         USER
                          │
                          ▼
                 ┌──────────────────┐
                 │ Next.js Web App  │
                 │ Voice-first UI   │
                 └────────┬─────────┘
                          │
                    Voice Fragment
                          │
                          ▼
                 ┌──────────────────┐
                 │ FastAPI Backend  │
                 └────────┬─────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
       ┌─────────────┐        ┌──────────────┐
       │ Audio Store │        │ PostgreSQL   │
       │ R2 / S3     │        │ Blog State   │
       └──────┬──────┘        └──────┬───────┘
              │                      │
              ▼                      │
       Speech-to-Text                │
              │                      │
              ▼                      │
         Transcript ─────────────────┤
                                     ▼
                            Fragment Analyzer
                                     │
                  ┌──────────────────┼─────────────────┐
                  ▼                  ▼                 ▼
               Topics             Claims           Sentiment
                  │                  │                 │
                  └──────────────────┼─────────────────┘
                                     ▼
                              Research Queue
                                     │
                                     ▼
                              Tavily / Exa
                                     │
                                     ▼
                            Research Synthesis
                                     │
                                     ▼
                              Blog Generator
                                     │
                                     ▼
                              QA / Guardrails
                                     │
                                     ▼
                                Final Blog
```

---

# 4. Recommended Technology Stack

The goal is to use inexpensive models for routine operations and reserve stronger reasoning models for difficult synthesis.

| Component | Recommended | Purpose |
|---|---|---|
| Frontend | Next.js + TypeScript | Web application |
| Recording | Browser MediaRecorder API + Web Audio API | Voice capture |
| Backend | Python + FastAPI | APIs and orchestration |
| Database | PostgreSQL | Persistent application state |
| Vector search | pgvector | Semantic memory/search |
| Audio storage | Cloudflare R2 or S3 | Original audio files |
| Speech-to-text | GPT-4o Mini Transcribe | Low-cost transcription |
| LLM | Low-cost Gemini/OpenAI model | Extraction, classification, drafting |
| Web search | Tavily | AI-oriented web search |
| Deep research | Tavily Research or Exa Agent | Complex research |
| Authentication | Supabase Auth or Clerk | User accounts |
| Hosting | Vercel + Railway/Render | Simple MVP deployment |
| Payments | Stripe | SaaS billing |
| Analytics | PostHog | Product analytics |
| Error monitoring | Sentry | Application monitoring |

## Cost-control principle

Do **not** use an expensive reasoning model for every operation.

Use inexpensive models for:

- Sentiment analysis
- Topic extraction
- Intent detection
- Claim extraction
- Summarization
- Basic rewriting
- Classification
- Routine QA

Use stronger models only for:

- Difficult research synthesis
- Conflicting evidence
- Complex reasoning
- Final editorial review
- Ambiguous claims

---

# 5. Step 1 — Capture Voice Fragments

The frontend should allow the user to record short voice fragments.

Example:

```text
┌──────────────────────────────────────────────┐
│                My New Blog                   │
│                                              │
│        🎙 Hold to speak                     │
│                                              │
│  "I've been thinking about AI coding..."    │
│                                              │
│        + Add another thought                 │
└──────────────────────────────────────────────┘
```

Use the browser's:

- MediaRecorder API
- Web Audio API

Store each recording independently.

Example:

```json
{
  "fragment_id": "f_123",
  "blog_id": "b_456",
  "audio_url": "https://storage/.../f_123.webm",
  "duration_seconds": 18.4,
  "created_at": "2026-08-29T20:00:00Z"
}
```

### Important design decision

Treat every fragment as an **event**.

Do not wait for the user to finish an entire blog.

```text
Fragment 1
   ↓
Process

Fragment 2
   ↓
Process

Fragment 3
   ↓
Process
```

This enables continuous understanding and incremental drafting.

---

# 6. Step 2 — Speech-to-Text

Send each audio fragment to a transcription service.

### Recommended MVP

**GPT-4o Mini Transcribe**

The objective is inexpensive, reliable transcription rather than sophisticated reasoning.

Pipeline:

```text
Audio
  ↓
Speech-to-text
  ↓
Transcript
```

Example:

```text
"I've been thinking about whether AI is
actually making programmers more productive."
```

Store both the original audio and transcript.

### Why keep the original audio?

Never throw away the source recording.

It allows future improvements such as:

- Re-transcription
- Better speech models
- Speaker/emotion analysis
- User corrections
- Audio playback
- Auditing

---

# 7. Step 3 — Understand Every Fragment

Do not immediately ask an LLM to write a blog.

First convert the transcript into structured information.

For example:

```json
{
  "summary": "User is questioning whether AI coding tools improve developer productivity.",
  "topics": [
    "AI coding assistants",
    "developer productivity"
  ],
  "claims": [
    {
      "text": "AI may make programmers more productive",
      "needs_research": true
    }
  ],
  "personal_experience": null,
  "questions": [
    "Does AI actually improve developer productivity?"
  ],
  "sentiment": {
    "primary": "curious",
    "secondary": "skeptical",
    "intensity": 0.62
  },
  "intent": "exploration"
}
```

Use structured JSON output from the LLM.

This makes downstream processing much easier.

Store:

- Fragment
- Transcript
- Summary
- Topics
- Claims
- Questions
- Intent
- Sentiment
- Personal experiences

---

# 8. Step 4 — Maintain the “Blog Brain”

The system needs a persistent representation of what the blog currently means.

Example:

```json
{
  "topic": "AI coding assistants",

  "central_thesis":
    "AI coding tools increase productivity but may shift developer effort toward reviewing and reasoning.",

  "user_position":
    "cautiously optimistic",

  "arguments": [
    "faster prototyping",
    "less boilerplate",
    "more code review"
  ],

  "personal_experiences": [
    "..."
  ],

  "research_questions": [
    "Does AI actually improve developer productivity?"
  ],

  "sources": [],

  "guardrails": {
    "tone": "conversational",
    "length": "1500-2000",
    "preserve_user_voice": true,
    "show_counterarguments": true,
    "citations": true
  }
}
```

This state should be updated whenever a new fragment arrives.

### Why this matters

Do not keep adding every transcript to one enormous prompt.

Instead:

```text
User fragments
      ↓
Structured state
      ↓
Current understanding
```

This reduces token usage and gives the system much better control.

---

# 9. Step 5 — Detect What Requires Research

Research should be selective.

Not every sentence needs an internet search.

For example:

> “I personally found GitHub Copilot useful.”

This is primarily a personal experience.

But:

> “AI makes developers 30% more productive.”

is an externally verifiable claim and should trigger research.

Create a research queue:

```text
Research Queue
──────────────────────────────
✓ AI coding productivity
✓ Developer productivity studies
✓ AI coding assistant adoption
○ Personal experience — no research
○ Personal opinion — no research
```

Each claim can have:

```json
{
  "claim_id": "claim_123",
  "text": "AI makes developers 30% more productive",
  "requires_research": true,
  "research_status": "pending"
}
```

This is one of the most important cost-control mechanisms.

---

# 10. Step 6 — Internet Search and Research

## Recommended MVP search provider: Tavily

Tavily is designed for AI-agent search and provides search results plus content useful for downstream LLM processing.

Use it for:

- Search queries
- Source discovery
- Research
- Fact checking
- Recent information
- Supporting evidence

Basic pipeline:

```text
Research Question
      ↓
Generate search query
      ↓
Tavily
      ↓
Search results
      ↓
Filter sources
      ↓
Extract evidence
      ↓
Synthesize
```

Example:

```text
Question:
Does AI actually improve developer productivity?

Search:
developer AI coding assistant productivity study 2026
```

The system might retrieve several relevant sources.

### Tavily vs Exa

A good initial approach:

**Tavily → default search**

**Exa → advanced/deep research option**

Exa is particularly useful when you need stronger semantic search and agent-style research.

Do not use deep research for every article.

Use:

```text
Simple claim
   ↓
Normal search
```

and:

```text
Complex / controversial claim
   ↓
Deep research
```

---

# 11. Source Evaluation

Never blindly trust search results.

The research pipeline should evaluate:

- Source credibility
- Recency
- Relevance
- Primary vs secondary source
- Agreement with other sources
- Conflicting evidence
- Strength of evidence

Pipeline:

```text
10 search results
      ↓
Remove irrelevant sources
      ↓
Prefer primary/high-quality sources
      ↓
Extract evidence
      ↓
Cross-check
      ↓
Identify contradictions
      ↓
Research summary
```

Example:

```json
{
  "question": "Does AI increase developer productivity?",

  "conclusion":
    "Evidence suggests productivity improvements in some coding tasks, but results vary by task and developer.",

  "strength": "moderate",

  "supporting_sources": [
    "Source A",
    "Source B"
  ],

  "contradicting_sources": [
    "Source C"
  ],

  "caveat":
    "Results vary considerably by task complexity."
}
```

Do not simply pass raw webpages to the writing model.

First turn research into structured evidence.

---

# 12. Step 7 — Generate the Blog

Once the system has:

- User thoughts
- Blog state
- Research findings
- Sources
- Outline
- Guardrails

the writing model can generate the article.

The prompt should explicitly instruct the model to:

- Preserve the user's underlying position
- Preserve personal experiences
- Distinguish opinions from facts
- Cite externally sourced claims
- Avoid strengthening claims beyond available evidence
- Surface contradictions in research
- Avoid silently changing the user's argument
- Match the requested tone
- Follow requested length
- Avoid prohibited subjects/content

Example guardrail:

> Never change the user's position without explicitly telling them.

### Example

User says:

> “I feel like remote work sometimes makes collaboration harder.”

The AI should not silently turn this into:

> “Remote work reduces collaboration.”

The second statement is materially stronger.

---

# 13. Step 8 — QA and Guardrails

Before showing the final article, run an editorial validation pass.

Input:

```text
Draft
+
Original user thoughts
+
Research findings
+
Guardrails
```

Output:

```json
{
  "passed": false,

  "issues": [
    {
      "type": "unsupported_claim",
      "text": "...",
      "severity": "medium"
    },
    {
      "type": "voice_drift",
      "text": "...",
      "severity": "low"
    }
  ]
}
```

Possible checks:

### Factuality

- Does the source actually support the claim?
- Are statistics accurate?
- Is the claim stronger than the evidence?

### Voice

- Does the article still sound like the user?
- Did the AI introduce opinions the user didn't express?

### Guardrails

- Correct length?
- Correct tone?
- Required structure?
- Banned topics avoided?
- Citations included?

### Consistency

- Does the conclusion match the thesis?
- Are contradictory arguments handled properly?
- Are personal experiences clearly distinguished from research?

---

# 14. Citation Architecture

Every externally sourced claim should have provenance.

Store:

```json
{
  "claim_id": "claim_123",
  "source_id": "source_456",
  "supporting_text": "...",
  "url": "...",
  "confidence": 0.94
}
```

The final article might contain:

> AI coding assistants can improve performance on certain programming tasks, although results vary by task and developer experience. [1]

Then:

```text
Sources

[1] Research paper
[2] Developer survey
[3] Industry report
```

This creates **claim-level provenance**.

---

# 15. The “Why Is This Here?” Feature

A particularly valuable trust feature is an explanation for every important sentence.

The user can click a sentence and see:

```text
Why is this here?

✓ Based on your statement:
  "AI makes code review more important."

✓ Research:
  2 sources support this conclusion.

✓ AI interpretation:
  Your statement was treated as an opinion,
  not an established fact.

✓ Source:
  Research paper

✓ Confidence:
  91%
```

This helps users distinguish:

- What they said
- What AI inferred
- What research established
- What AI added

It also creates trust in the system.

---

# 16. Suggested User Interface

```text
┌──────────────────────────────────────────────────────────┐
│ My Blog                                                   │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ 🎙 "I've been thinking about AI and software..."    │ │
│ │                                                      │ │
│ │ + Add another thought                               │ │
│ └──────────────────────────────────────────────────────┘ │
│                                                          │
│ AI understands your thoughts                             │
│                                                          │
│ ● Thesis                                                 │
│   AI changes the role of software developers              │
│                                                          │
│ ● Researching                                            │
│   3 claims · 5 sources · 1 conflicting viewpoint           │
│                                                          │
│ ● Draft                                                  │
│   1,247 words                                             │
│                                                          │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ "AI isn't replacing developers. It's changing..."   │ │
│ │                                                      │ │
│ │ [Edit] [Regenerate] [Why?] [Publish]                │ │
│ └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

---

# 17. Suggested Database Model

A simple initial PostgreSQL schema could contain:

```text
users
  id
  email
  created_at

blogs
  id
  user_id
  title
  thesis
  status
  created_at
  updated_at

fragments
  id
  blog_id
  audio_url
  transcript
  duration
  created_at

fragment_analysis
  id
  fragment_id
  summary
  sentiment
  intent
  topics
  claims
  questions

claims
  id
  blog_id
  text
  source_required
  research_status
  confidence

research_questions
  id
  blog_id
  question
  status

sources
  id
  blog_id
  title
  url
  publisher
  published_at
  credibility
  retrieved_at

evidence
  id
  claim_id
  source_id
  supporting_text
  confidence

outlines
  id
  blog_id
  structure

drafts
  id
  blog_id
  content
  version
  created_at

guardrails
  id
  blog_id
  tone
  length
  audience
  preserve_voice
  citation_required
  banned_topics

qa_results
  id
  draft_id
  passed
  issues
```

Use PostgreSQL + pgvector if you later want semantic retrieval of the user's previous thoughts and writing.

---

# 18. API Design

A clean initial API could look like:

```text
POST   /blogs
GET    /blogs/:id

POST   /blogs/:id/fragments
GET    /blogs/:id/fragments

POST   /fragments/:id/transcribe
POST   /fragments/:id/analyze

GET    /blogs/:id/state

POST   /blogs/:id/research
GET    /blogs/:id/research

POST   /blogs/:id/outline
POST   /blogs/:id/draft

POST   /drafts/:id/validate
POST   /drafts/:id/revise

GET    /drafts/:id/sources
```

The backend should orchestrate these operations asynchronously where appropriate.

---

# 19. Agent Architecture

Do not build one giant AI agent.

Use specialized steps/agents.

```text
                    Blog Orchestrator
                           │
       ┌───────────────────┼────────────────────┐
       ▼                   ▼                    ▼
 Fragment Agent       Research Agent       Writing Agent
       │                   │                    │
       ▼                   ▼                    ▼
  Understand          Find evidence         Generate draft
       │                   │                    │
       └───────────────────┼────────────────────┘
                           ▼
                       QA Agent
                           │
                           ▼
                      Final Article
```

### Fragment Agent

Responsibilities:

- Summarize
- Extract topics
- Detect claims
- Detect questions
- Detect sentiment
- Detect intent

### Research Agent

Responsibilities:

- Determine what requires research
- Search
- Evaluate sources
- Extract evidence
- Identify contradictions
- Produce research summaries

### Writing Agent

Responsibilities:

- Outline
- Draft
- Preserve voice
- Integrate research
- Add citations

### QA Agent

Responsibilities:

- Fact-check
- Validate citations
- Check voice
- Check guardrails
- Detect unsupported claims

---

# 20. Cost Optimization

Suppose one user speaks for 15 minutes and creates a 2,000-word article.

Potential workflow:

```text
15 minutes audio
       ↓
20 fragments
       ↓
20 fragment analyses
       ↓
5 research queries
       ↓
20 web pages
       ↓
1 research synthesis
       ↓
1 outline
       ↓
1 draft
       ↓
1 QA pass
```

The biggest cost-control opportunities are:

### 1. Don't research everything

Only research claims that need evidence.

### 2. Don't use expensive reasoning models for extraction

Use cheaper models for:

- Classification
- Sentiment
- Summaries
- Structured extraction

### 3. Cache research

If ten users ask:

> “Does AI improve developer productivity?”

don't perform ten identical searches.

Cache research results for a configurable period.

### 4. Deduplicate searches

Normalize research questions:

```text
"Does AI make developers faster?"
"Does AI improve programmer productivity?"
"Are AI coding assistants productive?"
```

These may represent essentially the same research question.

### 5. Use deep research selectively

Normal search should be the default.

Deep research should be triggered by:

- Complex topic
- Conflicting evidence
- User request
- High research confidence requirement
- Controversial claim

---

# 21. MVP Development Plan

## Phase 1 — Voice to Blog

Build:

```text
Voice
 ↓
Transcription
 ↓
Fragments
 ↓
Blog State
 ↓
Blog Generation
```

No sophisticated research initially.

Goal:

> Determine whether users enjoy thinking aloud and receiving a coherent article.

---

## Phase 2 — Research Intelligence

Add:

```text
Sentiment
Claim extraction
Research questions
Web search
Source evaluation
Citations
Fact checking
```

Now the product becomes:

> **Speak your thoughts → AI researches them → AI writes your article.**

---

## Phase 3 — Personal Voice

Add:

```text
Writing style
Vocabulary
Preferred sources
Recurring topics
Formatting preferences
Audience preferences
Banned topics
Personal opinions
```

Eventually the system can learn:

> “This is how the user writes.”

rather than producing generic AI prose.

---

# 22. Cost-Effective Tool Strategy

## Speech-to-text

Start with:

**GPT-4o Mini Transcribe**

Use a higher-quality transcription model only if real-world testing shows the cheaper model is insufficient.

## Search

Start with:

**Tavily**

Use normal search by default.

## Advanced research

Add:

**Exa Agent** or **Tavily Research**

only for difficult research.

## LLM

Benchmark at least two inexpensive models.

A practical architecture is:

```text
Cheap model
   ↓
~90% of operations

Strong reasoning model
   ↓
~10% difficult operations
```

## Storage

Start with:

**Cloudflare R2**

Keep audio files separate from database records.

## Database

Start with:

**PostgreSQL + pgvector**

This avoids introducing a separate vector database before you need one.

## Hosting

Start with:

```text
Vercel
+
Railway / Render
+
Cloudflare R2
```

Keep the infrastructure simple until usage justifies a more complex architecture.

---

# 23. Important Product Principles

### Principle 1 — Preserve the user's position

AI should improve the expression of an idea, not silently replace the idea.

### Principle 2 — Separate user content from AI content

Internally distinguish:

```text
USER_SAID
USER_OPINION
USER_EXPERIENCE
AI_INFERENCE
RESEARCH_FACT
AI_GENERATED
```

This dramatically improves traceability.

### Principle 3 — Research should augment, not dominate

The final blog should still feel like the user's article.

Research provides:

- Context
- Evidence
- Counterarguments
- Statistics
- Background

It shouldn't drown out the user's voice.

### Principle 4 — Confidence matters

For important claims, store:

```text
claim
evidence
source
confidence
```

### Principle 5 — Every generated claim should have an origin

Ideally, the system can answer:

> “Where did this sentence come from?”

with:

```text
User fragment
OR
Research source
OR
AI synthesis
```

---

# 24. Killer Feature

The core experience should be:

> **“Talk to your blog.”**

The user doesn't need to think about:

- Structure
- Grammar
- Transitions
- Research
- Citations
- SEO
- Outlining

They simply talk.

The AI handles the transformation:

```text
Messy thoughts
      ↓
Structured ideas
      ↓
Research
      ↓
Argument
      ↓
Outline
      ↓
Article
```

The most compelling version of the product is therefore not:

> “AI speech-to-text blogging.”

It is:

> **An AI thinking partner that turns your spoken thoughts into researched writing while preserving your voice and point of view.**
