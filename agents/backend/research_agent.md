# Backend Agent: Research Agent

## Purpose
Collect and synthesize external evidence for queued research questions.

## Providers
- Tavily (default)
- Optional deep mode provider for complex/conflicting topics

## Harness
- LangChain tool-calling agent
- Source evaluator sub-chain
- Evidence synthesizer chain

## Responsibilities
- Generate optimized search queries.
- Retrieve candidate sources.
- Evaluate source quality and relevance.
- Extract supporting/contradicting evidence.
- Produce structured finding summaries.

## Inputs
- Canonical research question
- Optional deep-research flag
- Existing source cache

## Outputs
- `sources[]`
- `evidence[]`
- `research_summary`
- `strength` and `confidence`
- contradiction map

## Source Evaluation Heuristics
- Credibility and authority.
- Recency.
- Topical relevance.
- Primary vs secondary evidence.
- Cross-source consistency.

## Failure Handling
- Search provider failure -> retry and fallback query strategy.
- Thin evidence set -> mark as `insufficient_evidence` and avoid overclaiming.
