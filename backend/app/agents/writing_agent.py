from datetime import datetime, UTC
from typing import Any

from pydantic import BaseModel, Field

from app.agents.llm import run_structured_prompt


class DraftGeneration(BaseModel):
    draft_content: str
    provenance_map: dict[str, dict[str, str]] = Field(default_factory=dict)


class WritingAgent:
    def run(
        self,
        blog_title: str,
        blog_brain: dict[str, Any],
        findings: list[dict[str, Any]],
        prior_draft: str | None,
    ) -> dict[str, Any]:
        # `any` consumes the generator lazily and stops after the first strong finding.
        has_complex_research = any(finding.get("strength") == "strong" for finding in findings)
        prompt = f"""Write a blog draft that preserves the user's position and personal voice.
Do not state uncertain research as fact. Cite externally sourced claims inline as [n], and include a Sources section
with URLs. Keep opinions distinct from evidence.

Title: {blog_title}
Blog brain: {blog_brain}
Research findings: {findings}
Prior draft: {prior_draft or "None"}
"""
        try:
            generated = run_structured_prompt(DraftGeneration, prompt, strong_reasoning=has_complex_research)
        except Exception:
            generated = None
        if generated is not None:
            # `**` copies model fields into a new dictionary before adding the timestamp.
            return {**generated.model_dump(), "generated_at": datetime.now(UTC).isoformat()}

        thesis = blog_brain.get("thesis") or "This article explores an evolving perspective."
        arguments = blog_brain.get("arguments", [])
        sentiment = blog_brain.get("sentiment", {}).get("primary", "reflective")

        source_lines: list[str] = []
        # `enumerate(..., start=1)` provides one-based source labels without a manual counter.
        for idx, finding in enumerate(findings, start=1):
            for source in finding.get("sources", []):
                source_lines.append(f"[{idx}] {source['title']} - {source['url']}")

        body = [
            f"# {blog_title}",
            "",
            f"Thesis: {thesis}",
            "",
            "Key points:",
        ]
        body.extend([f"- {argument}" for argument in arguments[-5:]])

        if source_lines:
            body.extend(["", "Sources:"] + source_lines)

        body.extend(
            [
                "",
                f"Tone target: {sentiment}.",
                "",
                "This draft is incremental and should be refined with additional fragments.",
            ]
        )

        content = "\n".join(body)
        if prior_draft:
            content = f"{content}\n\nUpdate note: integrated new fragment context."

        return {
            "draft_content": content,
            "provenance_map": {
                "s_1": {"origin": "AI_GENERATED", "basis": "blog_brain"},
                "s_2": {"origin": "RESEARCH_FACT", "basis": "sources"},
            },
            "generated_at": datetime.now(UTC).isoformat(),
        }
