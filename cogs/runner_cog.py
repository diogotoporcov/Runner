import asyncio
import shutil
import tempfile
import time
import uuid
from collections import ChainMap
from pathlib import Path
from typing import Optional, Tuple

import discord
from discord.ext.commands import Bot, Cog

from client.client import CONFIG
from utils.code_helper import extract_code, runner_command_generator
from utils.messages import format_to_discord_message
from utils.stream import read_stream, update_periodically

# Get the loaded config
RUNNER_CONFIG = CONFIG["runner"]


# Define the Runner Cog
class Runner(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if self.bot.user not in message.mentions:
            return

        filename, lang, code = await extract_code(message, RUNNER_CONFIG)

        if not code:
            return

        if not lang:
            await message.reply(format_to_discord_message("❌ Language not supported!"))
            return

        reply = await message.reply("⚙️ Running...")

        try:
            output, execution_time = await Runner._run_code(reply, lang, code, filename, RUNNER_CONFIG["timeout"])

        except TimeoutError as e:
            await reply.edit(content=format_to_discord_message(
                f"🕒 Execution timed out after {str(e)}s.")
            )

        except RuntimeError as e:
            await reply.edit(content=format_to_discord_message(
                str(e),
                "❌ Error: ```\n",
                "\n```")
            )

        except Exception as e:
            print(f"{type(e).__name__}: {str(e)}")
            await reply.edit(content=format_to_discord_message(
                "`Something went wrong!`",
                "❌ Error: ")
            )

        else:
            await reply.edit(
                content=format_to_discord_message(
                    output,
                    "📤 Output:\n```\n",
                    f"```\n✅ Executed"
                    # " in {execution_time:.2f}s!"
                )
            )

    # Function to run the code within Docker sandbox
    @staticmethod
    async def _run_code(
            message: discord.Message,
            language: str,
            code: str,
            file_name: Optional[str] = None,
            timeout: float = 120
    ) -> Tuple[Optional[str], float]:
        tempdir = None
        proc = None

        try:
            # Check if the language is implemented
            if language not in RUNNER_CONFIG["overrides"]:
                raise ValueError(f"Language '{language}' is not implemented.")

            # Merge default config with overrides using ChainMap
            default_config = RUNNER_CONFIG["default"]
            language_config = RUNNER_CONFIG["overrides"].get(language)

            # Combine the dictionaries, with language_config taking precedence
            config = ChainMap(language_config, default_config)

            # Ensure required fields are not null
            if not config["docker_image"]:
                raise ValueError("docker_image is not provided.")

            if not config["source_filename"]:
                raise ValueError("source_filename is not provided.")

            if not config["run_command"]:
                raise ValueError("run_command is not provided.")

            # Set up temp dir
            base_temp = Path(tempfile.gettempdir()) / "RunnerSandbox"
            base_temp.mkdir(parents=True, exist_ok=True)

            dir_id = uuid.uuid4().hex
            tempdir = base_temp / dir_id
            tempdir.mkdir(parents=True)

            # Get the file path
            file_name = Path(file_name or config["source_filename"])

            # Write source file
            source_path = tempdir / file_name
            source_path.write_text(code, encoding="utf-8")

            # Build compile command
            compile_command = config.get("compile_command", None)
            if compile_command:
                compile_command = compile_command.format(
                    file_name=file_name.stem,
                    file_extension=file_name.suffix,
                    memory=config["memory"]
                )

            run_command = config["run_command"].format(
                file_name=file_name.stem,
                file_extension=file_name.suffix,
                memory=config["memory"]
            )

            # Docker command
            cmd = runner_command_generator(
                name=f"sb_{dir_id}",
                cpus=config['cpus'],
                memory=config['memory'],
                pids_limit=config['pids_limit'],
                ulimit_nofile=config['ulimit_nofile'],
                read_only=config["read_only"],
                network=config['network'],
                tempdir=tempdir,
                user=config["user"],
                docker_image=config["docker_image"],
                compile_command=compile_command,
                run_command=run_command
            )

            # Execute the docker command
            start_time = time.time()
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            output, output_err = [], []

            await asyncio.wait_for(
                asyncio.gather(
                    read_stream(proc.stdout, output),
                    read_stream(proc.stderr, output_err),
                    update_periodically(message, proc, output, RUNNER_CONFIG["console_update"]),
                ),
                timeout=timeout
            )

            await proc.wait()

            end_time = time.time()

        except asyncio.TimeoutError:
            raise TimeoutError(timeout)

        finally:
            if proc and proc.returncode is None:
                proc.terminate()
                await proc.wait()

            if tempdir and tempdir.exists():
                shutil.rmtree(tempdir, ignore_errors=True)

        if proc.returncode != 0:
            raise RuntimeError("\n".join(output_err))

        execution_time = end_time - start_time

        return "\n".join(output), execution_time


# Function to add the Runner cog to the bot
async def setup(bot: Bot):
    await bot.add_cog(Runner(bot))
