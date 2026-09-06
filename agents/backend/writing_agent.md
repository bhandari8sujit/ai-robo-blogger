# Backend Agent: Writing Agent

## Purpose
Generate coherent blog sections and full drafts that preserve user voice while integrating verified research.

## Harness
- LangChain prompt-template chain
- Two-model policy:
  - low-cost model for routine drafting
  - stronger model only for complex synthesis paths

## Responsibilities
- Build/update outline from blog brain.
- Generate incremental section updates.
- Distinguish opinion vs fact in wording.
- Attach citations for externally sourced claims.

## Inputs
- Blog brain snapshot
- Research findings and evidence
- Guardrails
- Prior draft versions

## Outputs
- `draft_content`
- `draft_version`
- sentence/paragraph provenance map

## Guardrail Rules
- Do not shift user stance silently.
- Preserve user anecdotes and intent.
- Do not strengthen uncertain findings.
- Include caveats where evidence is mixed.

## Failure Handling
- Missing required citations -> block publish-ready status.
- Low confidence synthesis -> request deeper research node.
