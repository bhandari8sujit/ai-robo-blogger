from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime, UTC
import json

@dataclass
class EventMessage:
    # A dataclass generates the initializer and field storage from these annotated attributes.
    type: str
    blog_id: str
    payload: dict
    created_at: str

    def to_sse(self) -> str:
        # SSE frames are text records separated by a blank line, not ordinary JSON responses.
        body = {
            "type": self.type,
            "blogId": self.blog_id,
            "payload": self.payload,
            "createdAt": self.created_at,
        }
        return f"data: {json.dumps(body)}\\n\\n"


class EventHub:
    def __init__(self) -> None:
    # defaultdict(list) creates an empty subscriber list on first access for a blog id.
        self._queues: dict[str, list[asyncio.Queue[EventMessage]]] = defaultdict(list)

    async def publish(self, event_type: str, blog_id: str, payload: dict) -> None:
        # Each connected client owns a queue, so every subscriber receives the event.
        event = EventMessage(
            type=event_type,
            blog_id=blog_id,
            payload=payload,
            created_at=datetime.now(UTC).isoformat(),
        )
        for queue in list(self._queues.get(blog_id, [])):
            await queue.put(event)

    async def subscribe(self, blog_id: str) -> AsyncIterator[EventMessage]:
        # An async generator can await between yielded values while retaining its local state.
        queue: asyncio.Queue[EventMessage] = asyncio.Queue()
        self._queues[blog_id].append(queue)
        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            # `finally` also runs when a browser disconnect closes the generator.
            self._queues[blog_id].remove(queue)


# One in-memory hub is shared by all route handlers in this process.
event_hub = EventHub()
