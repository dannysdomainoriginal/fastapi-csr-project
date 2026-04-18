from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal

from app.config.database import get_db, Post
from app.schemas import BlogCreate, BlogUpdate, BlogResponse

router = APIRouter(tags=["blog"])


# --------------------------------------------------------- #
#                     GET ALL POSTS                         #
# --------------------------------------------------------- #
@router.get("/")
async def get_all_posts(
    limit: Optional[int] = 10,
    skip: Optional[int] = 0,
    session: AsyncSession = Depends(get_db),
) -> list[BlogResponse]:
    query = select(Post).order_by(Post.created_at.desc()).offset(skip)

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
    fields: BlogCreate, session: AsyncSession = Depends(get_db)
) -> BlogResponse:
    new_post = Post(**fields.model_dump())

    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)

    return BlogResponse.model_validate(new_post)


# --------------------------------------------------------- #
#                    GET POST BY ID                         #
# --------------------------------------------------------- #
@router.get("/{id}")
async def get_post_by_id(
    id: UUID, session: AsyncSession = Depends(get_db)
) -> BlogResponse:
    # session.get is the most efficient lookup for a single Primary Key
    post = await session.get(Post, str(id))

    if not post:
        raise HTTPException(404, "Post not found")

    return BlogResponse.model_validate(post)


# --------------------------------------------------------- #
#                     UPDATE BY ID                          #
# --------------------------------------------------------- #
@router.patch("/{id}")
async def update_post_by_id(
    id: UUID, fields: BlogUpdate, session: AsyncSession = Depends(get_db)
) -> BlogResponse:
    post = await session.get(Post, str(id))

    if not post:
        raise HTTPException(404, "Post not found")

    # Update instance attributes directly from the dump
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
    id: UUID, session: AsyncSession = Depends(get_db)
) -> Literal["Delete successful"]:
    # Execute the delete and check rowcount
    result = await session.execute(delete(Post).where(Post.id == str(id)))

    if result.rowcount == 0:  # type: ignore[attr-defined]
        raise HTTPException(404, "Post not found")

    await session.commit()
    return "Delete successful"
