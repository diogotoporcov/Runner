from pathlib import Path
from typing import Union

import discord
from discord.ext.commands.bot import Bot

from utils.files import path_to_module, load_config, list_cogs

CONFIG = load_config(Path("./config.json"))


class Client(Bot):
    _INTENTS = discord.Intents.all()

    def __init__(self, prefix: str):
        super().__init__(intents=Client._INTENTS, command_prefix=prefix)

    async def on_ready(self):
        print(f"Logged on as {self.user}!")
        await self.load_cogs("./cogs")

    async def load_cogs(self, path: Union[Path, str]) -> None:
        if not isinstance(path, Path):
            path = Path(path)

        # Load cogs
        for cog_path in list_cogs(path):
            cog_module = path_to_module(cog_path)
            await self.load_extension(cog_module)
            print(f"Loaded cog: {cog_module}")
