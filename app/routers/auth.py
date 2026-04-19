from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Literal

from app.dependencies.auth import get_current_user
from app.schemas import LoginUser, TokenResponse, UserCreate, UserResponse, UserUpdate
from app.config.database import get_db, User
from app.services import JWTService

router = APIRouter(tags=["auth"])


# ---------------------------------------------------------------------------- #
#                                CREATE NEW USER                               #
# ---------------------------------------------------------------------------- #
@router.post("/signup", status_code=201)
async def signup(
    fields: UserCreate, session: AsyncSession = Depends(get_db)
) -> TokenResponse:
    new_user = User(**fields.model_dump())

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    token = JWTService.issue_token(new_user.id)
    return TokenResponse(token=token)


# ---------------------------------------------------------------------------- #
#                            LOGIN USING CREDENTIALS                           #
# ---------------------------------------------------------------------------- #
@router.post("/login")
async def login(fields: LoginUser, session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(User).where(User.email == fields.email).limit(1)
    )
    user = result.scalar_one_or_none()

    if not user or not user.verify_password(fields.password):
        raise HTTPException(401, "Invalid credentials")

    token = JWTService.issue_token(user.id)
    return TokenResponse(token=token)


# ---------------------------------------------------------------------------- #
#                                  ISSUE TOKEN                                 #
# ---------------------------------------------------------------------------- #
@router.get("/session")
async def new_token(user: User = Depends(get_current_user)) -> TokenResponse:
    return TokenResponse(token=JWTService.issue_token(user.id))


# ---------------------------------------------------------------------------- #
#                                  GET PROFILE                                 #
# ---------------------------------------------------------------------------- #
@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------- #
#                                 UPDATE PROFILE                               #
# ---------------------------------------------------------------------------- #
@router.patch("/profile")
async def update_profile(
    fields: UserUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UserResponse:
    update_data = fields.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)

    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------- #
#                               DELETE ACCOUNT                                 #
# ---------------------------------------------------------------------------- #
@router.delete("/profile")
async def delete_profile(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Literal["Account deleted successfully"]:

    await session.delete(user)
    await session.commit()

    return "Account deleted successfully"
