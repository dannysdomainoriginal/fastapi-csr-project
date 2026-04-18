from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal

from app.config.database import get_db, Post, User
from app.schemas import BlogCreate, BlogUpdate, BlogResponse
from app.dependencies.auth import get_current_user

router = APIRouter(tags=["blog"])


# --------------------------------------------------------- #
#                     GET ALL POSTS                         #
# --------------------------------------------------------- #
@router.get("/")
async def get_all_posts(
    limit: Optional[int] = 10,
    skip: Optional[int] = 0,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[BlogResponse]:

    query = (
        select(Post)
        .where(Post.author_id == user.id)
        .order_by(Post.created_at.desc())
        .offset(skip)
    )

    if limit is not None:
        query = query.limit(limit)

    result = await session.execute(query)
    posts = result.scalars().all()

    return list(map(BlogResponse.model_validate, posts))


# --------------------------------------------------------- #
#                    CREATE NEW POST                        #
# --------------------------------------------------------- #
@router.post("/", status_code=201)
async def create_post(
    fields: BlogCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> BlogResponse:
    new_post = Post(**fields.model_dump(), author_id=user.id)

    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)

    return BlogResponse.model_validate(new_post)


# --------------------------------------------------------- #
#                    GET POST BY ID                         #
# --------------------------------------------------------- #
@router.get("/{id}")
async def get_post_by_id(
    id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> BlogResponse:
    result = await session.execute(
        select(Post).where(Post.id == str(id), Post.author_id == user.id)
    )

    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(404, "Post not found")

    return BlogResponse.model_validate(post)


# --------------------------------------------------------- #
#                     UPDATE BY ID                          #
# --------------------------------------------------------- #
@router.patch("/{id}")
async def update_post_by_id(
    id: UUID,
    fields: BlogUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> BlogResponse:
    result = await session.execute(
        select(Post).where(Post.id == str(id), Post.author_id == user.id)
    )

    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(404, "Post not found")

    update_data = fields.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(post, key, value)

    await session.commit()
    await session.refresh(post)

    return BlogResponse.model_validate(post)


# --------------------------------------------------------- #
#                    DELETE BY ID                           #
# --------------------------------------------------------- #
@router.delete("/{id}")
async def delete_post_by_id(
    id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Literal["Delete successful"]:
    result = await session.execute(
        delete(Post).where(Post.id == str(id), Post.author_id == user.id)
    )

    if result.rowcount == 0:  # type: ignore[attr-defined]
        raise HTTPException(404, "Post not found")

    await session.commit()
    return "Delete successful"
