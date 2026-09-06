from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session

# `Annotated` attaches FastAPI dependency metadata without changing the runtime Session value.
DbSession = Annotated[Session, Depends(get_session)]


def get_current_user_id() -> str:
    # This provider is replaceable in tests and when real authentication is added.
    return settings.default_user_id


# Route parameters typed as this alias receive the dependency result instead of client input.
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
