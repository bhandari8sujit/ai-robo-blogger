from typing import Any, TypedDict


class BlogPipelineState(TypedDict):
    # TypedDict describes required dictionary keys to type checkers without creating a runtime class.
    blog_id: str
    fragment_id: str
    transcript: str | None
    fragment_analysis: dict[str, Any] | None
    blog_brain: dict[str, Any]
    research_queue_delta: list[dict[str, Any]]
    research_findings_delta: list[dict[str, Any]]
    draft_delta: dict[str, Any] | None
    qa_result: dict[str, Any] | None
    errors: list[str]
