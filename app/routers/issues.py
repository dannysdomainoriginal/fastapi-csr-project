from uuid import UUID
from fastapi import APIRouter, Depends

from app.services import IssueService
from app.schemas import IssueCreate, IssueUpdate, IssueResponse
from app.dependencies.services import get_issue_service

router = APIRouter(tags=["issues"])


# --------------------------------------------------------- #
#                     GET ALL ISSUES                         #
# --------------------------------------------------------- #
@router.get("/")
async def get_all_issues(
    limit: int = 10,
    skip: int = 0,
    service: IssueService = Depends(get_issue_service),
) -> list[IssueResponse]:
    issues = await service.get_all_issues(limit, skip)
    return list(map(IssueResponse.model_validate, issues))


# --------------------------------------------------------- #
#                    CREATE NEW ISSUE                        #
# --------------------------------------------------------- #
@router.post("/", status_code=201)
async def create_issue(
    fields: IssueCreate,
    service: IssueService = Depends(get_issue_service),
) -> IssueResponse:
    new_issue = await service.create_issue(fields)
    return IssueResponse.model_validate(new_issue)


# --------------------------------------------------------- #
#                    GET ISSUE BY ID                         #
# --------------------------------------------------------- #
@router.get("/{id}")
async def get_issue_by_id(
    id: UUID,
    service: IssueService = Depends(get_issue_service),
) -> IssueResponse:
    issue = await service.get_issue_or_404(id)
    return IssueResponse.model_validate(issue)


# --------------------------------------------------------- #
#                     UPDATE BY ID                          #
# --------------------------------------------------------- #
@router.patch("/{id}")
async def update_issue_by_id(
    id: UUID,
    fields: IssueUpdate,
    service: IssueService = Depends(get_issue_service),
) -> IssueResponse:
    issue = await service.update_issue_or_404(id, fields)
    return IssueResponse.model_validate(issue)


# --------------------------------------------------------- #
#                    DELETE BY ID                           #
# --------------------------------------------------------- #
@router.delete("/{id}", status_code=204)
async def delete_issue_by_id(
    id: UUID,
    service: IssueService = Depends(get_issue_service),
) -> None:
    await service.delete_issue_or_404(id)
