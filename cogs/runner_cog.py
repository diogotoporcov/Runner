import asyncio
import shutil
import tempfile
import uuid
from collections import ChainMap
from pathlib import Path
from typing import Optional

import discord
from discord.ext.commands import Bot, Cog

from client.client import CONFIG
from utils.code_helper import extract_code


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

        file_name, lang, code = await extract_code(message, RUNNER_CONFIG)

        if not code:
            return

        if not lang:
            await message.reply(f"❌ Language not supported!")
            return

        reply = await message.reply("⚙️ Running...")
        output = await run_code(lang, code, file_name)
        await reply.edit(content=f"📤 Output:\n```\n{output}```")


# Function to run the code within Docker sandbox
async def run_code(
        language: str,
        code: str,
        file_name: Optional[str] = None,
        timeout: float = 120
) -> str:
    tempdir = None

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
        file_path = Path(file_name or config["source_filename"])

        # Write source file
        source_path = tempdir / file_path
        source_path.write_text(code, encoding="utf-8")

        # Build compile command
        compile_command = config.get("compile_command", None)
        if compile_command:
            compile_command = compile_command.format(file_name=file_path.stem, file_extension=file_path.suffix)

        run_command = config["run_command"].format(file_name=file_path.stem, file_extension=file_path.suffix)

        # Docker command setup with parameters
        cmd = [
            "docker", "run", "--rm",  # Run a Docker container and remove it after execution
            "--name", dir_id,  # Assign a name to the container
            f"--cpus={config['cpus']}",  # Set the number of CPUs the container can use
            f"--memory={config['memory']}",  # Set the amount of memory the container can use
            f"--pids-limit={config['pids_limit']}",  # Set a limit on the number of processes in the container
            f"--ulimit=nofile={config['ulimit_nofile']}",  # Set the ulimit for the number of open files
            "--read-only" if config["read_only"] else "",
            # Set the container filesystem to read-only if the config specifies
            f"--network={config['network']}",  # Set the network mode for the container
            "-v", f"{tempdir}:/sandbox:rw",
            # Mount a volume with read-write access from tempdir to /sandbox in the container
            "-w", "/sandbox",  # Set the working directory inside the container to /sandbox
            "-u", config["user"],  # Set the user to run the container as
            config["docker_image"],  # Specify the Docker image to run
            "sh", "-c", f"{compile_command} && {run_command}" if compile_command else run_command
        ]

        # Execute the docker command
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

        if proc.returncode != 0:
            raise RuntimeError(stderr.decode().strip())

        return stdout.decode().strip()

    except asyncio.TimeoutError:
        return f"Execution timed out after {timeout} seconds."

    except RuntimeError as e:
        return str(e)

    except Exception as e:
        print(f"{type(e).__name__}: {str(e)}")

    finally:
        if tempdir and tempdir.exists():
            shutil.rmtree(tempdir, ignore_errors=True)


# Function to add the Runner cog to the bot
async def setup(bot: Bot):
    await bot.add_cog(Runner(bot))
