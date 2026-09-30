from types import SimpleNamespace

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.agents.research_agent import ResearchAgent
from app.agents.research_planner_agent import ResearchPlannerAgent
from app.models import Evidence
from app.repositories.blog_repository import BlogRepository
from app.services.orchestration_service import OrchestrationService


def test_research_planner_deduplicates_questions(monkeypatch) -> None:
    monkeypatch.setattr("app.agents.research_planner_agent.run_structured_prompt", lambda *_args, **_kwargs: None)
    claim = {"text": "AI improves productivity", "requires_research": True, "confidence": 0.6}
    question = "What evidence supports: AI improves productivity"
    assert ResearchPlannerAgent().run([claim], [question]) == []


def test_research_without_provider_is_explicit(monkeypatch) -> None:
    monkeypatch.setattr("app.agents.research_agent.settings", SimpleNamespace(tavily_api_key=None))
    finding = ResearchAgent().run("Does this claim have evidence?")
    assert finding["status"] == "insufficient_evidence"
    assert finding["sources"] == []


def test_research_rerun_does_not_duplicate_sources_or_evidence() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        repo = BlogRepository(session)
        blog = repo.create_blog("owner", "Evidence")
        claim = repo.upsert_claims(blog.id, [{"text": "AI improves productivity", "requires_research": True}])[0]
        repo.create_research_questions(blog.id, [{"question": "What evidence supports: AI improves productivity"}])

        finding = {
            "sources": [{"title": "Study", "url": "https://example.edu/study", "credibility": 0.9}],
            "evidence": [{"source_url": "https://example.edu/study", "supporting_text": "Measured improvement.", "confidence": 0.9}],
            "status": "completed",
        }
        service = OrchestrationService(session)
        service.research_agent = SimpleNamespace(run=lambda *_args, **_kwargs: finding)
        assert service.run_research(blog.id) == 1

        question = repo.list_research_questions(blog.id)[0]
        question.status = "pending"
        session.add(question)
        session.commit()
        assert service.run_research(blog.id) == 1

        assert len(repo.list_sources(blog.id)) == 1
        evidence = list(session.exec(select(Evidence).where(Evidence.claim_id == claim.id)))
        assert len(evidence) == 1
