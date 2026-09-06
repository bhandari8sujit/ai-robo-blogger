from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Path

from app.core.events import event_hub

try:
    # This optional import selects FastAPI's SSE helper when the installed version provides it.
    from fastapi.sse import EventSourceResponse, ServerSentEvent
except Exception:  # pragma: no cover
    EventSourceResponse = None
    ServerSentEvent = None

router = APIRouter(prefix="/blogs", tags=["events"])


@router.get("/{blog_id}/events")
async def stream_events(blog_id: Annotated[str, Path(min_length=1)]):
    # The nested async generator stays alive for the connection and yields each event as it arrives.
    async def event_iterator() -> AsyncIterator[str | ServerSentEvent]:
        async for item in event_hub.subscribe(blog_id):
            if ServerSentEvent is not None:
                yield ServerSentEvent(data={
                    "type": item.type,
                    "blogId": item.blog_id,
                    "payload": item.payload,
                    "createdAt": item.created_at,
                })
            else:
                yield item.to_sse()

    if EventSourceResponse is not None:
        return EventSourceResponse(event_iterator())

    from fastapi.responses import StreamingResponse

    # The generic streaming response is the standards-compatible fallback for SSE.
    return StreamingResponse(event_iterator(), media_type="text/event-stream")
