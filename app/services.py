import os
import dotenv

from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException




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
