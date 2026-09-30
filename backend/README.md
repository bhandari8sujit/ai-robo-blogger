# Robo Blog Backend

Stage 1 of the incremental FastAPI backend rebuild. This checkpoint provides
application configuration, database setup, and JWT authentication.

## Run (development)

Copy `.env.example` to `.env`, then generate a local JWT signing key:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Set the result as `JWT_SECRET_KEY` in `.env`, install the dependencies, and start the API:

```powershell
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
