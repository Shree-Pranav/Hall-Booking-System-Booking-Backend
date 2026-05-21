from datetime import datetime
from datetime import timedelta
from datetime import timezone
from uuid import UUID


from sqlalchemy.ext.asyncio import AsyncSession


from src.core.exceptions import InvalidSearchDataException
from src.data.repositories.search_repository import SearchRepository
from src.observability.logging.logger import instrument_class_methods




@instrument_class_methods
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
            raise InvalidSearchDataException(
                "Start datetime must be before end datetime"
            )

    def _validate_half_hour_increment(self, value: datetime):
        if value.minute not in (0, 30) or value.second != 0 or value.microsecond != 0:
            raise InvalidSearchDataException(
                "Search times must start and end on the hour or half hour"
            )


    def _current_bookable_start(self) -> datetime:
        raw_now = datetime.now(timezone.utc)
        now = raw_now.replace(tzinfo=None, second=0, microsecond=0)
        minute_offset = now.minute % 30
        if minute_offset or raw_now.second or raw_now.microsecond:
            now += timedelta(minutes=30 - minute_offset)

        return now


    def _normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value

        return value.astimezone(timezone.utc).replace(tzinfo=None)


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
        search_start = self._normalize_datetime(search_start)
        search_end = self._normalize_datetime(search_end)
        self._validate_half_hour_increment(search_end)

        current_bookable_start = self._current_bookable_start()
        if search_start < current_bookable_start:
            search_start = current_bookable_start
        else:
            self._validate_half_hour_increment(search_start)

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


