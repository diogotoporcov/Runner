def format_to_discord_message(
        content: str,
        prefix: str = "",
        suffix: str = ""
) -> str:
    max_length = 2000
    prefix_length = len(prefix)
    suffix_length = len(suffix)

    content_length = max_length - prefix_length - suffix_length

    return f'{prefix}{content[-content_length:]}{suffix}'
