from typing import Any

from pydantic import BaseModel, Field

from app.agents.llm import run_structured_prompt


class ResearchQuestionPlan(BaseModel):
    question: str
    priority: str
    deep_research: bool = False
    needs_human_review: bool = False


class ResearchPlan(BaseModel):
    questions: list[ResearchQuestionPlan] = Field(default_factory=list)


class ResearchPlannerAgent:
    def run(
        self,
        claims: list[dict[str, Any]],
        existing_questions: list[str],
        cached_questions: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        # The optional cache participates in deduplication only when a caller supplies it.
        prompt = f"""Plan a cost-aware research queue for factual claims only.
Deduplicate against existing and cached questions. Assign high, medium, or low priority and enable deep research
only for ambiguous or conflicting questions. Return no question for personal opinions or experiences.

Claims: {claims}
Existing questions: {existing_questions}
Cached questions: {cached_questions or []}
"""
        try:
            planned = run_structured_prompt(ResearchPlan, prompt)
        except Exception:
            planned = None
        if planned is not None:
            # A list comprehension serializes each validated Pydantic item to a plain dict.
            return [question.model_dump() for question in planned.questions]

        output: list[dict[str, Any]] = []
        # A set comprehension gives O(1)-average duplicate checks after canonicalizing text.
        normalized = {question.lower().strip() for question in existing_questions + (cached_questions or [])}

        for claim in claims:
            if not claim.get("requires_research", False):
                continue
            canonical = f"What evidence supports: {claim['text']}"
            key = canonical.lower().strip()
            if key in normalized:
                continue
            normalized.add(key)
            output.append(
                {
                    "question": canonical,
                    "priority": "high" if claim.get("confidence", 0.5) < 0.65 else "medium",
                    "deep_research": claim.get("confidence", 0.5) < 0.5,
                    "needs_human_review": claim.get("confidence", 0.5) < 0.4,
                }
            )

        return output
