import json
import logging
from pathlib import Path
from typing import Any

from ..exceptions import FileLoadingError, InvalidPathError


class FileLoader:
    def __init__(
        self,
        allowed_base_path: str | None = None,
    ):
        self.allowed_base_path = Path(allowed_base_path or Path.cwd()).resolve()
        self.logger = logging.getLogger(__name__)

    def validate_path(self, file_path: str) -> Path:
        try:
            path = Path(file_path).resolve()

            # Prevent directory traversal
            if not str(path).startswith(str(self.allowed_base_path)):
                raise InvalidPathError(
                    f"Path '{file_path}' is outside allowed directory"
                )

            # Ensure it's not a directory
            if path.exists() and path.is_dir():
                raise InvalidPathError(f"Path '{file_path}' is a directory")

            return path

        except (OSError, ValueError) as file_error:
            raise InvalidPathError(
                f"Invalid file path '{file_path}': {file_error}"
            ) from file_error

    def load_json_file(self, file_path: str) -> dict[str, Any]:
        validated_path = self.validate_path(file_path)

        try:
            with validated_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                self.logger.info(f"Loaded JSON from: {validated_path}")
                return data

        except FileNotFoundError as file_error:
            raise FileLoadingError(f"File not found: {validated_path}") from file_error
        except json.JSONDecodeError as invalid_json:
            raise FileLoadingError(
                f"Invalid JSON in {validated_path}: {invalid_json}"
            ) from invalid_json
        except Exception as file_error:
            raise FileLoadingError(
                f"Failed to load {validated_path}: {file_error}"
            ) from file_error

    def load_json_from_package(self, module: str, filename: str) -> dict[str, Any]:
        try:
            from importlib.resources import files

            resource_path = files(module).joinpath(filename)
            with resource_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                self.logger.info(f"Loaded JSON resource: {module}/{filename}")
                return data

        except (ModuleNotFoundError, FileNotFoundError) as file_error:
            raise FileLoadingError(
                f"Resource not found {module}/{filename}: {file_error}"
            ) from file_error
        except json.JSONDecodeError as invalid_json:
            raise FileLoadingError(
                f"Invalid JSON in resource {module}/{filename}: {invalid_json}"
            ) from invalid_json
        except Exception as file_error:
            raise FileLoadingError(
                f"Failed to load resource {module}/{filename}: {file_error}"
            ) from file_error
