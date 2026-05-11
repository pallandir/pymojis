import json
import logging
from importlib.resources import files
from pathlib import Path
from typing import Any, cast


class FileLoader:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def load_json_file(self, file_path: str) -> dict[str, Any]:
        path = Path(file_path).resolve(strict=True)
        if path.is_dir():
            raise IsADirectoryError(f"Expected a file, got a directory: {path}")
        with path.open("r", encoding="utf-8") as f:
            self.logger.info("Loaded JSON from: %s", path)
            return cast(dict[str, Any], json.load(f))

    def load_json_from_package(self, module: str, filename: str) -> dict[str, Any]:
        resource = files(module).joinpath(filename)
        with resource.open("r", encoding="utf-8") as f:
            self.logger.info("Loaded JSON resource: %s/%s", module, filename)
            return cast(dict[str, Any], json.load(f))
