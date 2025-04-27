import re
from typing import Optional, Any, Dict

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

    return file_name, file_extension, code
