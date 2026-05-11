import logging
from typing import Any, Literal

from ..exceptions import DatasetNotFoundError
from .file_loader import FileLoader

DatasetKind = Literal["light", "full"]

_LIGHT = ("pymojis.infrastructure.data", "emoji_data.json")
_FULL = ("pymojis_fulldata.data", "full_emoji_data.json")


class EmojiDataLoader:
    def __init__(self, file_loader: FileLoader) -> None:
        self.file_loader = file_loader
        self.logger = logging.getLogger(__name__)

    def load_from_path(self, path: str) -> dict[str, Any]:
        return self.file_loader.load_json_file(path)

    def load(self, kind: DatasetKind) -> dict[str, Any]:
        module, filename = _FULL if kind == "full" else _LIGHT
        try:
            data = self.file_loader.load_json_from_package(module, filename)
        except ModuleNotFoundError as exc:
            if kind == "full":
                raise DatasetNotFoundError(
                    "pymojis-fulldata is not installed. "
                    "Install it with: pip install 'pymojis[full]'"
                ) from exc
            raise
        self.logger.info("Loaded %s emoji dataset", kind)
        return data
