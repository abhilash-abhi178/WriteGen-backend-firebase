# app/ai/tests/conftest.py
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    # provide a dedicated event loop for asyncio tests
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
