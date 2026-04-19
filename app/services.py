import os
import dotenv

from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException

from uuid import UUID
from typing import Sequence

from app.repositories import BlogRepo
from app.config.database import Post
from app.schemas import BlogCreate, BlogUpdate

dotenv.load_dotenv()


# ---------------------------------------------------------------------------- #
#                                 JWT Handling                                 #
# ---------------------------------------------------------------------------- #
class JWTService:
    SECRET_KEY = os.getenv("SECRET_KEY") or "secret-key"
    ALGORITHM = "HS256"

    @classmethod
    def issue_token(
        cls, user_id: str, expires_delta: timedelta = timedelta(days=7)
    ) -> str:
        payload = {
            "sub": user_id,
            "exp": datetime.now(timezone.utc) + expires_delta,
        }
        return jwt.encode(payload, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    def verify_token(cls, token: str):
        try:
            payload = jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
            user_id: str | None = payload.get("sub")

            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")

            return user_id
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Token verification failed",
            )


# ---------------------------------------------------------------------------- #
#                                 BLOG SERVICE                                 #
# ---------------------------------------------------------------------------- #
class BlogService:
    def __init__(self, repo: BlogRepo) -> None:
        self.repo = repo

    async def get_all_posts(
        self,
        limit: int = 10,
        skip: int = 0,
    ) -> Sequence[Post]:
        return await self.repo.get_all_posts(limit, skip)

    async def create_post(self, fields: BlogCreate) -> Post:
        return await self.repo.create_post(post=fields)

    async def get_post_or_404(self, id: UUID) -> Post:
        post = await self.repo.get_post_by_id(id)

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        return post

    async def update_post_or_404(self, id: UUID, fields: BlogUpdate) -> Post:
        post = await self.get_post_or_404(id)
        return await self.repo.update_post(post, fields)

    async def delete_post_or_404(self, id: UUID) -> None:
        deleted = await self.repo.delete_post(id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Post not found")
