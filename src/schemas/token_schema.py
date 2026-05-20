from pydantic import BaseModel
from uuid import UUID

class TokenData(BaseModel):
    user_id: UUID
    role: str