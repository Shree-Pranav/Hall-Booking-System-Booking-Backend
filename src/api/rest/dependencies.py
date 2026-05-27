from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID
from fastapi import Depends, Header, Query
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.settings import settings
from src.core.exceptions import InvalidTokenException, UnauthorizedException
from src.data.clients.postgres_client import get_db_session
from src.observability.logging.logger import get_logger
from src.schemas.token_schema import TokenData  


logger = get_logger(__name__)


async def db_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    logger.info("Entering db_session_dependency")
    async for session in get_db_session():
        logger.info("db_session_dependency yielded session")
        yield session
    logger.info("Exiting db_session_dependency")


async def verify_token(
    authorization: str | None = Header(default=None, alias="Authorization"),
    token: str | None = Query(default=None),
) -> TokenData:
    """Verify token sent by the Authorization header or SSE query string."""
    logger.info("Entering verify_token")
    access_token = None
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization.removeprefix("Bearer ").strip()
    elif token:
        access_token = token.strip()

    if not access_token:
        raise InvalidTokenException("Missing access token")

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

    logger.info("verify_token completed")
    logger.info("Exiting verify_token")
    return token_data


async def verify_admin_role(token_data: Annotated[TokenData, Depends(verify_token)]) -> TokenData:
    """Verify that the user has admin role."""
    logger.info("Entering verify_admin_role")
    if token_data.role != "admin":
        raise UnauthorizedException("Admin role required")
    logger.info("verify_admin_role completed")
    logger.info("Exiting verify_admin_role")
    return token_data

async def get_current_user(token_data: Annotated[TokenData, Depends(verify_token)]) -> dict:
    """Get current user info from token data."""
    logger.info("Entering get_current_user")
    logger.info("get_current_user completed")
    logger.info("Exiting get_current_user")
    return {
        "user_id": token_data.user_id,
        "role": token_data.role,
    }


async def get_current_admin_user(
    token_data: Annotated[TokenData, Depends(verify_admin_role)]
) -> dict:
    """Get current admin user info from token data."""
    logger.info("Entering get_current_admin_user")
    logger.info("get_current_admin_user completed")
    logger.info("Exiting get_current_admin_user")
    return {
        "user_id": token_data.user_id,
        "role": token_data.role,
    }
