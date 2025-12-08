# app/ai/tasks/queue_adapter.py
"""
Small in-memory queue adapter for testing/CI.
Replace with Redis/RQ adapter or Celery in production.
"""
import asyncio
from typing import Any, Callable, Coroutine, Optional

class InMemoryQueueAdapter:
    def __init__(self):
        self._queue = asyncio.Queue()

    async def enqueue(self, payload: Any):
        await self._queue.put(payload)

    async def worker(self, handler: Callable[[Any], Coroutine[Any, Any, Any]]):
        while True:
            item = await self._queue.get()
            try:
                await handler(item)
            except Exception:
                # logging omitted for brevity
                pass
            self._queue.task_done()

    async def drain(self):
        await self._queue.join()
