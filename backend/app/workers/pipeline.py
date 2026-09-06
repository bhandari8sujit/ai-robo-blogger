from typing import Any


class LangGraphPipelineHarness:
    """Minimal LangGraph harness placeholder with deterministic fallback.

    The orchestration service executes nodes directly for reliability.
    This class documents the intended graph integration point.
    """

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        # This pass-through preserves the mutable dictionary contract until LangGraph nodes are wired in.
        return state
