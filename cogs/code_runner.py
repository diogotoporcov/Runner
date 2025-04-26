import asyncio
import re
from typing import Awaitable, Callable, Dict

from discord.ext import commands
from discord.ext.commands import Bot

from runner.runner import load_runners

# Type Definitions
_RUNNER_TYPE = Callable[[str, float], Awaitable[str]]

# Internal Runner Mapping
_runner_mapping: Dict[str, _RUNNER_TYPE] = {}


# Registration Decorator
def register_runner_func(*keys: str) -> Callable[[_RUNNER_TYPE], _RUNNER_TYPE]:
    def decorator(func: _RUNNER_TYPE) -> _RUNNER_TYPE:
        for key in keys:
            key = key.casefold()
            if key in _runner_mapping:
                raise KeyError(f"Key '{key}' is already defined.")

            _runner_mapping[key] = func
        return func

    return decorator


class Runner(commands.Cog):
    def __init__(self, bot: Bot):
        load_runners()
        self.bot = bot

    import discord

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.bot.user not in message.mentions:
            return

        code = None
        lang = None

        attachment = message.attachments[0] if message.attachments else None
        if attachment:
            file_extension = attachment.filename.split('.')[-1].casefold()
            lang = file_extension
            code = await attachment.read()

        else:
            pattern = r"```(\w+)\n([\s\S]+?)```"
            match = re.search(pattern, message.content)
            if match:
                lang = match.group(1).casefold()
                code = match.group(2)

        if not lang or not code:
            return

        runner_func = _runner_mapping.get(lang)
        if not callable(runner_func):
            await message.reply(f"❌ Language `{lang}` not implemented!")
            return

        # Run the code and reply with the output
        output = await Runner._run_code_with_timeout(code.decode() if isinstance(code, bytes) else code, runner_func)
        await message.reply(f"📤 Output:\n```\n{output}```")

    @staticmethod
    async def _run_code_with_timeout(
        code: str,
        runner_func: _RUNNER_TYPE,
        *,
        timeout: float = 60,
    ) -> str:
        output = "Something went wrong!"

        try:
            output = await asyncio.wait_for(runner_func(code, timeout), timeout)

        except asyncio.TimeoutError:
            output = "Error: Code execution exceeded the timeout limit."

        finally:
            return output


async def setup(bot: Bot):
    await bot.add_cog(Runner(bot))
