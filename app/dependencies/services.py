from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.dependencies.auth import get_current_user

from app.repositories import BlogRepo, UserRepo, IssueRepo
from app.config.database import User
from app.services import BlogService, AuthService, UserService, IssueService


# ---------------------------------------------------------------------------- #
#                             BLOG REPO AND SERVICE                            #
# ---------------------------------------------------------------------------- #
def get_blog_repo(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BlogRepo:
    return BlogRepo(db=session, user_id=user.id)


def get_blog_service(repo: BlogRepo = Depends(get_blog_repo)) -> BlogService:
    return BlogService(repo=repo)


# ---------------------------------------------------------------------------- #
#                          USER, AUTH REPO AND SERVICE                         #
# ---------------------------------------------------------------------------- #
async def get_user_repo(session: AsyncSession = Depends(get_db)) -> UserRepo:
    return UserRepo(db=session)


async def get_auth_service(user_repo: UserRepo = Depends(get_user_repo)) -> AuthService:
    return AuthService(repo=user_repo)


async def get_user_service(
    repo: UserRepo = Depends(get_user_repo),
    user: User = Depends(get_current_user),
):
    return UserService(repo=repo, user=user)


# ---------------------------------------------------------------------------- #
#                            ISSUE REPO AND SERVICE                            #
# ---------------------------------------------------------------------------- #
def get_issue_repo(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> IssueRepo:
    return IssueRepo(db=session, user_id=user.id)


def get_issue_service(repo: IssueRepo = Depends(get_issue_repo)) -> IssueService:
    return IssueService(repo=repo)
