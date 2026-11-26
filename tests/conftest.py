"""Shared test fixtures."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest
from hypothesis import HealthCheck, settings

# No per-example deadline: timing on shared CI runners varies too much.
settings.register_profile(
    "amshan", deadline=None, suppress_health_check=[HealthCheck.too_slow]
)
settings.load_profile("amshan")


@pytest.fixture(autouse=True)
async def cancel_leftover_tasks() -> AsyncIterator[None]:
    """Cancel tasks a test leaves running, so they do not leak into other tests.

    ConnectionManager does not cancel its connect task on close (F13).
    """
    before = asyncio.all_tasks()
    yield
    leftovers = asyncio.all_tasks() - before - {asyncio.current_task()}
    for task in leftovers:
        task.cancel()
    await asyncio.gather(*leftovers, return_exceptions=True)
