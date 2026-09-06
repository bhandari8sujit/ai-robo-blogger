from typing import Any
from urllib.parse import urlparse

from app.core.config import settings


class ResearchAgent:
    def run(self, question: str, deep: bool = False) -> dict[str, Any]:
    # A default argument supplies the normal shallow-search behavior when omitted.
        if not settings.tavily_api_key:
            return self._insufficient("TAVILY_API_KEY is not configured.")

        try:
            from tavily import TavilyClient

            response = TavilyClient(api_key=settings.tavily_api_key).search(
                query=question,
                search_depth="advanced" if deep else "basic",
                max_results=10 if deep else 5,
                include_raw_content="text" if deep else False,
            )
        except Exception as error:
            return self._insufficient(f"Research provider failed: {error}")

        sources: list[dict[str, Any]] = []
        evidence: list[dict[str, Any]] = []
        # dict.get with a default avoids a KeyError for incomplete provider payloads.
        for result in response.get("results", []):
            url = result.get("url", "")
            content = result.get("content", "").strip()
            if not url or not content:
                continue
            domain = urlparse(url).netloc.removeprefix("www.")
            sources.append(
                {
                    "title": result.get("title") or domain,
                    "url": url,
                    "publisher": domain,
                    "published_at": result.get("published_date"),
                    "credibility": self._credibility(domain),
                }
            )
            evidence.append({"supporting_text": content[:1_000], "confidence": self._credibility(domain)})

        if not sources:
            return self._insufficient("The research provider returned no usable evidence.")

        confidence = round(sum(item["confidence"] for item in evidence) / len(evidence), 2)
        return {
            "sources": sources,
            "evidence": evidence,
            "research_summary": "Evidence was retrieved for review; conclusions should reflect source caveats.",
            "strength": "strong" if len(sources) >= 3 and confidence >= 0.75 else "moderate",
            "confidence": confidence,
            "contradictions": [],
            "status": "completed",
        }

    @staticmethod
    def _credibility(domain: str) -> float:
        # Static helpers are namespaced on the class but do not receive `self`.
        if domain.endswith((".gov", ".edu")):
            return 0.9
        if domain in {"arxiv.org", "nature.com", "science.org", "acm.org", "ieee.org"}:
            return 0.85
        return 0.65

    @staticmethod
    def _insufficient(reason: str) -> dict[str, Any]:
        # Returning a uniform shape lets callers avoid special-case error handling.
        return {
            "sources": [],
            "evidence": [],
            "research_summary": reason,
            "strength": "insufficient_evidence",
            "confidence": 0.0,
            "contradictions": [],
            "status": "insufficient_evidence",
        }
