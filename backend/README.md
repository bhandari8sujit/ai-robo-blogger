# Robo Blog Backend

FastAPI backend implementing the voice-fragment to researched draft workflow.

## Run (development)

```bash
fastapi dev
```

## Main API groups

- `/blogs`
- `/fragments`
- `/drafts`

## Notes

- The codebase is structured to match the component agent specs in `agents/backend`.
- LangChain/LangGraph harness is implemented with a safe local fallback path.
