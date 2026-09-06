from typing import TypeVar

from pydantic import BaseModel

from app.core.config import settings


# A bounded TypeVar preserves the specific Pydantic model type passed to this generic helper.
StructuredOutput = TypeVar("StructuredOutput", bound=BaseModel)


def run_structured_prompt(
    schema: type[StructuredOutput],
    prompt: str,
    *,
    strong_reasoning: bool = False,
) -> StructuredOutput | None:
    """Run a schema-constrained prompt when an OpenAI key is configured."""
    # `None` is the explicit no-provider result, letting callers use deterministic fallbacks.
    if not settings.openai_api_key:
        return None

    # Lazy import avoids loading the optional provider package when fallback mode is active.
    from langchain_openai import ChatOpenAI

    model = settings.llm_strong_model if strong_reasoning else settings.llm_model
    llm = ChatOpenAI(
        model=model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        temperature=0,
    )
    # The schema asks LangChain to parse and validate the model response into that Pydantic type.
    return llm.with_structured_output(schema).invoke(prompt)