# Backend Agent: Blog Orchestrator Agent

## Purpose
Coordinate end-to-end fragment processing through LangChain/LangGraph and persist stage outputs.

## Harness
- LangChain + LangGraph
- FastAPI task trigger endpoints
- PostgreSQL-backed event/task tables

## Responsibilities
- Receive `fragment.received` event.
- Execute graph nodes in deterministic order.
- Apply conditional branches (research required vs not required).
- Persist results and emit status events for frontend.

## Graph Nodes
1. `transcribe_fragment`
2. `analyze_fragment`
3. `update_blog_brain`
4. `plan_research`
5. Branch:
   - if no pending claims -> `write_incremental`
   - else -> `run_research` -> `synthesize_research` -> `write_incremental`
6. `validate_guardrails`
7. `persist_and_publish_state`

## Input State
- `blog_id`
- `fragment_id`
- Current `blog_brain`
- Guardrails

## Output State
- Updated blog brain snapshot
- Draft delta/new version
- QA result object
- Processing event timeline entries

## Reliability
- Idempotency key per `fragment_id + node_name`.
- Retry transient node failures with capped attempts.
- Dead-letter entries for repeated hard failures.

## Notes
- Keep node contracts explicit with Pydantic schemas.
- Log prompt/template version used at each node.
