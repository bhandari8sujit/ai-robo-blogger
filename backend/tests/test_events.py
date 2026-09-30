import asyncio

from app.core.events import EventHub


def test_event_hub_delivers_and_removes_subscriber() -> None:
    async def scenario() -> None:
        hub = EventHub()
        subscription = hub.subscribe("blog-1")
        pending = asyncio.create_task(anext(subscription))
        await asyncio.sleep(0)

        await hub.publish("draft.updated", "blog-1", {"version": 2})
        event = await pending
        assert event.type == "draft.updated"
        assert event.payload == {"version": 2}

        await subscription.aclose()
        assert hub._queues["blog-1"] == []

    asyncio.run(scenario())