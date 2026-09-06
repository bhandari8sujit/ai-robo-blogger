from typing import Any

from pydantic import BaseModel, Field

from app.agents.llm import run_structured_prompt


class ExtractedClaim(BaseModel):
    text: str
    requires_research: bool
    # Field constraints are validated by Pydantic at runtime, not merely by static typing.
    confidence: float = Field(ge=0, le=1)


class FragmentAnalysis(BaseModel):
    summary: str
    topics: list[str] = Field(default_factory=list)
    claims: list[ExtractedClaim] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    personal_experiences: list[str] = Field(default_factory=list)
    sentiment: dict[str, Any]
    intent: str


class FragmentAnalysisAgent:
    def run(self, transcript: str, prior_context: list[str] | None = None) -> dict[str, Any]:
    # `None` distinguishes omitted context from an intentionally empty list.
        text = transcript.strip()
        if not text:
            return self._fallback(text)

        context = "\n".join(prior_context or [])
        prompt = f"""Extract only information explicitly supported by this spoken blog fragment.
Do not strengthen claims. Mark personal experiences separately, and mark only externally verifiable
claims as requiring research. Use one of exploration, revision, argument, anecdote, or question for intent.

Prior context:
{context or "None"}

Fragment:
{text}
"""
        try:
            result = run_structured_prompt(FragmentAnalysis, prompt)
        except Exception:
            result = None
        if result is not None:
            # `model_dump()` converts a Pydantic model into ordinary nested Python dictionaries.
            return result.model_dump()

        return self._fallback(text)

    @staticmethod
    def _fallback(text: str) -> dict[str, Any]:
        # A static method needs no instance state; it keeps the offline fallback deterministic.
        lower = text.lower()

        intent = "exploration"
        if "disagree" in lower or "change" in lower:
            intent = "revision"

        requires_research = any(token in lower for token in ["study", "data", "percent", "research", "evidence"])

        claims = []
        if text:
            claims.append(
                {
                    "text": text,
                    "requires_research": requires_research,
                    "confidence": 0.72 if requires_research else 0.62,
                }
            )

        questions = []
        if "?" in text:
            questions.append(text)

        return {
            "summary": text[:220],
            "topics": ["ai", "blogging"] if "ai" in lower else ["blogging"],
            "claims": claims,
            "questions": questions,
            "personal_experiences": [text] if "i " in lower or "my " in lower else [],
            "sentiment": {
                "primary": "curious" if "?" in text else "reflective",
                "secondary": "skeptical" if "not" in lower or "disagree" in lower else None,
                "intensity": 0.6,
            },
            "intent": intent,
        }
