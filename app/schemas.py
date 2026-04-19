from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from typing import TypeVar, Generic, Optional, Literal


# ---------------------------------------------------------------------------- #
#                                 ROUTER LEVEL                                 #
# ---------------------------------------------------------------------------- #
class BlogCreate(BaseModel):
    title: str
    content: str
    published: bool = False


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


# ----------------------------------- USER ----------------------------------- #
class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class LoginUser(BaseModel):
    email: str
    password: str = Field(..., min_length=8, max_length=72)


class TokenResponse(BaseModel):
    token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    created_at: datetime
    updated_at: datetime


class BlogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    published: bool
    author: UserResponse
    created_at: datetime
    updated_at: datetime
