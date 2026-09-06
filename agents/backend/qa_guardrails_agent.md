# Backend Agent: QA and Guardrails Agent

## Purpose
Validate factual grounding, voice fidelity, and policy guardrails before a draft is considered publish-ready.

## Harness
- LangChain validation chain with structured issue reporting

## Responsibilities
- Detect unsupported claims.
- Check citation coverage and source alignment.
- Measure voice drift from user fragments.
- Validate tone, length, and banned-topic constraints.
- Flag contradictory conclusions not addressed in text.

## Inputs
- Draft content
- Blog brain snapshot
- Source and evidence graph
- Guardrails config

## Outputs
- `passed: bool`
- `issues[]` with severity and remediation hints
- `voice_score`
- `factuality_score`

## Issue Types
- `unsupported_claim`
- `citation_mismatch`
- `voice_drift`
- `stance_shift`
- `guardrail_violation`
- `consistency_error`

## Failure Handling
- If severe factual issues exist, set `publish_blocked=true`.
- Route actionable issues to revision workflow with targeted prompts.
