import json
from pathlib import Path
from typing import List, Dict, Any


def list_cogs(directory: Path, recursive: bool = False) -> List[Path]:
    if recursive:
        return list(directory.rglob("*_cog.py"))

    return [
        file for file
        in directory.iterdir()
        if file.is_file
        and file.name.endswith("_cog.py")
    ]


def path_to_module(file_path: Path) -> str:
    return ".".join(file_path.with_suffix("").parts)


def load_config(path: Path) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)
