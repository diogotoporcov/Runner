import asyncio
from typing import List

import discord


async def read_stream(stream: asyncio.StreamReader, lst: List[str]):
    while True:
        line = await stream.readline()
        if not line:
            break

        lst.append(line.decode().rstrip())


async def update_periodically(
        message: discord.Message,
        proc: asyncio.subprocess.Process,
        content: List[str],
        delay: float,
) -> None:
    while proc.returncode is None:
        await asyncio.sleep(delay)

        if content:
            await message.edit(content="📤 Output:\n```" + '\n'.join(content) + "```")
