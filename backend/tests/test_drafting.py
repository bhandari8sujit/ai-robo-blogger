from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.repositories.blog_repository import BlogRepository
from app.services.orchestration_service import OrchestrationService


def test_draft_versions_qa_and_provenance_use_persisted_data(monkeypatch) -> None:
    monkeypatch.setattr("app.agents.writing_agent.run_structured_prompt", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("app.agents.qa_guardrails_agent.run_structured_prompt", lambda *_args, **_kwargs: None)
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        repo = BlogRepository(session)
        blog = repo.create_blog("owner", "A measured argument")
        claim = repo.upsert_claims(blog.id, [{"text": "Evidence matters", "requires_research": True}])[0]
        source = repo.add_source(blog.id, {"title": "Primary study", "url": "https://example.edu/study", "credibility": 0.9})
        repo.add_evidence(claim.id, source.id, "Measured improvement.", 0.9)

        service = OrchestrationService(session)
        first = service.generate_draft(blog.id)
        assert first is not None and first["version"] == 1
        revised = service.revise_draft(first["id"], "Clarify the conclusion")
        assert revised is not None and revised["version"] == 2

        qa = service.validate_draft(revised["id"])
        assert qa is not None
        why = service.sentence_why(first["id"], "s_2")
        assert why is not None
        assert why["source_evidence"][0]["sourceTitle"] == "Primary study"
        assert why["source_evidence"][0]["supportText"] == "Measured improvement."


def test_owned_draft_lookup_blocks_other_users() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        repo = BlogRepository(session)
        blog = repo.create_blog("owner", "Ownership")
        draft = repo.save_draft(blog.id, "Draft", {})
        assert repo.get_owned_draft(draft.id, "owner") is not None
        assert repo.get_owned_draft(draft.id, "other-user") is None
