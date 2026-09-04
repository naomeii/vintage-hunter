import asyncio

import pytest

from app.services.scheduler import run_scheduler


@pytest.mark.asyncio
async def test_scheduler_survives_hunter_failure(monkeypatch):
    calls = 0

    async def fake_hunter(user_id, discord_service):
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

    monkeypatch.setattr(
        "app.services.scheduler.get_all_users",
        lambda: [
            {
                "id": 1,
                "discord_user_id": "123456",
            }
        ],
    )

    with pytest.raises(asyncio.CancelledError):
        await run_scheduler("shared_discord_service")

    assert calls == 2


@pytest.mark.asyncio
async def test_scheduler_hunts_for_all_users(monkeypatch):
    calls = []

    async def fake_hunter(user_id, discord_service):
        calls.append(
            (
                user_id,
                discord_service,
            )
        )

        if user_id == 2:
            raise asyncio.CancelledError

    monkeypatch.setattr(
        "app.services.scheduler.run_hunter",
        fake_hunter,
    )

    monkeypatch.setattr(
        "app.services.scheduler.get_all_users",
        lambda: [
            {
                "id": 1,
                "discord_user_id": "123456",
            },
            {
                "id": 2,
                "discord_user_id": "987654",
            },
        ],
    )

    async def fake_sleep(seconds):
        return

    monkeypatch.setattr(
        "app.services.scheduler.asyncio.sleep",
        fake_sleep,
    )

    shared_discord_service = object()

    with pytest.raises(asyncio.CancelledError):
        await run_scheduler(shared_discord_service)

    assert calls == [
        (1, shared_discord_service),
        (2, shared_discord_service),
    ]