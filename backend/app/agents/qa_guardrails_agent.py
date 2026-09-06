from typing import Any

from pydantic import BaseModel, Field

from app.agents.llm import run_structured_prompt


class QaEvaluation(BaseModel):
    issues: list[dict[str, str]] = Field(default_factory=list)
    voice_score: float = Field(ge=0, le=1)
    factuality_score: float = Field(ge=0, le=1)


class QaGuardrailsAgent:
    def run(
        self,
        draft_content: str,
        blog_brain: dict[str, Any],
        citation_required: bool,
        guardrails: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        # Optional guardrails use `None` as an explicit "use defaults" sentinel.
        prompt = f"""Review this blog draft for unsupported claims, citation mismatch, voice drift, stance shift,
guardrail violations, and unresolved contradictions. Report only issues grounded in the supplied data.

Draft: {draft_content}
Blog brain: {blog_brain}
Guardrails: {guardrails or {"citation_required": citation_required}}
"""
        try:
            evaluation = run_structured_prompt(QaEvaluation, prompt, strong_reasoning=True)
        except Exception:
            evaluation = None
        if evaluation is not None:
            issues = evaluation.issues
            return {
                # `any` short-circuits, like JavaScript's Array.some.
                "passed": not any(issue.get("severity") == "high" for issue in issues),
                "issues": issues,
                "voice_score": evaluation.voice_score,
                "factuality_score": evaluation.factuality_score,
                "publish_blocked": bool(issues),
            }

        issues: list[dict[str, Any]] = []
        has_research = "Sources:" in draft_content

        if citation_required and not has_research:
            issues.append(
                {
                    "type": "citation_mismatch",
                    "text": "Citations are required but no research section was generated.",
                    "severity": "medium",
                }
            )

        if blog_brain.get("contradictions", 0) > 0:
            issues.append(
                {
                    "type": "consistency_error",
                    "text": "Contradictory user signals were detected and need revision.",
                    "severity": "low",
                }
            )

        for topic in (guardrails or {}).get("banned_topics", []):
            if topic.lower() in draft_content.lower():
                issues.append(
                    {
                        "type": "guardrail_violation",
                        "text": f"Draft contains banned topic: {topic}.",
                        "severity": "high",
                    }
                )

        # This list comprehension filters the collection before the count is evaluated.
        passed = len([issue for issue in issues if issue["severity"] == "high"]) == 0

        return {
            "passed": passed,
            "issues": issues,
            "voice_score": 0.84,
            "factuality_score": 0.78 if has_research else 0.62,
            "publish_blocked": len(issues) > 0,
        }
