# app/ai/tasks/background_tasks.py
"""
Simple background runner wrapper using asyncio.create_task.
For production, use a worker queue (RQ/Celery) or dedicated worker process.
"""
import asyncio
from typing import Callable, Any

class BackgroundTaskRunner:
    def __init__(self):
        self._tasks = []

    def run(self, coro: Callable[..., Any]):
        t = asyncio.create_task(coro)
        self._tasks.append(t)
        return t

    async def wait_all(self):
        if not self._tasks:
            return
        await asyncio.gather(*self._tasks, return_exceptions=True)
