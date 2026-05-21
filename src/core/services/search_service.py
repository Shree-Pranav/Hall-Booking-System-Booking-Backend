from datetime import datetime
from uuid import UUID


from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from src.data.repositories.search_repository import SearchRepository




class SearchService:
    def __init__(self, session: AsyncSession):
        self.search_repository = SearchRepository(session)


    def _validate_datetime_range(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
    ):
        """Validate that start is before end."""
        if start_datetime >= end_datetime:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start datetime must be before end datetime",
            )


    async def search_available_halls(
        self,
        search_start: datetime,
        search_end: datetime,
        hall_id: UUID | None = None,
        hall_name: str | None = None,
        facility_id: int | None = None,
        facility_name: str | None = None,
    ) -> dict:
        """
        Search for available hall slots based on filters.
        """
        # Validate datetime range
        self._validate_datetime_range(search_start, search_end)


        # At least one filter should be provided (optional but recommended)
        # We allow search with just datetime range to show all halls


        results = await self.search_repository.search_halls(
            search_start=search_start,
            search_end=search_end,
            hall_id=hall_id,
            hall_name=hall_name,
            facility_id=facility_id,
            facility_name=facility_name,
        )


        return {
            "search_filters": {
                "start_datetime": search_start,
                "end_datetime": search_end,
                "hall_id": hall_id,
                "hall_name": hall_name,
                "facility_id": facility_id,
                "facility_name": facility_name,
            },
            "results": results,
        }


