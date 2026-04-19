from uuid import UUID
from fastapi import APIRouter, Depends

from app.schemas import BlogCreate, BlogUpdate, BlogResponse
from app.dependencies.blog import get_blog_service
from app.services import BlogService

router = APIRouter(tags=["blog"])


# --------------------------------------------------------- #
#                     GET ALL POSTS                         #
# --------------------------------------------------------- #
@router.get("/")
async def get_all_posts(
    limit: int = 10,
    skip: int = 0,
    service: BlogService = Depends(get_blog_service),
) -> list[BlogResponse]:
    posts = await service.get_all_posts(limit, skip)
    return list(map(BlogResponse.model_validate, posts))


# --------------------------------------------------------- #
#                    CREATE NEW POST                        #
# --------------------------------------------------------- #
@router.post("/", status_code=201)
async def create_post(
    fields: BlogCreate,
    service: BlogService = Depends(get_blog_service),
) -> BlogResponse:
    new_post = await service.create_post(fields)
    return BlogResponse.model_validate(new_post)


# --------------------------------------------------------- #
#                    GET POST BY ID                         #
# --------------------------------------------------------- #
@router.get("/{id}")
async def get_post_by_id(
    id: UUID,
    service: BlogService = Depends(get_blog_service),
) -> BlogResponse:
    post = await service.get_post_or_404(id)
    return BlogResponse.model_validate(post)


# --------------------------------------------------------- #
#                     UPDATE BY ID                          #
# --------------------------------------------------------- #
@router.patch("/{id}")
async def update_post_by_id(
    id: UUID,
    fields: BlogUpdate,
    service: BlogService = Depends(get_blog_service),
) -> BlogResponse:
    post = await service.update_post_or_404(id, fields)
    return BlogResponse.model_validate(post)


# --------------------------------------------------------- #
#                    DELETE BY ID                           #
# --------------------------------------------------------- #
@router.delete("/{id}", status_code=204)
async def delete_post_by_id(
    id: UUID,
    service: BlogService = Depends(get_blog_service),
) -> None:
    await service.delete_post_or_404(id)
