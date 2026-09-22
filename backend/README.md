# Robo Blog Backend

FastAPI backend implementing the voice-fragment to researched draft workflow.

## Run (development)

Copy `.env.example` to `.env`, then generate a local JWT signing key:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Set the result as `JWT_SECRET_KEY` in `.env`, install the dependencies, and start the API:

```bash
fastapi dev
```

## Main API groups

- `/blogs`
- `/fragments`
- `/drafts`
- `/auth/register` accepts an email and password as JSON.
- `/auth/token` accepts OAuth2 form fields (`username` contains the email) and returns a bearer token.
- `/auth/me` returns the authenticated user.

All mutation endpoints require `Authorization: Bearer <token>`. Read endpoints remain public.

## Notes

- The codebase is structured to match the component agent specs in `agents/backend`.
- LangChain/LangGraph harness is implemented with a safe local fallback path.
