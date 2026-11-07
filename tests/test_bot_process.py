from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import cast

import pytest

from app.bot_process import BotProcess, BotProcessError


def test_read_keeps_process_reference_if_stopped_while_reading() -> None:
    async def scenario() -> None:
        bot = BotProcess()
        fake_process: dict[str, Any] = {}

        async def readline() -> bytes:
            bot.process = None
            return b""

        async def wait() -> int:
            return 7

        bot.process = cast(
            asyncio.subprocess.Process,
            SimpleNamespace(
                stdout=SimpleNamespace(readline=readline),
                wait=wait,
            ),
        )

        with pytest.raises(BotProcessError, match="Worker exited with code 7"):
            await bot._read(1.0)

    asyncio.run(scenario())
