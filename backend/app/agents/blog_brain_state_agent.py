from datetime import datetime, UTC
from typing import Any

from pydantic import BaseModel, Field

from app.agents.llm import run_structured_prompt


class BlogBrainMerge(BaseModel):
    thesis: str = ""
    # `default_factory` prevents mutable lists from being shared across model instances.
    arguments: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    contradictions: int = Field(default=0, ge=0)


class BlogBrainStateAgent:
    def run(self, current_brain: dict[str, Any], analysis: dict[str, Any], guardrails: dict[str, Any]) -> dict[str, Any]:
    # The typed return signals a JSON-compatible payload, while Pydantic validates LLM output.
        prompt = f"""Merge a new spoken-fragment analysis into a compact blog state.
Prefer explicit user statements, preserve contradictory statements, and do not introduce new positions.
Return a thesis, arguments, open questions, and contradiction count.

Current state: {current_brain}
New analysis: {analysis}
Guardrails: {guardrails}
"""
        try:
            merged = run_structured_prompt(BlogBrainMerge, prompt)
        except Exception:
            # Provider failures intentionally fall through to deterministic local merge logic.
            merged = None

        thesis = (merged.thesis if merged else current_brain.get("thesis")) or analysis["summary"]

        arguments = list(merged.arguments if merged else current_brain.get("arguments", []))
        if not merged and analysis["summary"] and analysis["summary"] not in arguments:
            arguments.append(analysis["summary"])

        open_questions = list(merged.open_questions if merged else current_brain.get("open_questions", []))
        if not merged:
            for question in analysis["questions"]:
                if question not in open_questions:
                    open_questions.append(question)

        contradictions = merged.contradictions if merged else current_brain.get("contradictions", 0)
        if not merged and analysis["intent"] == "revision":
            contradictions += 1

        provenance = dict(current_brain.get("provenance", {}))
        provenance.update(
            {
                "thesis": {"origin_type": "AI_INFERENCE", "confidence": 0.75},
                "arguments": {"origin_type": "USER_SAID", "confidence": 0.8},
                "open_questions": {"origin_type": "USER_SAID", "confidence": 0.8},
            }
        )

        return {
            "thesis": thesis,
            # Negative slicing retains only the latest values and safely handles short lists.
            "arguments": arguments[-8:],
            "sentiment": analysis["sentiment"],
            "intent": analysis["intent"],
            "open_questions": open_questions[-10:],
            "contradictions": contradictions,
            "guardrails": guardrails,
            "provenance": provenance,
            "updated_at": datetime.now(UTC).isoformat(),
        }
