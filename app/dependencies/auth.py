from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db, User
from app.services import JWTService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ---------------------------------------------------------------------------- #
#                                AUTHENTICATION                                #
# ---------------------------------------------------------------------------- #
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    user_id = JWTService.verify_token(token)
    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
