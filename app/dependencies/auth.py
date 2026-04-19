from fastapi import HTTPException, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import TokenService
from app.config.database import get_db, User

api_key_scheme = APIKeyHeader(name="Authorization")


# ---------------------------------------------------------------------------- #
#                                AUTHENTICATION                                #
# ---------------------------------------------------------------------------- #
async def get_current_user(
    token: str = Depends(api_key_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    user_id = TokenService.verify_token(token)
    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
