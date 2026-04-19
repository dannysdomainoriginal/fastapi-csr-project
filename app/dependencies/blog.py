from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.repositories import BlogRepo
from app.config.database import User
from app.services import BlogService


def get_blog_repo(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BlogRepo:
    return BlogRepo(db=session, user_id=user.id)


def get_blog_service(repo: BlogRepo = Depends(get_blog_repo)) -> BlogService:
    return BlogService(repo=repo)
