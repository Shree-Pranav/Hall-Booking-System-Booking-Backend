from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID
from fastapi import Cookie, Depends
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.settings import settings
from src.core.exceptions import InvalidTokenException, UnauthorizedException
from src.data.clients.postgres_client import get_db_session
from src.schemas.token_schema import TokenData  



async def db_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


async def verify_token(
    access_token: str | None = Cookie(default=None, alias="access_token"),
) -> TokenData:
    """Verify token sent by the browser cookie."""
    if not access_token:
        raise InvalidTokenException("Missing access token cookie")

    try:
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id_from_token = payload.get("user_id")
        token_role = payload.get("role")

        if user_id_from_token is None or token_role is None:
            raise InvalidTokenException("Token payload is incomplete")

        token_data = TokenData(
            user_id=UUID(str(user_id_from_token)),
            role=token_role,
        )
    except (JWTError, ValueError) as e:
        raise InvalidTokenException(f"Invalid token: {str(e)}")

    return token_data


async def verify_admin_role(token_data: Annotated[TokenData, Depends(verify_token)]) -> TokenData:
    """Verify that the user has admin role."""
    if token_data.role != "admin":
        raise UnauthorizedException("Admin role required")
    return token_data

async def get_current_user(token_data: Annotated[TokenData, Depends(verify_token)]) -> dict:
    """Get current user info from token data."""
    return {
        "user_id": token_data.user_id,
        "role": token_data.role,
    }


async def get_current_admin_user(
    token_data: Annotated[TokenData, Depends(verify_admin_role)]
) -> dict:
    """Get current admin user info from token data."""
    return {
        "user_id": token_data.user_id,
        "role": token_data.role,
    }
