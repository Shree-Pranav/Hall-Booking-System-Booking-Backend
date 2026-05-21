from __future__ import annotations

import asyncio
import json
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from src.api.rest.dependencies import TokenData, verify_token
from src.core.services.notification_service import notification_hub
from src.observability.logging.logger import get_logger, log_function


router = APIRouter(prefix="/events", tags=["events"])
logger = get_logger(__name__)


@router.get("/hall-status")
@log_function(logger)
async def hall_status_events(
    token_data: Annotated[TokenData, Depends(verify_token)],
) -> StreamingResponse:
    async def event_stream():
        logger.info("Starting SSE stream for user_id=%s", token_data.user_id)
        queue = await notification_hub.subscribe(token_data.user_id)
        try:
            yield "event: connected\ndata: {}\n\n"
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                    payload = json.dumps(event.data)
                    logger.info("Streaming event=%s for user_id=%s", event.event, token_data.user_id)
                    yield f"event: {event.event}\ndata: {payload}\n\n"
                except asyncio.TimeoutError:
                    yield "event: ping\ndata: {}\n\n"
        finally:
            await notification_hub.unsubscribe(token_data.user_id, queue)
            logger.info("Closed SSE stream for user_id=%s", token_data.user_id)

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=headers,
    )
