from datetime import datetime
from typing import Optional
from uuid import UUID


from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession


from src.api.rest.dependencies import get_current_user, get_db_session
from src.core.exceptions import UnauthorizedException
from src.observability.logging.logger import get_logger, log_function
from src.core.services.search_service import SearchService
from src.schemas.search_schema import SearchResult


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)
logger = get_logger(__name__)




@router.get(
    "/available-halls",
    response_model=SearchResult,
    status_code=status.HTTP_200_OK,
)
@log_function(logger)
async def search_available_halls(
    start_datetime: datetime = Query(..., description="Search window start datetime"),
    end_datetime: datetime = Query(..., description="Search window end datetime"),
    hall_id: Optional[UUID] = Query(None, description="Filter by hall ID"),
    hall_name: Optional[str] = Query(None, description="Filter by hall name"),
    facility_id: Optional[int] = Query(None, description="Filter by facility ID"),
    facility_name: Optional[str] = Query(None, description="Filter by facility name"),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    """
    Search for available halls within a time window.


    Query Parameters:
    - start_datetime: Required. Start of search window (ISO format)
    - end_datetime: Required. End of search window (ISO format)
    - hall_id: Optional. Filter by specific hall ID
    - hall_name: Optional. Filter by specific hall name
    - facility_id: Optional. Filter by facility ID
    - facility_name: Optional. Filter by facility name


    Returns halls with available time slots during the search window.
    """
    search_service = SearchService(session)

    if current_user is None:
        raise UnauthorizedException("Authentication required to perform search")

    return await search_service.search_available_halls(
        search_start=start_datetime,
        search_end=end_datetime,
        hall_id=hall_id,
        hall_name=hall_name,
        facility_id=facility_id,
        facility_name=facility_name,
    )
