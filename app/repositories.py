from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID

from app.config.database import Post, User, Issue
from app.schemas import (
    BlogCreate,
    BlogUpdate,
    UserCreate,
    UserUpdate,
    IssueCreate,
    IssueUpdate,
)


# ---------------------------------------------------------------------------- #
#                                BLOG REPOSITORY                               #
# ---------------------------------------------------------------------------- #
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
            select(Post).where(Post.id == id, Post.author_id == self.user_id)
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
                Post.id == id,
                Post.author_id == self.user_id,
            )
        )

        await self.db.commit()
        return bool(result.rowcount)  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------- #
#                                USER REPOSITORY                               #
# ---------------------------------------------------------------------------- #
class UserRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, fields: UserCreate) -> User:
        new_user = User(**fields.model_dump())

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return new_user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email).limit(1))
        return result.scalar_one_or_none()

    async def update_profile(self, user: User, fields: UserUpdate) -> User:
        update_data = fields.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_profile(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()


# ---------------------------------------------------------------------------- #
#                              ISSUES REPOSITORIES                             #
# ---------------------------------------------------------------------------- #
class IssueRepo:
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def get_all_issues(
        self,
        limit: int = 10,
        skip: int = 0,
    ):
        query = (
            select(Issue)
            .where(Issue.author_id == self.user_id)
            .order_by(Issue.created_at.desc())
            .offset(skip)
        )

        if limit is not None:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_issue(self, issue: IssueCreate):
        new_issue = Issue(**issue.model_dump(), author_id=self.user_id, status="open")

        self.db.add(new_issue)
        await self.db.commit()
        await self.db.refresh(new_issue)
        return new_issue

    async def get_issue_by_id(self, id: UUID):
        result = await self.db.execute(
            select(Issue).where(Issue.id == id, Issue.author_id == self.user_id)
        )

        return result.scalar_one_or_none()

    async def update_issue(self, issue: Issue, updates: IssueUpdate):
        update_data = updates.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(issue, key, value)

        await self.db.commit()
        await self.db.refresh(issue)
        return issue

    async def delete_issue(self, id: UUID) -> bool:
        result = await self.db.execute(
            delete(Issue).where(
                Issue.id == id,
                Issue.author_id == self.user_id,
            )
        )

        await self.db.commit()
        return bool(result.rowcount)  # type: ignore[attr-defined]
