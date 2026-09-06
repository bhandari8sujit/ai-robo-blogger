# Backend Agent: Research Planner Agent

## Purpose
Determine which extracted claims require external verification and create a cost-aware research queue.

## Harness
- LangChain classifier chain with strict schema output

## Responsibilities
- Review claims from fragment analysis.
- Decide `requires_research` vs `personal_opinion` vs `personal_experience`.
- Normalize similar questions to reduce duplicate searches.
- Prioritize queue by impact and uncertainty.

## Inputs
- Claims list
- Existing open research questions
- Cached prior findings index

## Outputs
- `research_queue_delta`
- Canonicalized research questions
- Priority score per question

## Rules
- Research only externally verifiable factual claims.
- Skip claims already sufficiently supported by recent high-quality evidence.
- Route high-ambiguity questions to deep-research mode when needed.

## Failure Handling
- Ambiguous classification -> mark `needs_human_review` or low-confidence auto path.
