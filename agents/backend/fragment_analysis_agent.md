# Backend Agent: Fragment Analysis Agent

## Purpose
Transform raw transcript text into structured semantic artifacts for downstream planning.

## Harness
- LangChain structured-output chain (Pydantic schema)
- Low-cost LLM for extraction/classification

## Responsibilities
- Extract summary, topics, claims, questions.
- Classify sentiment and user intent.
- Tag personal experiences vs externally verifiable claims.

## Input
- `transcript`
- Optional prior context (last N fragments)

## Output Schema
- `summary: str`
- `topics: list[str]`
- `claims: list[{text, requires_research, confidence}]`
- `questions: list[str]`
- `personal_experiences: list[str]`
- `sentiment: {primary, secondary, intensity}`
- `intent: str`

## Quality Rules
- Avoid speculative claim inflation.
- Keep extraction faithful to user wording.
- Mark uncertainty explicitly when ambiguous.

## Failure Handling
- Invalid JSON output -> automatic parser retry.
- Persistent schema mismatch -> fallback safe extraction mode.
