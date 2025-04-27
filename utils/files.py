import json
from pathlib import Path
from typing import List, Dict, Any


def list_files(directory: Path, *extensions: str) -> List[Path]:
    if not directory.is_dir():
        raise ValueError(f"{directory} is not a valid directory.")

    if not extensions:
        return [file for file in directory.rglob("*") if file.is_file()]

    return [file for file in directory.rglob("*") if file.suffix in extensions]


def path_to_module(file_path: Path) -> str:
    return ".".join(file_path.with_suffix("").parts)


def load_config(path: Path) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)
