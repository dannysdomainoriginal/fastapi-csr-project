from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from uuid import UUID

from app.config.database import get_db, Post, User
from app.schemas import BlogCreate, BlogUpdate, BlogResponse


class BlogRepo:
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def get_all_posts(
        self,
        limit: int = 10,
        skip: int = 0,
    ):
        query = (
            select(Post)
            .where(Post.author_id == self.user_id)
            .order_by(Post.created_at.desc())
            .offset(skip)
        )

        if limit is not None:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_post(self, post: BlogCreate):
        new_post = Post(**post.model_dump(), author_id=self.user_id)

        self.db.add(new_post)
        await self.db.commit()
        await self.db.refresh(new_post)
        return new_post

    async def get_post_by_id(self, id: UUID):
        result = await self.db.execute(
            select(Post).where(Post.id == str(id), Post.author_id == self.user_id)
        )

        return result.scalar_one_or_none()

    async def update_post(self, post: Post, updates: BlogUpdate):
        update_data = updates.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(post, key, value)

        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def delete_post(self, id: UUID) -> bool:
        result = await self.db.execute(
            delete(Post).where(
                Post.id == str(id),
                Post.author_id == self.user_id,
            )
        )

        await self.db.commit()
        return bool(result.rowcount)  # type: ignore[attr-defined]
