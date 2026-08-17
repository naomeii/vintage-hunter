import asyncio

import pytest

from app.services.scheduler import run_scheduler


@pytest.mark.asyncio
async def test_scheduler_survives_hunter_failure(monkeypatch):
    calls = 0

    async def fake_hunter(discord_service):
        nonlocal calls

        calls += 1

        if calls == 1:
            raise RuntimeError("Hunter exploded")

        raise asyncio.CancelledError

    monkeypatch.setattr(
        "app.services.scheduler.run_hunter",
        fake_hunter,
    )

    async def fake_sleep(seconds):
        return

    monkeypatch.setattr(
        "app.services.scheduler.asyncio.sleep",
        fake_sleep,
    )

    with pytest.raises(asyncio.CancelledError):
        await run_scheduler(None)

    assert calls == 2