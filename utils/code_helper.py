import re
from typing import Optional, Any, Dict, List

import discord


async def extract_code(
        message: discord.Message,
        runner_config: Dict[str, Any]
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    file_name = None
    file_extension = None
    code = None

    attachment = message.attachments[0] if message.attachments else None
    if attachment:
        file_name = attachment.filename
        file_extension = file_name.split('.')[-1]
        code = await attachment.read()
        code = code.decode('utf-8', errors='ignore')

    else:
        pattern = r"```(\w+)\n([\s\S]+?)```"
        match = re.search(pattern, message.content)
        if match:
            file_extension = match.group(1).casefold()
            code = match.group(2)

    if file_extension not in runner_config["overrides"]:
        file_extension = runner_config["aliases"].get(file_extension)

    return code, file_name, file_extension


def runner_command_generator(**kwarg) -> List[str]:
    command = [
        "docker", "run", "--rm",  # Run a Docker container and remove it after execution
        "--name", kwarg["name"],  # Assign a name to the container
        f"--cpus={kwarg['cpus']}",  # Set the number of CPUs the container can use
        f"--memory={kwarg['memory']}",  # Set the amount of memory the container can use
        f"--pids-limit={kwarg['pids_limit']}",  # Set a limit on the number of processes in the container
        f"--ulimit=nofile={kwarg['ulimit_nofile']}",  # Set the ulimit for the number of open files
        f"--network={kwarg['network']}",  # Set the network mode for the container
        "-v", f"{kwarg['tempdir']}:/sandbox:rw",  # Mount a volume with read-write access from tempdir to /sandbox in the container
        "-w", "/sandbox",  # Set the working directory inside the container to /sandbox
        "-u", kwarg["user"],  # Set the user to run the container as
        kwarg["docker_image"],  # Specify the Docker image to run
        "sh", "-c",  # Execute the following command string using the shell
        f"{kwarg['compile_command']} && {kwarg['run_command']}"
        if kwarg["compile_command"]
        else kwarg["run_command"]  # Run both compile and execution commands if compile_command exists; otherwise, run only run_command
    ]

    if kwarg.get("read_only"):
        command.insert(8, "--read-only")  # Set the container filesystem to read-only if the config specifies

    return command


