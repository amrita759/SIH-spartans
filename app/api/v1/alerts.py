import asyncio
from fastapi import APIRouter, Request
import redis.asyncio as aioredis
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("/stream")
async def live_alert_feed(request: Request):
    async def event_publisher():
        redis = aioredis.from_url("redis://localhost:6379/0")
        pubsub = redis.pubsub()
        await pubsub.subscribe("crimesight_live_feed")
        try:
            while True:
                # Disconnect listener if client drops connection
                if await request.is_disconnected():
                    break

                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if msg and msg.get("data"):
                    raw_data = msg["data"]
                    payload = raw_data.decode("utf-8") if isinstance(raw_data, bytes) else str(raw_data)
                    yield {"event": "new_alert", "data": payload}

                await asyncio.sleep(0.2)
        finally:
            await pubsub.unsubscribe("crimesight_live_feed")
            await pubsub.close()
            await redis.close()

    return EventSourceResponse(event_publisher())