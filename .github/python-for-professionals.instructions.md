---
applyTo: "**/*.py"
---

# Python for Professionals Guidance

Use this guidance for Python code, with the course's examples and practices adapted to the repository's existing architecture and tooling.

## Project Setup

- Use `uv` for Python project and dependency management.
- Keep runtime dependencies separate from development dependencies: use `uv add` for runtime packages and `uv add --dev` for tools such as Ruff, mypy, pytest, and coverage.
- Keep project configuration in `pyproject.toml`; commit the lockfile when the repository uses one.
- Use a project-local virtual environment and run project commands through `uv run` so local and CI environments resolve the same dependencies.
- Keep `.env` files out of version control. Document required variable names without committing values.
- Prefer a reproducible, explicit setup over relying on globally installed Python packages.

## Python Design

- Write clear, small functions with explicit inputs and return types.
- Prefer descriptive names and keyword-only arguments when an argument's meaning matters.
- Use standard-library types and modules before adding dependencies.
- Use `Enum` for finite domain values rather than scattering string literals.
- Use comprehensions for straightforward transformations, but use ordinary loops when they make control flow or error handling clearer.
- Use dataclasses or focused classes for structured state; keep responsibilities narrow.
- Raise specific exceptions for exceptional conditions. Do not use bare `except` blocks or silently swallow errors.
- Preserve the original exception context when translating errors with `raise ... from ...`.
- Use context managers for resources that must be acquired and released reliably.
- Use decorators only when they express a reusable cross-cutting concern and preserve the wrapped function's metadata.

## Types and Validation

- Add type hints to public functions, methods, settings, models, and non-obvious values.
- Treat static type checking as a design aid: resolve type errors instead of weakening checks with broad `Any` or unnecessary ignores.
- Use Pydantic models at input boundaries to validate external data and make accepted data explicit.
- Keep validation separate from business logic where possible.
- Use `SecretStr` or an equivalent secret-aware type for sensitive settings so values are masked in representations and logs.
- Make required security settings fail fast at startup rather than providing unsafe defaults.

## Testing

- Use pytest with small, behavior-focused tests.
- Test both successful behavior and important failure paths, including invalid input, missing records, authorization failures, and database errors.
- Use fixtures to share setup and isolate database state; avoid tests that depend on execution order or an external shared database.
- For API code, test through the HTTP boundary when verifying routing, validation, status codes, and serialized responses.
- Use parametrization for the same behavior across several inputs.
- Treat coverage as a gap-finding tool, not a proxy for test quality. Branch coverage is useful for conditional behavior, but every test should assert meaningful outcomes.

## FastAPI

- Keep route handlers thin: validate input, call the application/data layer, and translate the result into an HTTP response.
- Use Pydantic request and response models instead of accepting or returning unstructured dictionaries at API boundaries.
- Choose `async def` when the endpoint and its dependencies perform non-blocking async I/O; use synchronous handlers for synchronous libraries. Do not make an endpoint async merely for appearance.
- Declare path, query, and body parameters explicitly and validate constraints at the boundary.
- Return deliberate status codes and response shapes. Do not expose internal ORM objects or database errors accidentally.
- Use `APIRouter` to group related routes and keep the application entry point small.
- Use FastAPI dependency injection for shared concerns such as database sessions, authenticated users, and reusable query parameters.
- Prefer `Annotated` aliases for dependencies when they reduce repetition and make handler signatures readable.
- Centralize exception handling for domain errors and map them to stable, documented HTTP responses.
- Keep OpenAPI documentation accurate through route metadata, typed parameters, and response models.
- Add a health endpoint that checks application availability without exposing secrets or unnecessary internals.

## Database and SQLModel

- Keep database models, relationships, and constraints explicit. Define foreign keys and indexes deliberately.
- Use a session per request or operation and ensure it is closed reliably through dependency injection or a context manager.
- Keep database access out of presentation code and avoid leaking sessions beyond their intended scope.
- Use relational queries and filtering in the database rather than loading large collections and filtering them in Python.
- Handle missing records explicitly and translate them to the API's intended not-found behavior.
- Avoid N+1 query patterns; inspect relationship loading when an endpoint returns related data.
- Treat Alembic migrations as versioned production code. Generate migrations as a draft, review every column, type, nullability, constraint, index, and downgrade, then apply them.
- Verify the migration state with `uv run alembic current` and use `uv run alembic upgrade head` only after review.
- Never edit an already-applied migration for a shared environment; create a new migration instead.
- Ensure every model is imported into Alembic metadata so autogeneration can see it.

## Authentication and Security

- Hash passwords with a modern password-hashing library; never store plaintext or reversibly encrypted passwords.
- Use signed, expiring JWTs for stateless authentication only when that matches the application's requirements.
- Keep JWT signing secrets in environment-backed settings, require a sufficiently long secret, and never hardcode one.
- Put the user identity in a stable token claim such as `sub`; validate signature, algorithm, and expiration when decoding.
- Protect routes through a reusable authentication dependency rather than duplicating token parsing in handlers.
- Return generic authentication failures that do not reveal whether an account exists.
- Do not log passwords, tokens, signing keys, database credentials, or raw authorization headers.

## Logging and Middleware

- Use Python's `logging` module rather than `print` for application diagnostics.
- Configure logging once at the application boundary and use module-level loggers in application code.
- Log useful context, levels, and exceptions without including secrets or sensitive payloads.
- Use middleware for genuinely cross-cutting request concerns such as timing, correlation IDs, or safe request logging.
- Keep middleware order intentional and avoid putting business logic in middleware.

## Quality Gates and Delivery

Run the same checks locally and in CI, in a consistent order:

```shell
uv run ruff check --no-cache .
uv run ruff format --check .
uv run mypy .
uv run coverage run -m pytest
uv run coverage report
```

- Use `ruff check --fix` only for safe local fixes; CI should verify rather than silently rewrite code.
- Keep mypy configuration strict enough to catch incomplete definitions, implicit optional values, redundant casts, and unused ignores.
- Scope coverage to application code and enable branch coverage where conditional behavior matters.
- Use Docker for reproducible service environments; keep the production image focused on runtime dependencies and do not copy secrets into it.
- Add CI checks for linting, formatting, type checking, tests, and coverage.
- Use environment or platform secret management for deployed credentials; do not commit `.env` files or secrets in workflow files.

## Debugging Workflow

- Read the complete traceback, starting at the final exception and following the project frames back to the triggering input.
- Reproduce the smallest failing case, then inspect values and types at the boundary where assumptions diverge.
- Use VS Code's debugger for FastAPI request flows when logs are insufficient; keep breakpoints focused on route, dependency, and data-layer boundaries.
- After fixing a bug, add a regression test for the behavior before broadening the change.

Source: Python for Professionals course at https://python-pros.netlify.app/, including the introduction and chapters 1 through 12, accessed September 23, 2026.