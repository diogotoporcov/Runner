import asyncio
from typing import List

import discord

from utils.messages import format_to_discord_message


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

        if not content:
            continue

        formatted_content = format_to_discord_message(
            "\n".join(content),
            "📤 Output:\n```\n",
            "```"
        )

        await message.edit(content=formatted_content)
