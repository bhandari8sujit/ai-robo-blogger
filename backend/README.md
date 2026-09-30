# Robo Blog Backend

FastAPI backend implementing the voice-fragment to researched-draft workflow.

## Run (development)

Copy `.env.example` to `.env`, then generate a local JWT signing key:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Set the result as `JWT_SECRET_KEY` in `.env`, start PostgreSQL, install the dependencies, and start the API:

```powershell
docker compose up -d postgres
uv sync --extra dev
uv run fastapi dev
```

To create test users, run:

```powershell
uv run python -m scripts.seed_users
```

## API

- `/healthz` reports application health.
- `/auth/register` accepts an email and password as JSON.
- `/auth/token` accepts OAuth2 form fields (`username` contains the email) and returns a bearer token.
- `/auth/me` returns the authenticated user.
- `/blogs` creates and reads blogs, fragments, state, research, and timelines.
- `/fragments` processes uploaded voice fragments.
- `/drafts` exposes validation, revision, sources, and sentence provenance.

Read endpoints are public. Mutation endpoints require `Authorization: Bearer <token>` and verify ownership.

## Incremental branches

The backend is implemented as six cumulative checkpoints:

1. `rebuild/01-authentication` - application foundation and authentication
2. `rebuild/02-blog-state` - blogs, guardrails, and versioned Blog Brain state
3. `rebuild/03-fragment-understanding` - audio, transcription, analysis, and claims
4. `rebuild/04-research` - selective research, sources, and evidence
5. `rebuild/05-drafting-qa` - drafting, provenance, revision, and QA
6. `rebuild/06-orchestration-events` - end-to-end processing, timeline, and SSE

Each branch starts from the preceding checkpoint, so it can be read and tested before moving forward.
