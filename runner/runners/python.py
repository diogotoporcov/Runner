import asyncio
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Union

from cogs.code_runner import register_runner_func


@register_runner_func("python", "py")
async def _run_python_docker(code: str, timeout: float = 10) -> Union[str, Exception]:
    tempdir = None

    try:
        # Set up temporary directory structure for sandbox
        base_temp = Path(tempfile.gettempdir()) / "RunnerSandbox"
        base_temp.mkdir(parents=True, exist_ok=True)

        dir_id = uuid.uuid4().hex
        tempdir = base_temp / dir_id
        tempdir.mkdir(parents=True)

        # Set up script file
        script_path = tempdir / "script.py"
        script_path.write_text(code, encoding="utf-8")

        container_name = f"sandbox_{dir_id[:8]}"

        # Docker command setup for isolated environment
        cmd = [
            "docker", "run", "--rm",
            "--name", container_name,
            "--network", "none",  # No network access
            "--cpus=0.5",  # Limit CPU usage
            "--memory=256m",  # Limit memory usage
            "--pids-limit", "50",  # Limit processes
            "--ulimit", "nofile=1024:1024",  # Limit file descriptors
            "--read-only",  # Make filesystem read-only
            "-v", f"{tempdir}:/sandbox:rw",  # Temporary volume
            "-w", "/sandbox",  # Set working directory
            "-u", "1000:1000",  # Run as non-root user (UID 1000, GID 1000)
            "python:3.11",  # Use Python 3.11 image
            "python", "script.py"
        ]

        # Execute the docker command
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Add timeout handling for the process
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

        if proc.returncode != 0:
            raise RuntimeError(stderr.decode().strip())

        return stdout.decode().strip()

    except asyncio.TimeoutError:
        return f"Execution timed out after {timeout} seconds."

    except Exception as e:
        return f"{type(e).__name__}: {str(e)}"

    finally:
        # Clean up the temporary directory after execution
        if tempdir and tempdir.exists():
            shutil.rmtree(tempdir, ignore_errors=True)
