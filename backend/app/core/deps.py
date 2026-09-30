from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.database import get_session
from app.security import get_current_user
from app.models import User

# `Annotated` attaches FastAPI dependency metadata without changing the runtime Session value.
DbSession = Annotated[Session, Depends(get_session)]


CurrentUser = Annotated[User, Depends(get_current_user)]


# Route parameters typed as this alias receive the dependency result instead of client input.
def get_current_user_id(current_user: CurrentUser) -> str:
    return current_user.id


CurrentUserId = Annotated[str, Depends(get_current_user_id)]
