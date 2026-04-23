from fastapi import APIRouter, Depends

from app.services import AuthService, UserService
from app.dependencies.services import get_auth_service, get_user_service
from app.schemas import UserLogin, TokenResponse, UserCreate, UserResponse, UserUpdate

router = APIRouter(tags=["auth"])


# ---------------------------------------------------------------------------- #
#                                CREATE NEW USER                               #
# ---------------------------------------------------------------------------- #
@router.post("/signup", status_code=201)
async def signup(
    fields: UserCreate, service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    token = await service.signup(fields)
    return TokenResponse(token=token)


# ---------------------------------------------------------------------------- #
#                            LOGIN USING CREDENTIALS                           #
# ---------------------------------------------------------------------------- #
@router.post("/login")
async def login(
    fields: UserLogin, service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    token = await service.login(fields)
    return TokenResponse(token=token)


# ---------------------------------------------------------------------------- #
#                                  ISSUE TOKEN                                 #
# ---------------------------------------------------------------------------- #
@router.get("/session")
async def new_token(
    service: UserService = Depends(get_user_service),
) -> TokenResponse:
    return TokenResponse(token=service.issue_token())


# ---------------------------------------------------------------------------- #
#                                  GET PROFILE                                 #
# ---------------------------------------------------------------------------- #
@router.get("/profile")
async def get_profile(service: UserService = Depends(get_user_service)) -> UserResponse:
    return UserResponse.model_validate(service.user)


# ---------------------------------------------------------------------------- #
#                                 UPDATE PROFILE                               #
# ---------------------------------------------------------------------------- #
@router.patch("/profile")
async def update_profile(
    fields: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await service.update_profile(fields)
    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------- #
#                               DELETE ACCOUNT                                 #
# ---------------------------------------------------------------------------- #
@router.delete("/profile", status_code=204)
async def delete_profile(
    service: UserService = Depends(get_user_service),
):
    await service.delete_account()
