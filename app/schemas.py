from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal


# ---------------------------------------------------------------------------- #
#                                     TOKEN                                    #
# ---------------------------------------------------------------------------- #
class TokenResponse(BaseModel):
    token: str


# ---------------------------------------------------------------------------- #
#                                     USER                                     #
# ---------------------------------------------------------------------------- #
class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str = Field(..., min_length=8, max_length=72)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------- #
#                                     BLOG                                     #
# ---------------------------------------------------------------------------- #
class BlogCreate(BaseModel):
    title: str
    content: str
    published: bool = False


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


class BlogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    published: bool
    author: UserResponse
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------- #
#                                    ISSUES                                    #
# ---------------------------------------------------------------------------- #
type Priority = Literal["low"] | Literal["medium"] | Literal["high"]
type Status = Literal["open"] | Literal["closed"]


class IssueCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=5)
    priority: Priority


class IssueUpdate(BaseModel):
    title: Optional[str] = Field(min_length=3, max_length=100)
    content: Optional[str] = Field(min_length=5)

    priority: Optional[Priority]
    status: Optional[Status]


class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str

    author_id: UUID

    priority: Priority
    status: Status

    created_at: datetime
    updated_at: datetime
