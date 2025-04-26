import importlib
from pathlib import Path

from utils.files import list_files, path_to_module


def load_runners() -> None:
    for file in list_files(Path("./runner/runners"), ".py"):
        if file.name == "__init__.py" or file.name == "runner.py":
            continue

        importlib.import_module(path_to_module(file))
