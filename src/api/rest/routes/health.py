from fastapi import APIRouter
from sqlalchemy import text

from src.data.clients.postgres_client import get_or_create_engine

router = APIRouter(prefix="/health", tags=["health"])



@router.get("")
async def health() -> dict[str, str]:
    engine = await get_or_create_engine()
    try:    
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as e:
        return {"status": "error", "message": str(e)}
    return {"status": "ok"}