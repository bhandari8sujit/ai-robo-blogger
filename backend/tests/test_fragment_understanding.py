from pathlib import Path
from types import SimpleNamespace
import asyncio

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.agents.fragment_analysis_agent import FragmentAnalysisAgent
from app.models import Draft
from app.repositories.blog_repository import BlogRepository
from app.services.orchestration_service import OrchestrationService
from app.services.storage_service import StorageService


def _repository() -> tuple[BlogRepository, Session]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    return BlogRepository(session), session


def test_storage_and_offline_analysis(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("app.agents.fragment_analysis_agent.run_structured_prompt", lambda *_args, **_kwargs: None)
    storage = StorageService()
    storage.base_dir = tmp_path
    audio_url, duration = storage.save_audio("blog-1", b"voice bytes", ".webm")

    assert Path(audio_url).read_bytes() == b"voice bytes"
    assert duration >= 0

    analysis = FragmentAnalysisAgent().run("I think research shows AI changes programming.")
    assert analysis["intent"] == "exploration"
    assert analysis["claims"][0]["requires_research"] is True


def test_processing_updates_brain_and_deduplicates_claims(monkeypatch) -> None:
    monkeypatch.setattr("app.agents.fragment_analysis_agent.run_structured_prompt", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("app.agents.blog_brain_state_agent.run_structured_prompt", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("app.agents.research_planner_agent.run_structured_prompt", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("app.agents.research_agent.settings", SimpleNamespace(tavily_api_key=None))
    monkeypatch.setattr("app.agents.writing_agent.run_structured_prompt", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("app.agents.qa_guardrails_agent.run_structured_prompt", lambda *_args, **_kwargs: None)
    repo, session = _repository()
    try:
        blog = repo.create_blog("owner", "AI and programming")
        first = repo.create_fragment(blog.id, "unused.webm", 1.0, "Research shows AI changes programming.")
        second = repo.create_fragment(blog.id, "unused.webm", 1.0, "  research shows AI changes programming!  ")

        service = OrchestrationService(session)
        assert asyncio.run(service.process_fragment(first.id)) == "validated"
        assert asyncio.run(service.process_fragment(second.id)) == "validated"
        draft_count = len(list(session.exec(select(Draft).where(Draft.blog_id == blog.id))))
        assert asyncio.run(service.process_fragment(first.id)) == "validated"

        assert len(repo.list_claims(blog.id)) == 1
        assert repo.get_latest_blog_brain(blog.id).version == 3
        assert len(list(session.exec(select(Draft).where(Draft.blog_id == blog.id)))) == draft_count
        assert [event.event_type for event in repo.timeline(blog.id)][:2] == [
            "fragment.received",
            "fragment.analyzed",
        ]
    finally:
        session.close()
