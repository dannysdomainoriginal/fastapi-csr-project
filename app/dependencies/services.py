from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.dependencies.auth import get_current_user

from app.repositories import BlogRepo, UserRepo
from app.config.database import User
from app.services import BlogService, AuthService, UserService


def get_blog_repo(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BlogRepo:
    return BlogRepo(db=session, user_id=user.id)


def get_blog_service(repo: BlogRepo = Depends(get_blog_repo)) -> BlogService:
    return BlogService(repo=repo)


async def get_user_repo(session: AsyncSession = Depends(get_db)) -> UserRepo:
    return UserRepo(db=session)


async def get_auth_service(user_repo: UserRepo = Depends(get_user_repo)) -> AuthService:
    return AuthService(repo=user_repo)


async def get_user_service(
    repo: UserRepo = Depends(get_user_repo),
    user: User = Depends(get_current_user),
):
    return UserService(repo=repo, user=user)
