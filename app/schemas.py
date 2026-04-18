from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from typing import TypeVar, Generic, Optional, Literal


# ---------------------------------------------------------------------------- #
#                                 ROUTER LEVEL                                 #
# ---------------------------------------------------------------------------- #
class BlogCreate(BaseModel):
    title: str
    content: str
    published: bool = False


class BlogUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    published: Optional[bool]


class BlogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    published: bool
    created_at: datetime
    updated_at: datetime


# ----------------------------------- USER ----------------------------------- #
class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class LoginUser(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    created_at: datetime
    updated_at: datetime


T = TypeVar("T")


# ---------------------------------------------------------------------------- #
#                                   API LEVEL                                  #
# ---------------------------------------------------------------------------- #
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str]
