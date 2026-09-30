from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ApiBaseModel(BaseModel):
    # Pydantic accepts both Python snake_case names and declared camelCase aliases as input.
    model_config = ConfigDict(populate_by_name=True)


class UserCreateRequest(ApiBaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(ApiBaseModel):
    id: str
    email: EmailStr
    is_active: bool = Field(alias="isActive")
    created_at: datetime = Field(alias="createdAt")


class TokenResponse(ApiBaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
