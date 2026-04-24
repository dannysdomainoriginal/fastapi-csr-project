from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from concurrent.futures import ProcessPoolExecutor

from app.config.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.process_pool import get_process_pool

from app.repositories import BlogRepo, UserRepo, IssueRepo
from app.config.database import User
from app.services import BlogService, AuthService, UserService, IssueService


# ---------------------------------------------------------------------------- #
#                             BLOG REPO AND SERVICE                            #
# ---------------------------------------------------------------------------- #
def get_blog_service(
    pool: ProcessPoolExecutor = Depends(get_process_pool),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BlogService:
    return BlogService(repo=BlogRepo(db=session, user_id=user.id), pool=pool)


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
def get_issue_service(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> IssueService:
    return IssueService(repo=IssueRepo(db=session, user_id=user.id))
