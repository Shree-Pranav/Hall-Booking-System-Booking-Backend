from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from src.observability.logging.logger import instrument_class_methods


@dataclass(frozen=True)
class SseEvent:
    event: str
    data: dict[str, Any]


@instrument_class_methods
class NotificationHub:
    def __init__(self) -> None:
        self._subscribers: dict[UUID, set[asyncio.Queue[SseEvent]]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, user_id: UUID) -> asyncio.Queue[SseEvent]:
        queue: asyncio.Queue[SseEvent] = asyncio.Queue()
        async with self._lock:
            self._subscribers.setdefault(user_id, set()).add(queue)
        return queue

    async def unsubscribe(self, user_id: UUID, queue: asyncio.Queue[SseEvent]) -> None:
        async with self._lock:
            queues = self._subscribers.get(user_id)
            if not queues:
                return
            queues.discard(queue)
            if not queues:
                self._subscribers.pop(user_id, None)

    async def publish(self, user_ids: list[UUID], event: SseEvent) -> None:
        unique_user_ids = list({user_id for user_id in user_ids})
        async with self._lock:
            queues = [
                queue
                for user_id in unique_user_ids
                for queue in self._subscribers.get(user_id, set())
            ]

        for queue in queues:
            queue.put_nowait(event)

    async def notify_hall_disabled(
        self,
        user_ids: list[UUID],
        hall_id: UUID,
        hall_name: str,
    ) -> None:
        if not user_ids:
            return

        message = (
            "The booked hall "
            f"{hall_name} is temporarily out of service, please book another hall."
        )
        await self.publish(
            user_ids,
            SseEvent(
                event="hall-disabled",
                data={
                    "hall_id": str(hall_id),
                    "hall_name": hall_name,
                    "message": message,
                },
            ),
        )


notification_hub = NotificationHub()
